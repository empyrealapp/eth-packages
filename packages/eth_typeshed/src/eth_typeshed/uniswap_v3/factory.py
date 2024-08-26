from typing import Annotated  # noqa: D100

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, primitives
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel

V3_FACTORY_ADDRESS = HexAddress(HexStr("0x1F98431c8aD98523631AE4a59f267346ea31F984"))


class GetPoolRequest(BaseModel):
    token_a: Annotated[HexAddress, Name("tokenA")]
    token_b: Annotated[HexAddress, Name("tokenB")]
    fee: primitives.uint24


class UniswapV3Factory(ProtocolBase):
    get_pool: Annotated[ContractFunc[GetPoolRequest, HexAddress], Name("getPool")] = (
        METHOD
    )
