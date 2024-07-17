from typing import Annotated

from eth_rpc.event import Event
from eth_rpc.types import Indexed, primitives
from eth_typing import HexAddress
from pydantic import BaseModel


class StakeType(BaseModel):
    executor: Annotated[HexAddress, Indexed]
    user: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


class UnstakeType(BaseModel):
    user: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


StakeEvent = Event[StakeType](name="Stake")
UnstakeEvent = Event[UnstakeType](name="Unstake")
