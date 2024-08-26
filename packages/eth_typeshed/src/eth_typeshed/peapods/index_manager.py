from typing import Annotated, NamedTuple  # noqa: D100

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel

PEAPOD_INDEX_MANAGER = HexAddress(HexStr("0x0BB39BA2EE60F825348676F9A87B7CD1E3B4AE6B"))


class IndexAndStatus(NamedTuple):
    index_address: HexAddress
    verified: primitives.bool


class IndexAndStatuses(BaseModel):
    values: list[IndexAndStatus]


class IndexManager(ProtocolBase):
    all_indexes: Annotated[
        ContractFunc[NoArgs, IndexAndStatuses],
        Name("allIndexes"),
    ] = METHOD
    authorized: ContractFunc[tuple[HexAddress], bool] = METHOD
    index_length: Annotated[
        ContractFunc[NoArgs, primitives.uint256], Name("indexLength")
    ] = METHOD
    indexes: ContractFunc[primitives.uint256, IndexAndStatus] = METHOD
    owner: ContractFunc[NoArgs, HexAddress] = METHOD
