from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from eth_typing import HexAddress
from pydantic import BaseModel


class Rewards(BaseModel):
    excluded: primitives.uint256
    realized: primitives.uint256


class TokenRewards(ProtocolBase):
    rewards_deposited: Annotated[
        ContractFunc[NoArgs, primitives.uint256], Name("rewardsDeposited")
    ] = METHOD
    rewards_deposited_tkn: Annotated[
        ContractFunc[HexAddress, primitives.uint256], Name("rewardsDeposited")
    ] = METHOD
    rewards_distributed: Annotated[
        ContractFunc[NoArgs, primitives.uint256], Name("rewardsDistributed")
    ] = METHOD
    rewards_dep_monthly: Annotated[
        ContractFunc[primitives.uint256, primitives.uint256], Name("rewardsDepMonthly")
    ] = METHOD
    beginning_of_month: Annotated[
        ContractFunc[
            Annotated[primitives.uint256, Name("_timestamp")], primitives.uint256
        ],
        Name("beginningOfMonth"),
    ] = METHOD
    get_unpaid: Annotated[
        ContractFunc[Annotated[HexAddress, Name("_wallet")], primitives.uint256],
        Name("getUnpaid"),
    ] = METHOD
    rewards: ContractFunc[HexAddress, Rewards] = METHOD
    rewards_token: Annotated[ContractFunc[NoArgs, HexAddress], Name("rewardsToken")] = (
        METHOD
    )
    shares: ContractFunc[HexAddress, primitives.uint256] = METHOD
    total_shares: Annotated[
        ContractFunc[NoArgs, primitives.uint256], Name("totalShares")
    ] = METHOD
    total_stakers: Annotated[
        ContractFunc[NoArgs, primitives.uint256], Name("totalStakers")
    ] = METHOD
    tracking_token: Annotated[
        ContractFunc[NoArgs, HexAddress], Name("trackingToken")
    ] = METHOD
