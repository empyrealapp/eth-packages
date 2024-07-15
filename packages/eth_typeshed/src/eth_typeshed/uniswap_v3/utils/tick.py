import math

from ..constants import Q96


def tick_to_price(tick, token0_decimals=18, token1_decimals=18) -> float:
    return 1.0001**tick * (10 ** (token0_decimals - token1_decimals))


def get_tick_at_sqrt_price(sqrt_price_x96) -> int:
    return math.floor(math.log((sqrt_price_x96 / Q96) ** 2) / math.log(1.0001))
