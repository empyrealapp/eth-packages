import asyncio
import json
import logging
import re
import time
from copy import deepcopy
from functools import cached_property
from inspect import isclass
from types import GenericAlias
from typing import (
    Any,
    AsyncIterator,
    Generic,
    Iterator,
    Literal,
    Optional,
    TypeVar,
    get_args,
    get_origin,
)

from eth_abi import decode
from eth_abi.exceptions import InsufficientDataBytes
from eth_typing import ChecksumAddress, HexAddress, HexStr
from pydantic import BaseModel, PrivateAttr, computed_field
from pydantic.networks import AnyWebsocketUrl
from pydantic_core import Url
from websockets.exceptions import ConnectionClosedError
from websockets.legacy.client import WebSocketClientProtocol, connect
from websockets.sync.client import ClientConnection
from websockets.sync.client import connect as sync_connect

from ._request import Request
from ._transport import _force_get_default_network, get_current_network
from .block import Block
from .exceptions import LogDecodeError, LogResponseExceededError, RateLimitingError
from .models import EventData, Log
from .types import (
    BLOCK_STRINGS,
    BlockReference,
    EvmDataDict,
    Indexed,
    JsonResponseWssResponse,
    LogsArgs,
    LogsParams,
    Name,
    Network,
    RPCResponseModel,
    Struct,
    SubscriptionResponse,
)
from .utils import is_annotation, to_topic

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)
IGNORE = Literal[""]
IGNORE_VAL: IGNORE = ""


class UnindexedField(BaseModel):
    alias: str
    name: str
    string_type: str
    type: Any


def map_type(name):
    return {
        ChecksumAddress: "address",
        HexAddress: "address",
        str: "string",
        int: "uint256",
    }.get(name, name.__name__)


def map_indexed(is_indexed):
    if is_indexed:
        return " indexed "
    return ""


def load_type(type, value):
    if isclass(type) and issubclass(type, Struct):
        return type.from_tuple(value)
    if isinstance(type, GenericAlias):
        if get_origin(type) == list:
            return [load_type(get_args(type)[0], item) for item in value]
        elif get_origin(type) == tuple:
            return tuple(
                load_type(get_args(type)[i], item) for i, item in enumerate(value)
            )
    return type(value)


def convert(type, with_name: bool = False, with_indexed: bool = False):  # noqa: C901
    name = ""
    indexed = False
    if is_annotation(type):
        type, *annotations = get_args(type)
        for annotation in annotations:
            if annotation == Indexed:
                if with_indexed:
                    indexed = True
            elif isinstance(annotation, Name):
                if with_name:
                    name = annotation.value
    if isclass(type) and issubclass(type, Struct):
        return type.to_tuple_type()
    if isinstance(type, GenericAlias):
        if get_origin(type) == list:
            list_type = get_args(type)[0]
            converted_list_type = convert(list_type)
            if isinstance(converted_list_type, list):
                converted_list_type = f"({','.join(converted_list_type)})"
            return f"{converted_list_type}[] {name}".strip()
        else:
            tuple_args = ",".join([convert(t) for t in get_args(type)])
            return f"({tuple_args})"
    return f"{map_type(type)}{map_indexed(indexed)}{name}".strip()


