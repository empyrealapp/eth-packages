from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, NoArgs, primitives
from eth_typing import HexAddress
from pydantic import BaseModel


class FunctionType:
    Bond = 0
    Debond = 1
    Approve = 2
    SwapV2 = 3
    SwapV3 = 4


class FunctionArg(BaseModel):
    type: primitives.uint8
    data: primitives.bytes


class PeapodsRouter(ProtocolBase):
    route: ContractFunc[
        tuple[
            primitives.uint256,
            HexAddress,
            HexAddress,
            list[tuple[primitives.uint8, primitives.bytes]],
        ],
        primitives.uint256,
    ] = METHOD

    ping: ContractFunc[
        NoArgs,
        primitives.uint256,
    ] = METHOD
