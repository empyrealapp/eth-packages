from collections.abc import Awaitable
from dataclasses import dataclass
from typing import Any, NewType, Optional, TypedDict, TypeVar, Union

from eth_typing import HexAddress, HexStr, TypeStr
from pydantic import BaseModel, Field

from .args import (  # noqa: F401
    AlchemyBlockReceipt,
    AlchemyParams,
    BlockNumberArg,
    CallWithBlockArgs,
    EthCallArgs,
    EthCallParams,
    FeeHistoryArgs,
    GetAccountArgs,
    GetBlockByHashArgs,
    GetBlockByNumberArgs,
    GetCodeArgs,
    GetStorageArgs,
    GetTransactionByBlockHash,
    GetTransactionByBlockNumber,
    LogsArgs,
    LogsParams,
    RawTransaction,
    TraceArgs,
    TransactionRequest,
)
from .basic import (
    ALL_PRIMITIVES,
    BLOCK_STRINGS,
    BlockReference,
    HexInt,
    HexInteger,
    map_type_to_str,
)
from .event import Indexed, Name
from .network import BlockExplorer, Network, Rpcs, RpcUrl
from .primitives import BASIC_TYPES, BYTES_TYPES
from .response import NoArgs, RPCResponseModel
from .struct import Struct
from .transaction import SignedTransaction
from .typed_data import Domain, EIP712Model

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
    "ALL_PRIMITIVES",
    "BASIC_TYPES",
    "BYTES_TYPES",
    "BLOCK_STRINGS",
    "BlockExplorer",
    "BlockReference",
    "Domain",
    "EIP712Model",
    "Indexed",
    "Name",
    "Network",
    "NoArgs",
    "RPCResponseModel",
    "Rpcs",
    "RpcUrl",
    "SignedTransaction",
    "Struct",
    "map_type_to_str",
]
