from decimal import Decimal


class UniswapV3FactoryAddresses:
    class Ethereum:
        Uniswap = "0x1F98431c8aD98523631AE4a59f267346ea31F984"


MAX_TICK = 887272
MIN_TICK = -MAX_TICK

Q96 = Decimal(2**96)
Q128 = Decimal(2**128)
Q192 = Decimal(2**192)
Q256 = Decimal(2**256)

TICK_BITMAP_RANGE = {
    100: (-3466, 3465),
    500: (-347, 346),
    3_000: (-58, 57),
    10_000: (-18, 17),
}
