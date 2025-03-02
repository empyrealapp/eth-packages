from __future__ import annotations

from typing import TYPE_CHECKING

from eth_rpc.types import BLOCK_STRINGS, primitives
from eth_typeshed.multicall import MULTICALL3_ADDRESS, Multicall
from eth_typing import HexAddress

if TYPE_CHECKING:
    from eth_typeshed.uniswap_v3.pool import UniswapV3Pool


def _to_uint256(num: int) -> primitives.uint256:
    return primitives.uint256(num if num >= 0 else num + 2**256)


async def calculate_fee_growth_inside(
    pool: UniswapV3Pool,
    tick_lower: primitives.int24,
    tick_upper: primitives.int24,
    block_number: int | BLOCK_STRINGS = "latest",
    multicall_address: HexAddress = MULTICALL3_ADDRESS,
) -> tuple[primitives.uint256, primitives.uint256]:
    multicall = Multicall[pool._network](address=multicall_address)
    (
        fee_growth_global0_x128,
        fee_growth_global1_x128,
        lower_tick,
        upper_tick,
        slot0,
    ) = await multicall.execute(
        pool.fee_growth_global0(),
        pool.fee_growth_global1(),
        pool.ticks(tick_lower),
        pool.ticks(tick_upper),
        pool.slot0(),
        block_number=block_number,
    )
    tick_current = slot0.tick

    fee_growth_outside0_lower = (
        lower_tick.fee_growth_outside0
        if lower_tick.initialized
        else fee_growth_global0_x128
    )
    fee_growth_outside1_lower = (
        lower_tick.fee_growth_outside1
        if lower_tick.initialized
        else fee_growth_global1_x128
    )
    fee_growth_outside0_upper = (
        upper_tick.fee_growth_outside0
        if upper_tick.initialized
        else fee_growth_global0_x128
    )
    fee_growth_outside1_upper = (
        upper_tick.fee_growth_outside1
        if upper_tick.initialized
        else fee_growth_global1_x128
    )

    # calculate fee growth below
    fee_growth_below0_x128: int
    fee_growth_below1_x128: int
    if tick_current >= tick_lower:
        fee_growth_below0_x128 = fee_growth_outside0_lower
        fee_growth_below1_x128 = fee_growth_outside1_lower
    else:
        fee_growth_below0_x128 = fee_growth_global0_x128 - fee_growth_outside0_lower
        fee_growth_below1_x128 = fee_growth_global1_x128 - fee_growth_outside1_lower

    # calculate fee growth above
    fee_growth_above0_x128: int
    fee_growth_above1_x128: int
    if tick_current < tick_upper:
        fee_growth_above0_x128 = fee_growth_outside0_upper
        fee_growth_above1_x128 = fee_growth_outside1_upper
    else:
        fee_growth_above0_x128 = fee_growth_global0_x128 - fee_growth_outside0_upper
        fee_growth_above1_x128 = fee_growth_global1_x128 - fee_growth_outside1_upper

    # calculate fee growth inside
    fee_growth_inside0_x128 = (
        fee_growth_global0_x128 - fee_growth_below0_x128 - fee_growth_above0_x128
    )
    fee_growth_inside1_x128 = (
        fee_growth_global1_x128 - fee_growth_below1_x128 - fee_growth_above1_x128
    )
    return _to_uint256(fee_growth_inside0_x128), _to_uint256(fee_growth_inside1_x128)


async def calculate_fees(
    pool: UniswapV3Pool,
    tick_lower: primitives.int24,
    tick_upper: primitives.int24,
    user_liquidity: primitives.uint128,
    start_block: int | BLOCK_STRINGS,
    end_block: int | BLOCK_STRINGS = "latest",
) -> tuple[primitives.uint256, primitives.uint256]:
    [start_fee_growth_inside0, start_fee_growth_inside1] = (
        await calculate_fee_growth_inside(
            pool,
            tick_lower,
            tick_upper,
            start_block,
        )
    )
    [end_fee_growth_inside0, end_fee_growth_inside1] = (
        await calculate_fee_growth_inside(
            pool,
            tick_lower,
            tick_upper,
            end_block,
        )
    )

    tokens_owed0 = (
        (end_fee_growth_inside0 - start_fee_growth_inside0) * user_liquidity / 2**128
    )
    tokens_owed1 = (
        (end_fee_growth_inside1 - start_fee_growth_inside1) * user_liquidity / 2**128
    )

    return primitives.uint256(int(tokens_owed0)), primitives.uint256(int(tokens_owed1))
