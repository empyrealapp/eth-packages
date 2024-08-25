from typing import Annotated, NamedTuple  # noqa: D100

from eth_rpc.contract import ContractFunc
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from eth_typeshed.erc20 import ERC20
from eth_typing import HexAddress
from pydantic import BaseModel


class IndexAssetInfo(NamedTuple):
    token: HexAddress
    weighting: primitives.uint256
    basePriceUSDX96: primitives.uint256
    c1: HexAddress
    q1: primitives.uint256


class IndexAssets(BaseModel):
    values: list[IndexAssetInfo]


class Fees(BaseModel):
    burn: primitives.uint256
    bond: primitives.uint256
    debond: primitives.uint256
    buy: primitives.uint256
    sell: primitives.uint256
    partner: primitives.uint256


class WeightedIndex(ERC20):
    get_all_assets: Annotated[
        ContractFunc[NoArgs, IndexAssets], Name("getAllAssets")
    ] = METHOD
    get_idx_price_USDX96: Annotated[
        ContractFunc[NoArgs, tuple[primitives.uint256, primitives.uint256]],
        Name("getIdxPriceUSDX96"),
    ] = METHOD
    index_tokens: Annotated[
        ContractFunc[primitives.uint256, IndexAssetInfo], Name("indexTokens")
    ] = METHOD
    indextype: Annotated[ContractFunc[NoArgs, primitives.uint8], Name("indexType")] = (
        METHOD
    )
    bond_fee: Annotated[ContractFunc[NoArgs, primitives.uint256], Name("BOND_FEE")] = (
        METHOD
    )
    debond_fee: Annotated[
        ContractFunc[NoArgs, primitives.uint256], Name("DEBOND_FEE")
    ] = METHOD
    is_asset: Annotated[ContractFunc[HexAddress, primitives.bool], Name("isAsset")] = (
        METHOD
    )
    lp_rewards_token: Annotated[
        ContractFunc[NoArgs, HexAddress], Name("lpRewardsToken")
    ] = METHOD
    lp_staking_pool: Annotated[
        ContractFunc[NoArgs, HexAddress], Name("lpStakingPool")
    ] = METHOD
    paired_lp_token: Annotated[
        ContractFunc[NoArgs, HexAddress], Name("PAIRED_LP_TOKEN")
    ] = METHOD
    partner: ContractFunc[NoArgs, HexAddress] = METHOD
    fees: ContractFunc[NoArgs, Fees] = METHOD
    created: ContractFunc[NoArgs, primitives.uint256] = METHOD
    index_type: Annotated[ContractFunc[NoArgs, primitives.uint8], Name("indexType")] = (
        METHOD
    )
