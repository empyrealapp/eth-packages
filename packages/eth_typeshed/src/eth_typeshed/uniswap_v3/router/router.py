from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, primitives
from pydantic import BaseModel


class Request(BaseModel):
    params: tuple[
        primitives.address,  # tokenIn
        primitives.address,  # tokenOut
        primitives.uint24,  # fee
        primitives.address,  # recipient
        primitives.uint256,  # amountIn
        primitives.uint256,  # amountOutMinimum
        primitives.uint160,  # sqrtPriceLimitX96
    ]


class V3SwapRouter(ProtocolBase):
    exact_input_single: Annotated[
        ContractFunc[
            Request,
            primitives.uint256,
        ],
        Name("exactInputSingle"),
    ] = METHOD
