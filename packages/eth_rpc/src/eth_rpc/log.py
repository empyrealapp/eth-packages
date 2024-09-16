import asyncio
import json
from collections.abc import AsyncIterator
from typing import TypeVar

from eth_rpc.models import Log as LogModel
from eth_rpc.types import HexInt, LogsArgs, LogsParams
from eth_typing import HexAddress, HexStr
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.legacy.client import connect

from ._request import Request
from .block import Block
from .constants import DEFAULT_EVENT
from .types import RPCResponseModel

T = TypeVar("T")


class Log(Request, LogModel):
    @classmethod
    def load_by_number(
        self,
        from_block: int | HexInt,
        to_block: int | HexInt | None = None,
        address: HexAddress | list[HexAddress] | None = None,
        topics: list[list[HexStr] | HexStr | None] | None = None,
    ) -> RPCResponseModel[LogsArgs, list["LogModel"]]:
        """
        Get all logs in a certain range
        """
        return RPCResponseModel(
            self.rpc().get_logs,
            LogsArgs(
                params=LogsParams(
                    address=address,
                    from_block=HexInt(from_block),
                    to_block=HexInt(to_block or from_block + 1),
                    topics=topics,
                )
            ),
        )

    @classmethod
    async def listen(
        cls,
        *,
        queue: asyncio.Queue["LogModel"],
        publish_logs: asyncio.Event = DEFAULT_EVENT,
    ):
        """
        Subscribe to logs
        """

        internal_queue: asyncio.Queue = asyncio.Queue()
        flush_queue: bool = True
        async for log in cls._listen():
            if publish_logs.is_set():
                if flush_queue:
                    while not internal_queue.empty():
                        staged_block = await internal_queue.get()
                        await queue.put(staged_block)
                    flush_queue = False
                await queue.put(log)
            else:
                await internal_queue.put(log)

    @classmethod
    async def _listen(cls):
        async for w3_connection in connect(
            cls.rpc().wss,
            ping_interval=60,
            ping_timeout=60,
            max_queue=10000,
        ):
            network = cls._network
            # TODO: this is incomplete
            params = ["logs", {}]

            await w3_connection.send(
                json.dumps({"id": 1, "method": "eth_subscribe", "params": params})
            )
            subscription_response = await w3_connection.recv()
            if not (subscription_id := json.loads(subscription_response).get("result")):
                raise ValueError(subscription_response)
            assert subscription_id, "subscription failed to connect"

            while True:
                try:
                    raw_message = await asyncio.wait_for(
                        w3_connection.recv(), timeout=60
                    )
                    message_json = json.loads(raw_message)
                    result = message_json["params"]["result"]

                    yield Log(**result, network=network)
                except asyncio.exceptions.TimeoutError:
                    pass
                except (
                    ConnectionClosedOK,
                    ConnectionClosedError,
                    ConnectionResetError,
                    asyncio.exceptions.IncompleteReadError,  # TODO: should this be handled differently?
                ) as err:
                    print("Connection Error:", err)
                    # TODO: track the last block consumed, when you restart, confirm there's no gap in continuity
                    # w3_connection is an iterator, so make a new connection and continue listening
                    break

    @classmethod
    async def subscribe_from(
        self,
        start_block: int | None = None,
        batch_size: int = 50,
    ) -> AsyncIterator[LogModel]:
        """
        Subscribe to logs, but backfilling starting at a specific block number and then listening
        """
        queue = asyncio.Queue[LogModel]()
        should_publish_logs = asyncio.Event()
        asyncio.create_task(
            self.listen(
                queue=queue,
                publish_logs=should_publish_logs,
            )
        )
        latest = await Block.get_number()
        if not start_block:
            start_block = latest
        assert start_block

        num = start_block
        while num <= latest:
            batch_end = min(num + batch_size, latest)
            for log in await self.load_by_number(num, batch_end):
                yield log
            num += batch_size

        should_publish_logs.set()
        while True:
            log = await queue.get()
            if log.block_number > latest:
                yield log
