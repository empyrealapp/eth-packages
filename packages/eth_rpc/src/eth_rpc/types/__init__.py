from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any, NewType, Optional, TypedDict, TypeVar, Union

from eth_typing import HexAddress, HexStr, TypeStr
from pydantic import BaseModel, Field

from .basic import (  # noqa: F401
    BLOCK_STRINGS,
    BlockReference,
    Empty,
    HexInteger,
    HexInt,
)
from .event import Indexed, Name
from .response import RPCResponseModel, NoArgs
from .args import (  # noqa: F401
    AlchemyBlockReceipt,
    AlchemyParams,
    GetAccountArgs,
    EthCallArgs,
    EthCallParams,
    CallWithBlockArgs,
    FeeHistoryArgs,
    BlockNumberArg,
    GetBlockByHashArgs,
    GetBlockByNumberArgs,
    LogsArgs,
    LogsParams,
    TransactionRequest,
    GetTransactionByBlockHash,
    GetTransactionByBlockNumber,
    GetStorageArgs,
    GetCodeArgs,
    RawTransaction,
    TraceArgs,
)
from .network import BlockExplorer, Rpcs, RpcUrl, Network
from .transaction import SignedTransaction

T = TypeVar("T")
MaybeAwaitable = Union[T, Awaitable[T]]

METHOD = Field(init=False)
VersionNumber = NewType("VersionNumber", str)
EventType = NewType("EventType", BaseModel)


class ContractMethod:
    init: bool = False


@dataclass
class EvmTuple:
    values: list[Any]


class ABIParamType(BaseModel):
    indexed: bool = False
    name: str = ""
    type: TypeStr
    components: Optional[list["ABIParamType"]] = None

    def get_type(self):
        if self.components:
            return ",".join(component.get_type() for component in self.components)
        return self.type

    def model_dump(self, exclude_none=True, **kwargs):
        return super().model_dump(exclude_none=exclude_none, **kwargs)

    @classmethod
    def convert(self):
        if type == "tuple":
            tuple_vals = []
            for component in self.components:
                tuple_vals.append(component.convert())
            return EvmTuple(values=tuple_vals)


class SubscriptionResponse(TypedDict):
    id: int
    result: HexAddress
    jsorpc: VersionNumber


class EvmDataDict(TypedDict):
    address: HexAddress
    topics: list[HexStr]
    data: HexStr
    blockNumber: HexInt
    transactionHash: HexStr
    transactionIndex: HexInt
    blockHash: HexStr
    logIndex: HexInteger
    removed: bool


class EvmResult(TypedDict):
    result: EvmDataDict
    subscription: HexStr


class PendingResult(TypedDict):
    result: HexStr
    subscription: HexStr


class JsonPendingWssResponse(TypedDict):
    jsonrpc: VersionNumber
    method: str
    params: PendingResult
    subscription: HexStr


class JsonResponseWssResponse(TypedDict):
    jsonrpc: VersionNumber
    method: str
    params: EvmResult
    subscription: HexStr


__all__ = [
    "BlockExplorer",
    "Indexed",
    "Name",
    "Network",
    "NoArgs",
    "RPCResponseModel",
    "Rpcs",
    "RpcUrl",
    "SignedTransaction",
]