class Event(Request, Generic[T]):
    """
    Generic event class for processing and subscribing to blockchain events.

    Event[T] provides a type-safe way to work with smart contract events,
    offering both historical data retrieval and real-time event streaming.

    Key features:
    - **Type Safety**: Full typing support for event data structures
    - **Flexible Filtering**: Filter by addresses, indexed parameters, and block ranges
    - **Real-time Streaming**: Subscribe to live events via WebSocket
    - **Historical Analysis**: Backfill events over large block ranges with automatic chunking
    - **Automatic Decoding**: Converts raw log data to typed Python objects

    Example:
        ```python
        class TransferEventType(BaseModel):
            sender: Annotated[HexAddress, Indexed]
            recipient: Annotated[HexAddress, Indexed]
            amount: primitives.uint256

        transfer_event = Event[TransferEventType](name="Transfer")

        async for event in transfer_event.set_filter(
            addresses=[token_address]
        ).subscribe():
            print(f"Transfer: {event.event.amount}")

        async for event in transfer_event.backfill(
            start_block=18000000,
            end_block=18001000
        ):
            process_transfer(event.event)
        ```

    Attributes:
        name: Event name as defined in the contract ABI
        anonymous: Whether this is an anonymous event (no topic0)
        topic1_filter: Filter for first indexed parameter
        topic2_filter: Filter for second indexed parameter
        topic3_filter: Filter for third indexed parameter
        addresses_filter: List of contract addresses to monitor
    """

    name: str
    anonymous: bool = False

    topic1_filter: Optional[HexStr | list[HexStr]] | IGNORE = IGNORE_VAL
    topic2_filter: Optional[HexStr | list[HexStr]] | IGNORE = IGNORE_VAL
    topic3_filter: Optional[HexStr | list[HexStr]] | IGNORE = IGNORE_VAL
    addresses_filter: list[HexAddress] = []

    _output_type: BaseModel = PrivateAttr()

    def model_post_init(self, __context) -> None:
        EventType, *_ = self.__pydantic_generic_metadata__["args"]
        self._output_type = EventType
        return super().model_post_init(__context)

    @staticmethod
    def _matches(topic: HexStr, topic_filter: HexStr | list[HexStr] | None) -> bool:
        if isinstance(topic_filter, list):
            if None in topic_filter:
                return True
            return topic in topic_filter
        return topic == topic_filter

    def match_topics(self, log: Log) -> bool:
        # TODO: addresses_filter
        if len(log.topics) == 0:
            return False
        if log.topics[0] != self.get_topic0:
            return False
        if self.topic1_filter != IGNORE_VAL and len(log.topics) >= 2:
            if not self._matches(log.topics[1], self.topic1_filter):
                return False
        if self.topic2_filter != IGNORE_VAL and len(log.topics) >= 3:
            if not self._matches(log.topics[2], self.topic2_filter):
                return False
        if self.topic3_filter != IGNORE_VAL and len(log.topics) >= 4:
            if not self._matches(log.topics[3], self.topic3_filter):
                return False
        return True

    def match_address(self, log: Log) -> bool:
        if self.addresses_filter:
            return log.address in self.addresses_filter
        return True

    def match(self, log: Log) -> bool:
        return self.match_address(log) and self.match_topics(log)

    def add_address(self, address: HexAddress | list[HexAddress]):
        if isinstance(address, list):
            for addr in address:
                self.add_address(addr)
        else:
            if address not in self.addresses_filter:
                self.addresses_filter.append(address)

    def remove_address(self, address: HexAddress):
        self.addresses_filter = [
            _address for _address in self.addresses_filter if _address != address
        ]

    @staticmethod
    def process_value(type_name, v: str):
        # strip prefix if necessary
        if "0x" in v:
            v = v[2:]

        if type_name == "address":
            # last 20 bytes of value
            return "0x{}".format(v[-40:])
        if "bytes" in type_name:
            return bytes.fromhex(v)
        if "uint" in type_name:
            return int.from_bytes(bytes.fromhex(v), "big", signed=False)
        elif "int" in type_name:
            return int.from_bytes(bytes.fromhex(v), "big", signed=True)
        if type_name == "bool":
            return v[-1] == "1"

    def from_dict(self, fields: dict[str, Any]):
        EventType, *_ = self.__pydantic_generic_metadata__["args"]
        return EventType(**fields)

    def process_log(self, log: Log) -> EventData[T]:
        return EventData(
            name=self.name,
            log=log,
            event=self.process(log.topics, log.data),
            network=self._network or get_current_network(),
        )

    def process(self, topics: list[HexStr], data: HexStr) -> T:
        """
        Decode raw log data into a typed event object.

        This method handles the complex process of converting raw blockchain
        log data (topics and data) into a properly typed Python object.

        The decoding process:
        1. **Indexed Parameters**: Extracted from log topics (limited to 3 indexed params)
        2. **Non-indexed Parameters**: Decoded from the log data using ABI decoding
        3. **Type Conversion**: Raw values converted to appropriate Python types
        4. **Object Construction**: Final event object created with all parameters

        Args:
            topics: List of log topics (topic0 is event signature, topic1-3 are indexed params)
            data: Hex-encoded log data containing non-indexed parameters

        Returns:
            Typed event object with all decoded parameters

        Raises:
            LogDecodeError: If topics/data don't match expected event structure

        Example:
            ```python
            topics = [
                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",  # Transfer signature
                "0x000000000000000000000000a0b86a33e6441b8e776f1c0b8e8e8e8e8e8e8e8e",  # from address
                "0x000000000000000000000000b1c86a33e6441b8e776f1c0b8e8e8e8e8e8e8e8e"   # to address
            ]
            data = "0x0000000000000000000000000000000000000000000000000de0b6b3a7640000"  # amount

            transfer = transfer_event.process(topics, data)
            print(f"Transfer: {transfer.amount} from {transfer.sender} to {transfer.recipient}")
            ```
        """
        EventType, *_ = self.__pydantic_generic_metadata__["args"]
        indexed = self.get_indexed()
        try:
            indexed_dict = {
                name: self.process_value(type_, topics[i + 1])
                for i, (name, type_) in enumerate(indexed)
            }
        except IndexError:
            raise LogDecodeError("Mismatched Indexed values")

        unindexed = self.get_unindexed()
        try:
            type_strings = [field.string_type for field in unindexed]
            types = [field.type for field in unindexed]
            unindexed_values = decode(
                type_strings, bytes.fromhex(data.removeprefix("0x"))
            )

            parsed_values = []
            for type_, value in zip(types, unindexed_values):
                parsed_values.append(load_type(type_, value))
        except InsufficientDataBytes:
            raise LogDecodeError("Mismatched Unindexed values")

        return EventType(
            **indexed_dict
            | {field.alias: val for field, val in zip(unindexed, parsed_values)}
        )

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def get_topic0(self) -> HexStr:
        inputs, *_ = self.__pydantic_generic_metadata__["args"]
        input_types = inputs.model_fields
        converted_inputs = ",".join(
            [convert(field.annotation) for name, field in input_types.items()]
        )
        event_signature = f"{self.name}({converted_inputs})"
        return HexStr("0x" + to_topic(event_signature).hex())

    def get_indexed(self):
        inputs, *_ = self.__pydantic_generic_metadata__["args"]
        input_types = inputs.model_fields
        results = []
        for name, field in input_types.items():
            indexed = False
            _type = field.annotation
            annotations = field.metadata
            for annotation in annotations:
                if annotation == Indexed:
                    indexed = True
                elif isinstance(annotation, Name):
                    name = annotation.value
            if indexed:
                results.append((name, map_type(_type)))
        return results

    def get_unindexed(self) -> list[UnindexedField]:
        inputs, *_ = self.__pydantic_generic_metadata__["args"]
        input_types = inputs.model_fields
        results = []
        for name, field in input_types.items():
            alias = name
            indexed = False
            _type = field.annotation
            annotations = field.metadata
            for annotation in annotations:
                if annotation == Indexed:
                    indexed = True
                elif isinstance(annotation, Name):
                    name = annotation.value
            if not indexed:
                field = UnindexedField(
                    alias=alias,
                    name=name,
                    string_type=convert(_type),
                    type=_type,
                )
                results.append(field)
        return results

    def _get_logs(
        self,
        start_block: BlockReference | int,
        end_block: BlockReference | int,
        addresses: list[HexAddress] = [],
        topic1: Optional[HexStr | list[HexStr] | None] | IGNORE = IGNORE_VAL,
        topic2: Optional[HexStr | list[HexStr] | None] | IGNORE = IGNORE_VAL,
        topic3: Optional[HexStr | list[HexStr] | None] | IGNORE = IGNORE_VAL,
    ) -> RPCResponseModel[LogsArgs, list[Log]]:
        topics: list[HexStr | None | list[HexStr]] = []
        if topic1 != IGNORE_VAL:
            topics.append(topic1)
            if topic2 != IGNORE_VAL:
                topics.append(topic2)
                if topic3 != IGNORE_VAL:
                    topics.append(topic3)
        return RPCResponseModel(
            self.rpc().get_logs,
            LogsArgs(
                params=LogsParams(
                    address=addresses,
                    from_block=start_block,
                    to_block=end_block,
                    topics=[self.get_topic0, *topics],
                )
            ),
        )

    def set_filter(
        self,
        addresses: list[HexAddress] = [],
        topic1: Optional[HexStr | list[HexStr]] | IGNORE = IGNORE_VAL,
        topic2: Optional[HexStr | list[HexStr]] | IGNORE = IGNORE_VAL,
        topic3: Optional[HexStr | list[HexStr]] | IGNORE = IGNORE_VAL,
    ):
        model = deepcopy(self)
        model.addresses_filter = addresses
        if topic1 != IGNORE_VAL:
            model.topic1_filter = topic1
        if topic2 != IGNORE_VAL:
            model.topic1_filter = model.topic1_filter or None
            model.topic2_filter = topic2
        if topic3 != IGNORE_VAL:
            model.topic1_filter = model.topic1_filter or None
            model.topic2_filter = model.topic2_filter or None
            model.topic3_filter = topic3
        return model

    async def get_logs(
        self,
        start_block: BlockReference | int,
        end_block: BlockReference | int,
    ) -> AsyncIterator[EventData[T]]:
        cur_end = end_block
        try:
            response = await self._get_logs(
                start_block,
                cur_end,
                self.addresses_filter,
                topic1=self.topic1_filter,
                topic2=self.topic2_filter,
                topic3=self.topic3_filter,
            )
        except ValueError as err:
            message = err.args[0]
            if isinstance(message, bytes):
                try:
                    message = message.decode("utf-8")
                except UnicodeDecodeError:
                    message = str(message)
            else:
                message = str(message)
            if "Log response size exceeded." in message:
                boundaries = re.findall("0x[0-9a-f]+", message)
                raise LogResponseExceededError(
                    err.args[0], int(boundaries[0], 16), int(boundaries[1], 16)
                )
            elif (
                "Your app has exceeded its compute units per second capacity" in message
            ):
                raise RateLimitingError(message)
            raise err

        for result in response:
            # TODO: this is just a placeholder
            if len(result.topics) != (len(self.get_indexed()) + 1):
                # this happens when an event has the same topic0, but different indexed events so it doesn't match up to the expected ABI
                continue

            event_data = EventData[T](
                name=self.name,
                log=result,
                event=self.process(
                    result.topics,
                    result.data,
                ),
                network=self._network or get_current_network(),
            )
            yield event_data

    async def backfill(
        self,
        start_block: int | None = None,
        end_block: int | None = None,
        step_size: Optional[int] = None,
        confirmations: int = 2,
    ) -> AsyncIterator[EventData[T]]:
        """
        Retrieve historical events over a block range with automatic chunking.

        This method handles large block ranges by automatically splitting them
        into smaller chunks when RPC providers return "response too large" errors.
        It provides a robust way to analyze historical blockchain data.

        Key features:
        - **Automatic Chunking**: Splits large ranges when RPC limits are hit
        - **Rate Limit Handling**: Automatically retries on rate limit errors
        - **Confirmation Safety**: Excludes recent blocks to avoid reorgs
        - **Memory Efficient**: Yields events as they're processed (streaming)

        Args:
            start_block: Starting block number (default: 1)
            end_block: Ending block number (default: latest - confirmations)
            step_size: Fixed chunk size for processing (optional)
            confirmations: Number of blocks to exclude from tip to avoid reorgs

        Yields:
            EventData[T]: Decoded event data with log information and network context

        Example:
            ```python
            async for event in transfer_event.set_filter(
                addresses=[usdc_address]
            ).backfill(
                start_block=18000000,
                end_block=18001000
            ):
                if event.event.amount > 1000000 * 10**6:  # > $1M
                    print(f"Large transfer: ${event.event.amount / 10**6:,.2f}")

            async for event in transfer_event.backfill(
                start_block=17000000,
                end_block=18000000,
                step_size=10000  # Process 10k blocks at a time
            ):
                await store_event_in_database(event)
            ```

        Note:
            This method automatically handles:
            - RPC response size limits by reducing chunk size
            - Rate limiting with exponential backoff
            - Network errors with retry logic
            - Block reorganizations by using confirmations
        """
        start_block = start_block or 1
        current_number = await Block[self._network].get_number()  # type: ignore[name-defined]
        end_block = end_block or (current_number - confirmations)

        if start_block == "earliest":
            cur_start = 0
        else:
            cur_start = start_block

        if step_size:
            cur_end = cur_start + step_size
        else:
            cur_end = end_block
        while cur_start <= end_block:
            try:
                async for log in self.get_logs(
                    start_block=cur_start,
                    end_block=min(cur_end, end_block),
                ):
                    yield log
            except LogResponseExceededError as err:
                cur_end = err.recommended_end
                continue
            except RateLimitingError:
                await asyncio.sleep(3)
                continue
            cur_start = cur_end + 1
            if step_size:
                cur_end += step_size
            else:
                cur_end = end_block

    @property
    def subscribe(self) -> "AsyncSubscribeCallable[T]":
        """
        This returns a callable for the async subscriber, allowing you to select the network
        for the subscription, ie.

        ```python
        my_event = Event[EventType](name="MyEvent")
        async for event in my_event.subscribe[Ethereum]():
            ...
        ```

        If no network is provided, it will use the default network.
        """
        # TODO: sometimes the topics match, but the indexed fields are different
        network = self._network or _force_get_default_network()
        return AsyncSubscribeCallable(
            network=network,
            event=self,
        )

    @property
    def sync(self) -> "SyncEventWrapper[T]":
        return SyncEventWrapper(
            network=self._network or _force_get_default_network(),
            event=self,
        )

    @staticmethod
    async def _convert_block_string(
        block_string: BLOCK_STRINGS,
    ) -> int:
        if block_string == "earliest":
            return 0
        return (await Block.load_by_number(block_string)).number

    @staticmethod
    async def _send_subscription_request(
        w3_connection: WebSocketClientProtocol,
        pending: bool,
        addresses: list[HexAddress],
        topics: list[HexStr | list[HexStr] | None],
    ):
        # this only handles a list of topic0s being subscribed together
        subscription_type = "newPendingTransactions" if pending else "logs"
        await w3_connection.send(
            json.dumps(
                {
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": [
                        subscription_type,
                        {
                            "address": addresses,
                            "topics": topics,
                        },
                    ],
                }
            )
        )


