from typing import Annotated
from eth_typing import HexAddress, HexStr

from eth_rpc.contract import ContractFunc
from eth_rpc.types import METHOD
from eth_typeshed._base import ProtocolBase
from eth_rpc.function import Name
from pydantic import BaseModel

V2_FACTORY_ADDRESS = HexAddress(HexStr("0x5C69BEE701EF814A2B6A3EDD4B1652CB9CC5AA6F"))


class GetPairRequest(BaseModel):
    token_a: Annotated[HexAddress, Name("tokenA")]
    token_b: Annotated[HexAddress, Name("tokenB")]


class UniswapV2Factory(ProtocolBase):
    get_pair: Annotated[ContractFunc[GetPairRequest, HexAddress], Name("getPair")] = METHOD
