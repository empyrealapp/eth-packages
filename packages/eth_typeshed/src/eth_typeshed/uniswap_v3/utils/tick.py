import math

from ..constants import Q96

TICK_SPACING = {
    10_000: 200,
    3_000: 60,
    500: 10,
    100: 1,
}


def tick_to_price(tick, token0_decimals=18, token1_decimals=18) -> float:
    return 1.0001**tick * (10 ** (token0_decimals - token1_decimals))


def get_tick_at_sqrt_price(sqrt_price_x96) -> int:
    return math.floor(math.log((sqrt_price_x96 / Q96) ** 2) / math.log(1.0001))


def get_closest_low_tick(tick: int, tick_spacing: int = 200) -> int:
    # Ensure tickSpacing is not zero
    if tick_spacing == 0:
        raise ValueError("tickSpacing cannot be zero")

    remainder = tick % tick_spacing
    if remainder < 0:
        return (tick // tick_spacing) * tick_spacing - tick_spacing
    else:
        return (tick // tick_spacing) * tick_spacing


def get_closest_high_tick(tick: int, tick_spacing: int = 200) -> int:
    # Ensure tickSpacing is not zero
    if tick_spacing == 0:
        raise ValueError("tickSpacing cannot be zero")

    closest_low_tick = get_closest_low_tick(tick, tick_spacing)

    if tick % tick_spacing == 0:
        return closest_low_tick  # Tick is exactly on a spacing boundary
    else:
        return closest_low_tick + tick_spacing