class SyncEventWrapper(BaseModel, Generic[T]):
    network: type[Network]
    event: Event[T]

    def __getitem__(self, network: type[Network]):
        self.network = network
        return self

    def subscribe(  # noqa: C901
        self,
    ) -> Iterator[EventData[T]]:
        # TODO: sometimes the topics match, but the indexed fields are different

        if not (wss_uri := self.network.wss):
            raise ValueError("No wss set for network")

        w3_connection = sync_connect(
            (
                wss_uri.unicode_string()
                if isinstance(wss_uri, AnyWebsocketUrl)
                else wss_uri
            ),
            max_queue=10000,
        )
        try:
            topics: list[HexStr | list[HexStr] | None] = []
            if self.event.topic1_filter != IGNORE_VAL:
                topics.append(self.event.topic1_filter)
                if self.event.topic2_filter != IGNORE_VAL:
                    topics.append(self.event.topic2_filter)
                    if self.event.topic3_filter != IGNORE_VAL:
                        topics.append(self.event.topic3_filter)

            self._send_subscription_request(
                w3_connection,
                False,
                self.event.addresses_filter,
                [
                    self.event.get_topic0,
                    *topics,
                ],
            )
            subscription_response: SubscriptionResponse = json.loads(
                w3_connection.recv()
            )
            if not subscription_response.get("result"):
                raise ValueError(subscription_response)
        except Exception as e:
            raise e

        while True:
            try:
                message = w3_connection.recv(timeout=32.0)
                message_json: JsonResponseWssResponse = json.loads(message)
                if "params" not in message_json:
                    raise ValueError(message_json)

                result_dict: EvmDataDict = message_json["params"]["result"]
                result = Log.model_validate(result_dict)
                yield EventData(
                    name=self.event.name,
                    log=result,
                    event=self.event.process(
                        result.topics,
                        result.data,
                    ),
                    network=self.network,
                )
            except asyncio.exceptions.TimeoutError:
                pass
            except (TypeError, LogDecodeError):
                logger.warning("Mistmatched type: %s", result_dict)
            except (
                ConnectionClosedError,
                ConnectionResetError,
                OSError,  # No route to host
                asyncio.exceptions.IncompleteReadError,  # TODO: should this be handled differently?
            ) as err:
                logger.error("connection terminated unexpectedly: %s", err)
                time.sleep(1)
                # we're in an iterator, so make a new connection and continue listening
                break
            except Exception as err:
                logger.error("connection error: %s", err)
                time.sleep(1)
                # we're in an iterator, so make a new connection and continue listening
                break

    def get_logs(
        self,
        start_block: BlockReference | int,
        end_block: BlockReference | int,
    ) -> Iterator[EventData[T]]:
        cur_end = end_block
        try:
            response = self.event._get_logs(
                start_block,
                cur_end,
                self.event.addresses_filter,
                topic1=self.event.topic1_filter,
                topic2=self.event.topic2_filter,
                topic3=self.event.topic3_filter,
            ).sync
        except ValueError as err:
            message = err.args[0]
            if isinstance(message, bytes):
                try:
                    message = message.decode("utf-8")
                except UnicodeDecodeError:
                    message = str(message)
            else:
                message = str(message)
            if "Log response size exceeded." in message:
                boundaries = re.findall("0x[0-9a-f]+", message)
                raise LogResponseExceededError(
                    err.args[0], int(boundaries[0], 16), int(boundaries[1], 16)
                )
            elif (
                "Your app has exceeded its compute units per second capacity" in message
            ):
                raise RateLimitingError(message)
            raise err

        for result in response:
            # TODO: this is just a placeholder
            if len(result.topics) != (len(self.event.get_indexed()) + 1):
                # this happens when an event has the same topic0, but different indexed events so it doesn't match up to the expected ABI
                continue

            event_data = EventData[T](
                name=self.event.name,
                log=result,
                event=self.event.process(
                    result.topics,
                    result.data,
                ),
                network=self.network,
            )
            yield event_data

    def backfill(
        self,
        start_block: int | None = None,
        end_block: int | None = None,
        step_size: Optional[int] = None,
        confirmations: int = 2,
    ) -> Iterator[EventData[T]]:
        """
        This backfills events, handling LogResponseExceededError to provide all logs in a range too large for a single request
        """
        start_block = start_block or 1
        current_number = Block[self.network].get_number().sync  # type: ignore[name-defined]
        end_block = end_block or (current_number - confirmations)

        if start_block == "earliest":
            cur_start = 0
        else:
            cur_start = start_block

        if step_size:
            cur_end = cur_start + step_size
        else:
            cur_end = end_block
        while cur_start <= end_block:
            try:
                for log in self.get_logs(
                    start_block=cur_start,
                    end_block=min(cur_end, end_block),
                ):
                    yield log
            except LogResponseExceededError as err:
                cur_end = err.recommended_end
                continue
            except RateLimitingError:
                time.sleep(3)
                continue
            cur_start = cur_end + 1
            if step_size:
                cur_end += step_size
            else:
                cur_end = end_block

    @staticmethod
    def _send_subscription_request(
        w3_connection: ClientConnection,
        pending: bool,
        addresses: list[HexAddress],
        topics: list[HexStr | list[HexStr] | None],
    ):
        # this only handles a list of topic0s being subscribed together
        subscription_type = "newPendingTransactions" if pending else "logs"
        w3_connection.send(
            json.dumps(
                {
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": [
                        subscription_type,
                        {
                            "address": addresses,
                            "topics": topics,
                        },
                    ],
                }
            )
        )


