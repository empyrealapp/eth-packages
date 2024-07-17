from eth_rpc.types import primitives

from ..constants import Q128, Q256

ZERO = 0


def sub_in_256(x, y):
    difference = x - y
    if difference < ZERO:
        return Q256 + difference
    else:
        return difference


def get_fees(
    fee_growth_global0: primitives.uint256,
    fee_growth_global1: primitives.uint256,
    fee_growth0_low: primitives.uint256,
    fee_growth0_hi: primitives.uint256,
    fee_growth_inside0: primitives.uint256,
    fee_growth1_low: primitives.uint256,
    fee_growth1_hi: primitives.uint256,
    fee_growth_inside1: primitives.uint256,
    liquidity: primitives.uint128,
    tick_lower: primitives.int24,
    tick_upper: primitives.int24,
    tick_current: primitives.int24,
):
    fee_growth_global_0 = fee_growth_global0
    fee_growth_global_1 = fee_growth_global1
    tick_lower_fee_growth_outside_0 = fee_growth0_low
    tick_lower_fee_growth_outside_1 = fee_growth1_low
    tick_upper_fee_growth_outside_0 = fee_growth0_hi
    tick_upper_fee_growth_outside_1 = fee_growth1_hi

    tick_lower_fee_growth_below_0 = ZERO
    tick_lower_fee_growth_below_1 = ZERO
    tick_upper_fee_growth_above_0 = ZERO
    tick_upper_fee_growth_above_1 = ZERO

    if tick_current >= tick_upper:
        tick_upper_fee_growth_above_0 = sub_in_256(
            fee_growth_global_0, tick_upper_fee_growth_outside_0
        )
        tick_upper_fee_growth_above_1 = sub_in_256(
            fee_growth_global_1, tick_upper_fee_growth_outside_1
        )
    else:
        tick_upper_fee_growth_above_0 = tick_upper_fee_growth_outside_0
        tick_upper_fee_growth_above_1 = tick_upper_fee_growth_outside_1

    if tick_current < tick_lower:
        tick_lower_fee_growth_below_0 = sub_in_256(
            fee_growth_global_0, tick_lower_fee_growth_outside_0
        )
        tick_lower_fee_growth_below_1 = sub_in_256(
            fee_growth_global_1, tick_lower_fee_growth_outside_1
        )
    else:
        tick_lower_fee_growth_below_0 = tick_lower_fee_growth_outside_0
        tick_lower_fee_growth_below_1 = tick_lower_fee_growth_outside_1

    fr_t1_0 = sub_in_256(
        sub_in_256(fee_growth_global_0, tick_lower_fee_growth_below_0),
        tick_upper_fee_growth_above_0,
    )
    fr_t1_1 = sub_in_256(
        sub_in_256(fee_growth_global_1, tick_lower_fee_growth_below_1),
        tick_upper_fee_growth_above_1,
    )

    fee_growth_inside_last_0 = fee_growth_inside0
    fee_growth_inside_last_1 = fee_growth_inside1

    uncollected_fees_0 = (
        liquidity * sub_in_256(fr_t1_0, fee_growth_inside_last_0)
    ) // Q128
    uncollected_fees_1 = (
        liquidity * sub_in_256(fr_t1_1, fee_growth_inside_last_1)
    ) // Q128

    return uncollected_fees_0, uncollected_fees_1
