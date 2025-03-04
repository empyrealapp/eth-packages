from __future__ import annotations

import math
from decimal import Decimal
from typing import TYPE_CHECKING

from eth_rpc.types import BLOCK_STRINGS, primitives
from eth_typeshed.uniswap_v3.utils.tick import get_tick_at_sqrt_price

if TYPE_CHECKING:
    from eth_typeshed.uniswap_v3.pool import UniswapV3Pool

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


async def calc_liquidity_and_amounts(
    pool: UniswapV3Pool,
    amount_in: int,
    tick_lower: primitives.int24,
    tick_upper: primitives.int24,
    is_token0: bool = True,
    block_number: BLOCK_STRINGS = "latest",
) -> tuple[primitives.uint128, primitives.uint256, primitives.uint256]:
    """
    Given an amount of token0 or token1, calculate the liquidity and the amounts of each token that would be used to create the position.

    Args:
        pool (UniswapV3Pool): The Uniswap V3 pool instance.
        amount_in (int): The amount of token0 or token1 to be used.
        tick_lower (int): The lower tick of the position.
        tick_upper (int): The upper tick of the position.
        is_token0 (bool, optional): Whether the input amount is in token0. Defaults to True.
        block_number (BLOCK_STRINGS, optional): The block number to query the state at. Defaults to "latest".

    Returns:
        tuple[int, int, int]: A tuple containing the liquidity, amount of token0 used, and amount of token1 used.
    """

    # 1) Get current sqrt price (slot0)
    slot0 = await pool.slot0().get(block_number=block_number)
    sqrtP_current = Decimal(slot0.sqrt_price_x96) / (2**96)

    # 2) Compute sqrt(P_low) and sqrt(P_high)
    #    (We typically prefer to exponentiate once, not do sqrt(1.0001**tick).)
    #    But for clarity:
    sqrtP_low = Decimal(math.sqrt(1.0001**tick_lower))
    sqrtP_high = Decimal(math.sqrt(1.0001**tick_upper))

    # 3) Depending on where current price lies, use the appropriate formula
    if sqrtP_current <= sqrtP_low:
        # Entirely below the range -> all token0
        if not is_token0:
            # The user gave us token1, but the position is below range
            return (
                primitives.uint128(0),
                primitives.uint256(0),
                primitives.uint256(amount_in),
            )

        X = amount_in
        L = (X * sqrtP_low * sqrtP_high) / (sqrtP_high - sqrtP_low)
        Y = 0
        return (
            primitives.uint128(int(L)),
            primitives.uint256(int(X)),
            primitives.uint256(int(Y)),
        )

    elif sqrtP_current >= sqrtP_high:
        # Entirely above the range -> all token1
        if is_token0:
            # The user gave us token0, but the position is above range -> that yields 0 liquidity
            return (
                primitives.uint128(0),
                primitives.uint256(amount_in),
                primitives.uint256(0),
            )

        Y = amount_in
        L = Y / (sqrtP_high - sqrtP_low)
        X = 0
        return (
            primitives.uint128(int(L)),
            primitives.uint256(int(X)),
            primitives.uint256(int(Y)),
        )

    else:
        # Price is inside the tick range
        pc = sqrtP_current
        pa = sqrtP_low
        pb = sqrtP_high

        if is_token0:
            # Single-sided deposit of token0
            # The relevant formula when the price is inside the range is that
            # your token0 will be used from pc up to pb.
            # So effectively, the “max liquidity” you can get from X token0 alone is:
            #   L0 = X * pc * pb / (pb - pc)
            # But that implies you also need some token1 if you want to cover pa -> pc.
            # If you truly want to supply *only* token0, you'll be "filling" only the portion
            # of the range from pc to pb, and ignoring pa -> pc.
            # So let's do that partial-range formula:
            X = amount_in
            L0 = (X * pc * pb) / (pb - pc)

            # That deposit uses:
            used0 = L0 * (pb - pc) / (pb * pc)  # should come back to X
            used1 = L0 * (pc - pa)  # > 0 if pa < pc

            return (
                primitives.uint128(int(L0)),
                primitives.uint256(int(used0)),
                primitives.uint256(int(used1)),
            )

        else:
            # Single-sided deposit of token1
            # Similarly, if we only deposit token1 and the price is inside the range,
            # we effectively fill from pa up to pc.
            Y = amount_in
            L1 = Y / (pc - pa)

            used0 = L1 * (pb - pc) / (pb * pc)  # token0 used
            used1 = L1 * (pc - pa)  # should come back to Y

            return (
                primitives.uint128(int(L1)),
                primitives.uint256(int(used0)),
                primitives.uint256(int(used1)),
            )
