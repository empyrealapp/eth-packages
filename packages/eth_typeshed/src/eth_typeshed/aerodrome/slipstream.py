from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, primitives
from eth_typing import HexAddress
from pydantic import BaseModel

ROUTER_ADDRESS = "0xBE6D8f0d05cC4be24d5167a3eF062215bE6D18a5"


class ExactInputSingleParams(BaseModel):
    token_in: Annotated[HexAddress, Name("tokenIn")]
    token_out: Annotated[HexAddress, Name("tokenOut")]
    tick_spacing: Annotated[primitives.int24, Name("tickSpacing")]
    recipient: HexAddress
    deadline: primitives.uint256
    amount_in: Annotated[primitives.uint256, Name("amountIn")]
    amount_out_minimum: Annotated[primitives.uint256, Name("amountOutMinimum")]
    sqrt_price_limit_x96: Annotated[primitives.uint160, Name("sqrtPriceLimitX96")]


class SlipstreamRouter(ProtocolBase):
    exact_input_single: Annotated[
        ContractFunc[ExactInputSingleParams, primitives.uint256],
        Name("exactInputSingle"),
    ] = METHOD
