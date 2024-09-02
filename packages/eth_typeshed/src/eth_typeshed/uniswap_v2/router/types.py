from typing import Annotated

from eth_rpc.types import Name, primitives
from eth_typing import HexAddress
from pydantic import BaseModel


class AddLiquidityRequest(BaseModel):
    token_a: Annotated[HexAddress, Name("tokenA")]
    token_b: Annotated[HexAddress, Name("tokenB")]
    amount_a_desired: Annotated[primitives.uint256, Name("amountADesired")]
    amount_b_desired: Annotated[primitives.uint256, Name("amountBDesired")]
    amount_a_min: Annotated[primitives.uint256, Name("amountAMin")]
    amount_b_min: Annotated[primitives.uint256, Name("amountBMin")]
    to: HexAddress
    deadline: primitives.uint256


class AddLiquidityETHRequest(BaseModel):
    token: Annotated[HexAddress, Name("token")]
    amount_token_desired: Annotated[primitives.uint256, Name("amountTokenDesired")]
    amount_token_min: Annotated[primitives.uint256, Name("amountTokenMin")]
    amount_eth_min: Annotated[primitives.uint256, Name("amountETHMin")]
    to: HexAddress
    deadline: primitives.uint256


class AddLiquidityResponse(BaseModel):
    amount_a: Annotated[primitives.uint256, Name("amountA")]
    amount_b: Annotated[primitives.uint256, Name("amountB")]
    liquidity: primitives.uint256


class RemoveLiquidityRequest(BaseModel):
    token_a: Annotated[primitives.address, Name("tokenA")]
    token_b: Annotated[primitives.address, Name("tokenB")]
    liquidity: primitives.uint256
    amount_a_min: Annotated[primitives.uint256, Name("amountAMin")]
    amount_b_min: Annotated[primitives.uint256, Name("amountBMin")]
    to: HexAddress
    deadline: primitives.uint256


class RemoveLiquidityETHRequest(BaseModel):
    token: Annotated[primitives.address, Name("token")]
    liquidity: primitives.uint256
    amount_token_min: Annotated[primitives.uint256, Name("amountTokenMin")]
    amount_eth_min: Annotated[primitives.uint256, Name("amountETHMin")]
    to: HexAddress
    deadline: primitives.uint256


class RemoveLiquidityResponse(BaseModel):
    amount_a: Annotated[primitives.uint256, Name("amountA")]
    amount_b: Annotated[primitives.uint256, Name("amountB")]


class RemoveLiquidityETHResponse(BaseModel):
    amount_token: Annotated[primitives.uint256, Name("amountToken")]
    amount_eth: Annotated[primitives.uint256, Name("amountETH")]


class EthSwapRequest(BaseModel):
    amount_out_min: primitives.uint256
    route: list[primitives.address]
    to: primitives.address
    deadline: primitives.uint256


class TokenSwapRequest(BaseModel):
    amount_in: primitives.uint256
    amount_out_min: primitives.uint256
    route: list[primitives.address]
    to: primitives.address
    deadline: primitives.uint256
