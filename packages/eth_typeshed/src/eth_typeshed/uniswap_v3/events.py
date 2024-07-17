from typing import Annotated

from eth_rpc.event import Event
from eth_rpc.types import Indexed, primitives
from pydantic import BaseModel


class V3PoolCreatedEventType(BaseModel):
    token0: Annotated[primitives.address, Indexed]
    token1: Annotated[primitives.address, Indexed]
    fee: Annotated[primitives.uint24, Indexed]
    tick_spacing: primitives.int24
    pool: primitives.address


class V3SwapEventType(BaseModel):
    sender: Annotated[primitives.address, Indexed]
    recipient: Annotated[primitives.address, Indexed]
    amount0: primitives.int256
    amount1: primitives.int256
    sqrt_price_x96: primitives.uint160
    liquidity: primitives.uint128
    tick: primitives.int24


class V3MintEventType(BaseModel):
    sender: primitives.address
    owner: Annotated[primitives.address, Indexed]
    tick_lower: Annotated[primitives.int24, Indexed]
    tick_upper: Annotated[primitives.int24, Indexed]
    amount: primitives.uint128
    amount0: primitives.uint256
    amount1: primitives.uint256


class V3IncreaseLiquidityEventType(BaseModel):
    """From the NFT Position Manager"""

    token_id: Annotated[primitives.uint256, Indexed]
    liquidity: primitives.uint128
    amount0: primitives.uint256
    amount1: primitives.uint256


# FACTORY
V3PoolCreatedEvent = Event[V3PoolCreatedEventType](name="PoolCreated")

# POOL
V3SwapEvent = Event[V3SwapEventType](name="Swap")
V3MintEvent = Event[V3MintEventType](name="Mint")

# NFT_POSITION_MANAGER
V3IncreaseLiquidityEvent = Event[V3IncreaseLiquidityEventType](name="IncreaseLiquidity")
