from eth_typing import HexAddress, HexStr


class Tokens:
    class Ethereum:
        WETH = HexAddress(HexStr("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"))
        USDC = HexAddress(HexStr("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"))
        USDT = HexAddress(HexStr("0xdac17f958d2ee523a2206206994597c13d831ec7"))
        DAI = HexAddress(HexStr("0x6b175474e89094c44da98b954eedeac495271d0f"))

        main = [WETH, USDC, USDT, DAI]


class Routers:
    class Ethereum:
        UniswapV2 = HexAddress(HexStr("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"))
        UniswapV3 = HexAddress(HexStr("0xe592427a0aece92de3edee1f18e0157c05861564"))


class Factories:
    class Ethereum:
        UniswapV2 = HexAddress(HexStr("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"))
        UniswapV3 = HexAddress(HexStr("0x1F98431c8aD98523631AE4a59f267346ea31F984"))
        SushiSwap = HexAddress(HexStr("0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"))
        ShibaSwap = HexAddress(HexStr("0x115934131916C8b277DD010Ee02de363c09d037c"))