class AsyncSubscribeCallable(BaseModel, Generic[T]):
    network: type[Network]
    event: Event[T]

    def __getitem__(self, network: type[Network]):
        self.network = network
        return self

    async def __call__(  # noqa: C901
        self,
    ) -> AsyncIterator[EventData[T]]:
        # TODO: sometimes the topics match, but the indexed fields are different

        if not (wss_uri := self.network.wss):
            raise ValueError("No wss set for network")

        async for w3_connection in connect(
            (
                wss_uri.unicode_string()
                if isinstance(wss_uri, AnyWebsocketUrl)
                else wss_uri
            ),
            ping_interval=60,
            ping_timeout=60,
            max_queue=10000,
            open_timeout=30,
        ):
            try:
                topics: list[HexStr | list[HexStr] | None] = []
                if self.event.topic1_filter != IGNORE_VAL:
                    topics.append(self.event.topic1_filter)
                    if self.event.topic2_filter != IGNORE_VAL:
                        topics.append(self.event.topic2_filter)
                        if self.event.topic3_filter != IGNORE_VAL:
                            topics.append(self.event.topic3_filter)

                await self.event._send_subscription_request(
                    w3_connection,
                    False,
                    self.event.addresses_filter,
                    [
                        self.event.get_topic0,
                        *topics,
                    ],
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
                    message = await asyncio.wait_for(w3_connection.recv(), timeout=32.0)
                    message_json: JsonResponseWssResponse = json.loads(message)
                    if "params" not in message_json:
                        raise ValueError(message_json)

                    result_dict: EvmDataDict = message_json["params"]["result"]
                    result = Log.model_validate(result_dict)
                    yield EventData(
                        name=self.event.name,
                        log=result,
                        event=self.event.process(
                            result.topics,
                            result.data,
                        ),
                        network=self.network,
                    )
                except asyncio.exceptions.TimeoutError:
                    pass
                except (TypeError, LogDecodeError):
                    logger.warning("Mistmatched type: %s", result_dict)
                except (
                    ConnectionClosedError,
                    ConnectionResetError,
                    OSError,  # No route to host
                    asyncio.exceptions.IncompleteReadError,  # TODO: should this be handled differently?
                ) as err:
                    logger.error("connection terminated unexpectedly: %s", err)
                    await asyncio.sleep(1)
                    # we're in an iterator, so make a new connection and continue listening
                    break
                except Exception as err:
                    logger.error("connection error: %s", err)
                    await asyncio.sleep(1)
                    # we're in an iterator, so make a new connection and continue listening
                    break
