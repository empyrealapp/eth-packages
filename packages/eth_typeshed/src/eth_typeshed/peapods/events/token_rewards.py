from typing import Annotated

from eth_rpc.event import Event
from eth_rpc.types import Indexed, primitives
from eth_typing import HexAddress
from pydantic import BaseModel


class AddSharesType(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


class RemoveSharesType(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


class ClaimRewardType(BaseModel):
    wallet: Annotated[HexAddress, Indexed]


class DistributeRewardType(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


class DepositRewardsType(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


class DistributeRewardV2Type(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    token: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


class DepositRewardsV2Type(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    token: Annotated[HexAddress, Indexed]
    amount: primitives.uint256


AddSharesEvent = Event[AddSharesType](name="AddShares")
RemoveSharesEvent = Event[RemoveSharesType](name="RemoveShares")
ClaimRewardEvent = Event[ClaimRewardType](name="ClaimReward")
DistributeRewardEvent = Event[DistributeRewardType](name="DistributeReward")
DepositRewardsEvent = Event[DepositRewardsType](name="DepositRewards")
DistributeRewardV2Event = Event[DistributeRewardV2Type](name="DistributeReward")
DepositRewardsV2Event = Event[DepositRewardsV2Type](name="DepositRewards")
