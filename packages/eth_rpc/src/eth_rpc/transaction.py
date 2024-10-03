import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Generic, Optional, cast

from eth_rpc.models import AccessList, PendingTransaction
from eth_rpc.models import Transaction as TransactionModel
from eth_rpc.models import TransactionReceipt as TransactionReceiptModel
from eth_rpc.types.args import (
    GetTransactionByBlockHash,
    GetTransactionByBlockNumber,
    RawTransaction,
    TransactionRequest,
)
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, ConfigDict, model_validator
from pydantic.alias_generators import to_camel
from typing_extensions import TypeVar
from websockets.exceptions import ConnectionClosedError
from websockets.legacy.client import WebSocketClientProtocol, connect

from ._request import Request
from ._transport import _force_get_global_rpc
from .types import (
    BLOCK_STRINGS,
    AlchemyBlockReceipt,
    AlchemyParams,
    HexInteger,
    JsonPendingWssResponse,
    RPCResponseModel,
    SubscriptionResponse,
)

T = TypeVar("T")
Network = TypeVar("Network", default=None)

logger = logging.getLogger(__name__)


class PreparedTransaction(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    type: int = 2
    gas: int
    gas_price: int | None = None
    max_fee_per_gas: int | None = None
    max_priority_fee_per_gas: int | None = None
    data: HexStr
    nonce: int
    to: HexAddress
    value: int
    access_list: Optional[list[AccessList]] = None
    chain_id: int

    def model_dump(self, *args, exclude_none=True, by_alias=True, **kwargs):
        return super().model_dump(
            *args, exclude_none=exclude_none, by_alias=by_alias, **kwargs
        )

    @model_validator(mode="after")
    def validate_xor(self):
        if self.gas_price is None and self.max_fee_per_gas is None:
            raise ValueError("Must set gas_price or max_fee_per_gas")
        if self.max_fee_per_gas is not None and self.max_priority_fee_per_gas is None:
            self.max_priority_fee_per_gas = 0
        return self


class TransactionReceipt(Request, TransactionReceiptModel, Generic[Network]):
    @classmethod
    def get_by_hash(
        self, tx_hash: HexStr
    ) -> RPCResponseModel[TransactionRequest, Optional[TransactionReceiptModel]]:
        return RPCResponseModel(
            self.rpc().get_tx_receipt,
            TransactionRequest(
                tx_hash=tx_hash,
            ),
        )

    @classmethod
    def get_block_receipts(
        self,
        block_number: Optional[int] = None,
        block_hash: Optional[HexStr] = None,
    ) -> RPCResponseModel[list[HexStr], list[TransactionReceiptModel]]:
        if block_number:
            param = hex(block_number)
        elif block_hash:
            param = block_hash
        return RPCResponseModel(
            self.rpc().get_block_receipts,
            [HexStr(param)],
        )

    @classmethod
    def alchemy_get_block_receipts(
        self,
        block_number: Optional[int] = None,
        block_hash: Optional[HexStr] = None,
    ) -> RPCResponseModel[AlchemyBlockReceipt, "AlchemyReceiptsResponse"]:
        return RPCResponseModel(
            self.rpc().alchemy_get_block_receipts,
            AlchemyBlockReceipt(
                params=AlchemyParams(
                    block_number=HexInteger(block_number) if block_number else None,
                    block_hash=block_hash,
                )
            ),
        )


class AlchemyReceiptsResponse(BaseModel):
    receipts: list[TransactionReceipt]


class Transaction(Request, TransactionModel, Generic[Network]):
    @classmethod
    def get_by_hash(
        self, tx_hash: HexStr
    ) -> RPCResponseModel[TransactionRequest, Optional["Transaction[Network]"]]:
        return RPCResponseModel(
            self.rpc().get_tx_by_hash,
            TransactionRequest(
                tx_hash=tx_hash,
            ),
        )

    @classmethod
    def get_pending_by_hash(
        self, tx_hash: HexStr
    ) -> RPCResponseModel[TransactionRequest, PendingTransaction]:
        return RPCResponseModel(
            self.rpc().get_pending_tx_by_hash,
            TransactionRequest(
                tx_hash=tx_hash,
            ),
        )

    @classmethod
    def get_receipt_by_hash(
        self, tx_hash: HexStr
    ) -> RPCResponseModel[TransactionRequest, "Transaction[Network]"]:
        return RPCResponseModel(
            self.rpc().get_tx_receipt,
            TransactionRequest(
                tx_hash=tx_hash,
            ),
        )

    @classmethod
    def send_raw_transaction(
        cls, tx: HexStr
    ) -> RPCResponseModel[RawTransaction, HexStr]:
        return RPCResponseModel(
            cls.rpc().send_raw_tx,
            RawTransaction(
                signed_tx=tx,
            ),
        )

    @classmethod
    def get_by_index(
        self,
        transaction_index: int,
        block_hash: HexStr | None = None,
        block_number: int | BLOCK_STRINGS | None = None,
    ) -> RPCResponseModel[
        GetTransactionByBlockHash | GetTransactionByBlockNumber, "Transaction[Network]"
    ]:
        if block_hash is None and block_number is None:
            raise ValueError("Must provide either block_hash or block_number")
        if block_hash:
            return RPCResponseModel(
                self.rpc().get_tx_by_block_hash,
                GetTransactionByBlockHash(
                    block_hash=block_hash,
                    index=HexInteger(transaction_index),
                ),
            )
        block_number = cast(int | BLOCK_STRINGS, block_number)
        return RPCResponseModel(
            self.rpc().get_tx_by_block_number,
            GetTransactionByBlockNumber(
                block_number=(
                    HexInteger(block_number)
                    if isinstance(block_number, int)
                    else block_number
                ),
                index=HexInteger(transaction_index),
            ),
        )

    @classmethod
    async def subscribe_pending(  # noqa: C901
        self,
    ) -> AsyncIterator[PendingTransaction]:  # noqa: C901
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
                    message_json: JsonPendingWssResponse = json.loads(message)
                    if "params" not in message_json:
                        raise ValueError(message_json)

                    transaction_hash: HexStr = message_json["params"]["result"]
                    transaction = await self.get_pending_by_hash(transaction_hash)
                    if transaction:
                        yield transaction
                except asyncio.exceptions.TimeoutError:
                    pass
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
                    logger.error("unknown connection error: %s", err)
                    await asyncio.sleep(1)
                    # we're in an iterator, so make a new connection and continue listening
                    break

    @staticmethod
    async def _send_subscription_request(
        w3_connection: WebSocketClientProtocol,
    ):
        # this only handles a list of topic0s being subscribed together
        await w3_connection.send(
            json.dumps(
                {
                    "id": 1,
                    "method": "eth_subscribe",
                    "params": ["newPendingTransactions"],
                }
            )
        )

    def receipt(
        self,
    ) -> RPCResponseModel[TransactionRequest, Optional[TransactionReceipt]]:
        return RPCResponseModel(
            self.rpc().get_tx_receipt,
            TransactionRequest(
                tx_hash=self.hash,
            ),
        )
