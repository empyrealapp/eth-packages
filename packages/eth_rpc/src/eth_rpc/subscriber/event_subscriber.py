import asyncio
import json
import re
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from contextvars import ContextVar
from typing import Generic, Optional, TypeVar

from eth_rpc import Event, EventData, get_current_network
from eth_rpc.block import Block
from eth_rpc.log import Log
from eth_rpc.types import (
    BLOCK_STRINGS,
    EvmDataDict,
    JsonResponseWssResponse,
    LogsArgs,
    LogsParams,
    SubscriptionResponse,
)
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, ConfigDict, Field
from websockets.exceptions import ConnectionClosedError
from websockets.legacy.client import WebSocketClientProtocol, connect

from .._request import Request
from .._transport import _force_get_global_rpc
from ..constants import DEFAULT_CONTEXT, DEFAULT_EVENT

T = TypeVar("T", bound=BaseModel)
U = TypeVar("U", bound=BaseModel)


class Receiver(ABC, Generic[T]):
    @abstractmethod
    async def put(self, event: EventData[T]) -> None: ...


class EventSubscriber(Request, Generic[U]):
    receivers: dict[HexStr, list[Receiver[U]]] = Field(default_factory=dict)
    events: list[Event] = Field(default_factory=list)
    step_size: int | None = Field(default=None)

    _start_block: Optional[int | BLOCK_STRINGS] = None
    _end_block: Optional[int | BLOCK_STRINGS] = None
    _addresses: Optional[list[HexAddress]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def network(self):
        return self._network or get_current_network()

    def get_topics(self):
        """The nested list makes it so any match to topic0 will be selected"""
        return [[e.get_topic0 for e in self.events]]

    async def _get_logs(
        self,
        start_block: int,
        end_block: int,
        addresses: list[HexAddress] = [],
    ) -> AsyncIterator[EventData[U]]:
        topic_dict = {event.get_topic0: event for event in self.events}
        cur_end = start_block + self.step_size - 1 if self.step_size else end_block

        while True:
            try:
                response = await self.rpc().get_logs(
                    LogsArgs(
                        params=LogsParams(
                            address=addresses,
                            from_block=start_block,
                            to_block=cur_end,
                            topics=self.get_topics(),
                        )
                    )
                )
            except ValueError as err:
                # TODO: confirm this error is due to the cur_end being too far in the future
                message = err.args[0]

                if "Log response size exceeded." in message:
                    boundaries = re.findall("0x[0-9a-f]+", message)
                    if len(boundaries) != 2:
                        raise err
                    cur_end = int(boundaries[1], 16)
                else:
                    raise err
                continue

            for result in response:
                event = topic_dict[result.topics[0]]

                # TODO: this is just a placeholder
                if len(result.topics) != (len(event.get_indexed()) + 1):
                    # this happens when an event has the same topic0, but different indexed events so it doesn't match up to the expected ABI
                    # print("INDEX MISMATCH", result.transaction_hash, result.log_index)
                    continue

                event_data = EventData[U](
                    name=event.name,
                    log=result,
                    event=event.process(
                        result.topics,
                        result.data,
                    ),
                    network=self.network,
                )
                yield event_data

            start_block = cur_end + 1
            cur_end = start_block + self.step_size - 1 if self.step_size else end_block
            if start_block >= end_block:
                break

    async def get_logs(
        self,
        start_block: int | BLOCK_STRINGS,
        end_block: int | BLOCK_STRINGS,
        addresses: list[HexAddress] = [],
    ):
        _start_block: int = await Block.convert(start_block)
        _end_block: int = await Block.convert(end_block)
        async for event_data in self._get_logs(_start_block, _end_block, addresses):
            for receiver in self.receivers[event_data.tx.topics[0]]:
                await receiver.put(event_data)

    def add_receiver(self, receiver: Receiver, events: list[Event[U]]):
        for event in events:
            # add event to events list
            if event not in self.events:
                self.events.append(event)

            # add topic0 to receivers
            topic0 = event.get_topic0
            if topic0 not in self.receivers:
                self.receivers[topic0] = [receiver]
            else:
                if receiver not in self.receivers[topic0]:
                    self.receivers[topic0].append(receiver)

    async def _get_event(
        self,
        w3_connection: WebSocketClientProtocol,
        event_dict: dict[HexStr, "Event"],
    ) -> EventData[U] | None:
        message = await asyncio.wait_for(w3_connection.recv(), timeout=32.0)
        message_json: JsonResponseWssResponse = json.loads(message)
        if "params" not in message_json:
            raise ValueError(message_json)

        result_dict: EvmDataDict = message_json["params"]["result"]
        if result_dict["removed"]:
            return None
        result = Log(**result_dict, network=self.network)  # type: ignore
        event = event_dict[result.topics[0]]

        # TODO: this is just a placeholder
        if len(result.topics) != (len(event.get_indexed()) + 1):
            # print("INDEX MISMATCH", result.transaction_hash, result.log_index)
            return None

        return EventData[U](
            name=event.name,
            log=result,
            event=event.process(
                result.topics,
                result.data,
            ),
            network=self.network,
        )

    async def _listen(  # noqa: C901
        self,
        addresses: list[HexAddress] = [],
    ):
        # TODO: sometimes the topics match, but the indexed fields are different
        topic_dict = {event.get_topic0: event for event in self.events}

        rpc = _force_get_global_rpc()
        async for w3_connection in connect(
            rpc.wss,
            ping_interval=60,
            ping_timeout=60,
            max_queue=10000,
            open_timeout=30,
        ):
            try:
                await self._send_subscription_request(
                    w3_connection,
                    addresses,
                    [event.get_topic0 for event in self.events],
                )
                subscription_response: SubscriptionResponse = json.loads(
                    await w3_connection.recv()
                )
                if not subscription_response.get("result"):
                    raise ValueError(subscription_response)
            except Exception as e:
                raise e

            while True:
                try:
                    event_data = await self._get_event(w3_connection, topic_dict)
                    if event_data is None:
                        continue
                    yield event_data

                except asyncio.exceptions.TimeoutError:
                    pass
                except (
                    ConnectionClosedError,
                    ConnectionResetError,
                    OSError,  # No route to host
                    asyncio.exceptions.IncompleteReadError,  # TODO: should this be handled differently?
                ) as err:
                    print("Connection Error:", err)
                    await asyncio.sleep(3)
                    # we're in an iterator, so make a new connection and continue listening
                    break
                except Exception as e:
                    print("Unknown Error:", e)
                    await asyncio.sleep(3)
                    # we're in an iterator, so make a new connection and continue listening
                    break

    async def listen(
        self,
        addresses: list[HexAddress] = [],
        publish_events: asyncio.Event = DEFAULT_EVENT,
        start_context: ContextVar = DEFAULT_CONTEXT,
    ):
        """
        Listen for new blockchain events.  Publish Event is used to tell the listener to
        start publishing to receivers.  The default is for this variable to be set.
        The start_context is used to set a starting block number, so you can synchronize this
        with backfill.
        """
        queue: asyncio.Queue[EventData[U]] = asyncio.Queue()
        flush_queue: bool = True
        async for event_data in self._listen(addresses=addresses):
            if publish_events.is_set():
                if flush_queue:
                    while not queue.empty():
                        event_data = await queue.get()
                        if event_data.tx.block_number <= start_context.get():
                            continue
                        for receiver in self.receivers[event_data.tx.topics[0]]:
                            await receiver.put(event_data)
                    flush_queue = False
                for receiver in self.receivers[event_data.tx.topics[0]]:
                    await receiver.put(event_data)
            else:
                await queue.put(event_data)

    async def backfill_and_listen(
        self,
        start_block: int,
        addresses: list[HexAddress] = [],
    ):
        should_publish_events = asyncio.Event()
        latest_block: ContextVar[int] = ContextVar("latest_block")
        task = asyncio.create_task(
            self.listen(
                addresses=addresses,
                publish_events=should_publish_events,
                start_context=latest_block,
            )
        )
        latest = await Block.latest()
        latest_block.set(latest.number)
        await self.get_logs(start_block, latest.number, addresses)
        should_publish_events.set()
        return await task

    @staticmethod
    async def _send_subscription_request(
        w3_connection: WebSocketClientProtocol,
        addresses: list[HexAddress],
        topics: list[HexStr],
    ) -> None:
        # this only handles a list of topic0s being subscribed together
        await w3_connection.send(
            json.dumps(
                {
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": [
                        "logs",
                        {
                            "address": addresses,
                            "topics": [[t for t in topics]],
                        },
                    ],
                }
            )
        )

    def __call__(
        self,
        start_block: int | BLOCK_STRINGS = 0,
        end_block: int | BLOCK_STRINGS = "latest",
        addresses: list[HexAddress] = [],
    ) -> AsyncIterator[EventData[U]]:
        """This is used to set these values so you can use the iterator"""

        self._start_block = start_block
        self._end_block = end_block
        self._addresses = addresses
        return self.__aiter__()

    async def __aiter__(self) -> AsyncIterator[EventData[U]]:
        if not (
            self._start_block is not None
            and self._end_block is not None
            and self._addresses is not None
        ):
            raise ValueError("Must set blocks first.")
        start_block = await Block.convert(self._start_block)
        end_block = await Block.convert(self._end_block)
        async for event in self._get_logs(start_block, end_block, self._addresses):
            yield event
