from typing import Annotated  # noqa: D100

from eth_rpc.contract import ContractFunc
from eth_rpc.types import METHOD, Name, NoArgs
from eth_typeshed.erc20 import ERC20
from eth_typing import HexAddress


class StakingPool(ERC20):
    pool_rewards: Annotated[ContractFunc[NoArgs, HexAddress], Name("poolRewards")] = (
        METHOD
    )
    index_fund: Annotated[ContractFunc[NoArgs, HexAddress], Name("indexFund")] = METHOD
    staking_token: Annotated[ContractFunc[NoArgs, HexAddress], Name("stakingToken")] = (
        METHOD
    )
