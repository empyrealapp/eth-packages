from typing import Annotated

from pydantic import BaseModel
from eth_typing import HexAddress

from eth_rpc.types import Indexed, primitives

from eth_rpc.event import Event


class StakeType(BaseModel):
    executor: Annotated[HexAddress, Indexed]
    user: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


class UnstakeType(BaseModel):
    user: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


StakeEvent = Event[StakeType](name="Stake")
UnstakeEvent = Event[UnstakeType](name="Unstake")
