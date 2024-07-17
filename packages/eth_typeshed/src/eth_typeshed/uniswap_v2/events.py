from typing import Annotated

from eth_rpc.event import Event
from eth_rpc.types import Indexed, primitives
from eth_typing import HexAddress
from pydantic import BaseModel


class V2SwapEventType(BaseModel):
    sender: Annotated[primitives.address, Indexed]
    amount0_in: primitives.uint256
    amount1_in: primitives.uint256
    amount0_out: primitives.uint256
    amount1_out: primitives.uint256
    to: Annotated[primitives.address, Indexed]


class V2PairCreatedEventType(BaseModel):
    token0: Annotated[primitives.address, Indexed]
    token1: Annotated[primitives.address, Indexed]
    pair: primitives.address
    index: primitives.uint256


class V2SyncEventType(BaseModel):
    reserve0: primitives.uint112
    reserve1: primitives.uint112


class V2MintEventType(BaseModel):
    sender: Annotated[HexAddress, Indexed]
    amount0: primitives.uint256
    amount1: primitives.uint256


class V2BurnEventType(BaseModel):
    sender: Annotated[HexAddress, Indexed]
    amount0: primitives.uint256
    amount1: primitives.uint256
    to: Annotated[HexAddress, Indexed]


V2SwapEvent = Event[V2SwapEventType](name="Swap")
V2PairCreatedEvent = Event[V2PairCreatedEventType](name="PairCreated")
V2SyncEvent = Event[V2SyncEventType](name="Sync")
V2MintEvent = Event[V2MintEventType](name="Mint")
V2BurnEvent = Event[V2BurnEventType](name="Burn")
