import asyncio
import json
import zlib
from collections.abc import AsyncIterator
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Generic, Literal

from eth_rpc.models import Block as BlockModel
from eth_rpc.models import FeeHistory
from eth_rpc.types.args import (
    BlockNumberArg,
    FeeHistoryArgs,
    GetBlockByHashArgs,
    GetBlockByNumberArgs,
)
from eth_typing import HexStr
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.legacy.client import connect

from ._request import Request
from .constants import DEFAULT_EVENT
from .models import Transaction as TransactionModel
from .types import (
    BLOCK_STRINGS,
    BlockReference,
    HexInteger,
    Network,
    NetworkT,
    NoArgs,
    RPCResponseModel,
)

SUBSCRIPTION_TYPE = Literal["newHeads", "newPendingTransactions"]
DEFAULT_CONTEXT = ContextVar[int]("DEFAULT_CONTEXT")
DEFAULT_CONTEXT.set(0)


class Block(BlockModel, Request, Generic[NetworkT]):
    @classmethod
    def priority_fee(cls) -> RPCResponseModel[NoArgs, HexInteger]:
        return RPCResponseModel(
            cls.rpc().max_priority_fee_per_gas,
        )

    @classmethod
    def fee_history(
        cls,
        block_count: int = 4,
        lower_percentile: int = 25,
        upper_percentile: int = 75,
        block_number: BlockReference = "latest",
    ) -> RPCResponseModel[FeeHistoryArgs, FeeHistory]:
        return RPCResponseModel(
            cls.rpc().fee_history,
            FeeHistoryArgs(
                block_count=block_count,
                block_number=block_number,
                percentiles=[
                    lower_percentile,
                    upper_percentile,
                ],
            ),
        )

    @classmethod
    def get_block_transaction_count(
        cls, block_number: HexInteger
    ) -> RPCResponseModel[BlockNumberArg, int]:
        return RPCResponseModel(
            cls.rpc().get_block_tx_count_by_number,
            BlockNumberArg(
                block_number=block_number,
            ),
        )

    @classmethod
    def load_by_number(
        cls,
        block_number: int | HexInteger | BLOCK_STRINGS,
        with_tx_data: bool = False,
    ) -> RPCResponseModel[GetBlockByNumberArgs, "Block[Network]"]:
        return RPCResponseModel(
            cls.rpc().get_block_by_number,
            GetBlockByNumberArgs(
                block_number=(
                    HexInteger(block_number)
                    if isinstance(block_number, int)
                    else block_number
                ),
                with_tx_data=with_tx_data,
            ),
        )

    @classmethod
    def get_number(cls) -> RPCResponseModel[NoArgs, HexInteger]:
        return RPCResponseModel(
            cls.rpc().block_number,
        )

    @classmethod
    async def load_by_datetime(
        cls,
        when: datetime,
        low: int | None = None,
        high: int | None = None,
        apprx_block_time=12,
    ) -> "Block[Network]":
        """
        Searches for a block, finding the first block before a datetime.
        Recursively searches, using low and high as the boundaries for the binary search.
        """
        Network = cls._network
        if not when.tzinfo:
            when = when.replace(tzinfo=timezone.utc)
        if not (low and high):
            now = datetime.now(timezone.utc)
            diff = now - when
            day_diff = diff.days
            seconds_diff = day_diff * 24 * 3600
            block_number = await cls[Network].get_number()  # type: ignore
            if not low:
                low = int(
                    max(block_number - (seconds_diff / (apprx_block_time * 0.8)), 0)
                )
            if not high:
                high = int(
                    min(
                        block_number - (seconds_diff / (apprx_block_time * 1.2)),
                        block_number,
                    )
                )
        if when < datetime(
            year=2015,
            month=7,
            day=30,
            hour=3,
            minute=26,
            second=13,
            tzinfo=timezone.utc,
        ):
            raise ValueError("Block before genesis")

        if high > low:
            mid = (high + low) // 2
            mid_block = await cls[Network].load_by_number(mid)  # type: ignore

            if mid_block.timestamp == when:
                return mid_block
            elif mid_block.timestamp > when:
                return await cls[Network].load_by_datetime(when, low, mid - 1)  # type: ignore
            else:
                return await cls[Network].load_by_datetime(when, mid + 1, high)  # type: ignore
        return await cls[Network].load_by_number(high)  # type: ignore

    @classmethod
    def latest(
        cls, with_tx_data: bool = False
    ) -> RPCResponseModel[GetBlockByNumberArgs, "Block[Network]"]:
        return cls.load_by_number("latest", with_tx_data=with_tx_data)

    @classmethod
    def pending(
        cls, with_tx_data: bool = False
    ) -> RPCResponseModel[GetBlockByNumberArgs, "Block[Network]"]:
        return cls.load_by_number("pending", with_tx_data=with_tx_data)

    @classmethod
    def load_by_hash(
        cls, block_hash: HexStr, with_tx_data: bool = False
    ) -> RPCResponseModel[GetBlockByHashArgs, "Block[Network]"]:
        return RPCResponseModel(
            cls.rpc().get_block_by_hash,
            GetBlockByHashArgs(
                block_hash=block_hash,
                with_tx_data=with_tx_data,
            ),
        )

    @staticmethod
    def _to_hex(number: int | str) -> HexStr:
        if isinstance(number, int):
            return HexStr(hex(number))
        return HexStr(number)

    @classmethod
    async def subscribe_from(
        cls,
        start_block: int | None = None,
        with_tx_data: bool = True,
    ) -> AsyncIterator["Block[Network]"]:
        queue = asyncio.Queue[Block[Network]]()
        should_publish_blocks = asyncio.Event()
        asyncio.create_task(
            cls.listen(
                queue=queue,
                publish_blocks=should_publish_blocks,
                with_tx_data=with_tx_data,
            )
        )
        latest = await cls.latest()
        if not start_block:
            start_block = latest.number
        assert start_block

        # NOTE: you pull latest twice because there can be a backfill while you're populating
        for num in range(start_block, latest.number + 1):
            yield await cls.load_by_number(num, with_tx_data=with_tx_data)

        should_publish_blocks.set()
        while True:
            block = await queue.get()
            if block.number > latest.number:
                yield block

    @classmethod
    async def listen(
        cls,
        *,
        # TODO: typehinting this is tricky because the type of the Queue is conditional based on the subscription type
        queue: asyncio.Queue,
        publish_blocks: asyncio.Event = DEFAULT_EVENT,
        with_tx_data: bool = True,
        subscription_type: SUBSCRIPTION_TYPE = "newHeads",
    ):
        internal_queue: asyncio.Queue = asyncio.Queue()
        flush_queue: bool = True
        async for block in cls._listen(
            with_tx_data=with_tx_data, subscription_type=subscription_type
        ):
            if publish_blocks.is_set():
                if flush_queue:
                    while not internal_queue.empty():
                        staged_block = await internal_queue.get()
                        await queue.put(staged_block)
                    flush_queue = False
                await queue.put(block)
            else:
                await internal_queue.put(block)

    @classmethod
    async def _listen(  # noqa: C901
        cls,
        with_tx_data: bool = True,
        subscription_type: SUBSCRIPTION_TYPE = "newHeads",
    ):
        async for w3_connection in connect(
            cls.rpc().wss,
            ping_interval=60,
            ping_timeout=60,
            max_queue=10000,
        ):
            params: list
            params = [subscription_type]

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

                    if subscription_type == "newHeads":
                        if not with_tx_data:
                            block_ = BlockModel(**result)
                        else:
                            block_ = await cls.load_by_hash(
                                result["hash"], with_tx_data=with_tx_data
                            )
                        yield block_
                    else:
                        yield TransactionModel(**result)
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
    async def convert(cls, block_value: BLOCK_STRINGS | int) -> int:
        if isinstance(block_value, int):
            return block_value
        block = await cls.load_by_number(block_value)
        return block.number

    @classmethod
    def decompress(cls, raw_bytes: bytes) -> "Block":
        """Convert gzip compressed block to a Block"""
        return Block.model_validate_json(zlib.decompress(raw_bytes))

    def parent_block(self) -> RPCResponseModel[GetBlockByHashArgs, "Block[Network]"]:
        return self.load_by_hash(self.parent_hash)
