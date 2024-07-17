from typing import Annotated  # noqa: D100

from eth_rpc.contract import ContractFunc
from eth_rpc.function import Name
from eth_rpc.types import METHOD, primitives
from eth_typeshed._base import ProtocolBase
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel

V3_FACTORY_ADDRESS = HexAddress(HexStr("0x1a3c9B1d2F0529D97f2afC5136Cc23e58f1FD35B"))


class GetPoolRequest(BaseModel):
    token_a: Annotated[HexAddress, Name("tokenA")]
    token_b: Annotated[HexAddress, Name("tokenB")]


class CamelotV3Factory(ProtocolBase):
    pool_by_pair: Annotated[
        ContractFunc[GetPoolRequest, HexAddress], Name("poolByPair")
    ] = METHOD
