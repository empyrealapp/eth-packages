import math

from .tick import get_tick_at_sqrt_price

Q96 = 2**96
TICK_BASE = 1.0001


def price_to_tick(p):
    return math.floor(math.log(p, TICK_BASE))


def price_to_sqrtp(p):
    return int(math.sqrt(p) * Q96)


def sqrtp_to_price(sqrt_price):
    return (sqrt_price / Q96) ** 2


def liquidity0(amount, pa, pb):
    if pa > pb:
        pa, pb = pb, pa
    return (amount * (pa * pb) / Q96) / (pb - pa)


def liquidity1(amount, pa, pb):
    if pa > pb:
        pa, pb = pb, pa
    return amount * Q96 / (pb - pa)


def liquidity_to_token_amounts(liquidity, sqrt_price_x96, tick_low, tick_high):
    sqrt_ratio_a = math.sqrt(TICK_BASE**tick_low)
    sqrt_ratio_b = math.sqrt(TICK_BASE**tick_high)
    current_tick = get_tick_at_sqrt_price(sqrt_price_x96)
    sqrt_price = sqrt_price_x96 / Q96
    amount0 = 0
    amount1 = 0

    if current_tick < tick_low:
        amount0 = math.floor(
            liquidity * ((sqrt_ratio_b - sqrt_ratio_a) / (sqrt_ratio_a * sqrt_ratio_b))
        )
    elif current_tick >= tick_high:
        amount1 = math.floor(liquidity * (sqrt_ratio_b - sqrt_ratio_a))
    elif tick_low <= current_tick < tick_high:
        amount0 = math.floor(
            liquidity * ((sqrt_ratio_b - sqrt_price) / (sqrt_price * sqrt_ratio_b))
        )
        amount1 = math.floor(liquidity * (sqrt_price - sqrt_ratio_a))

    return [amount0, amount1]


def tick_to_price(tick):
    return TICK_BASE**tick
