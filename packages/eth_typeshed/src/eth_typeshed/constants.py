from eth_rpc import get_current_network
from eth_rpc.networks import Arbitrum, Ethereum
from eth_rpc.types import Network
from eth_typing import HexAddress, HexStr


class Tokens:
    class Ethereum:
        WETH = HexAddress(HexStr("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"))
        USDC = HexAddress(HexStr("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"))
        USDT = HexAddress(HexStr("0xdac17f958d2ee523a2206206994597c13d831ec7"))
        DAI = HexAddress(HexStr("0x6b175474e89094c44da98b954eedeac495271d0f"))

        main = [WETH, USDC, USDT, DAI]
        stables = [USDC, USDT, DAI]

    class Arbitrum:
        WETH = HexAddress(HexStr("0x82af49447d8a07e3bd95bd0d56f35241523fbab1"))
        USDC = HexAddress(HexStr("0xaf88d065e77c8cc2239327c5edb3a432268e5831"))
        USDT = HexAddress(HexStr("0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9"))

        main = [WETH, USDC, USDT]
        stables = [USDC, USDT]

    @classmethod
    def for_network(cls, network: type[Network] = get_current_network()):
        if network.chain_id == Ethereum.chain_id:
            return cls.Ethereum
        if network.chain_id == Arbitrum.chain_id:
            return cls.Arbitrum


class Routers:
    class Ethereum:
        UniswapV2 = HexAddress(HexStr("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"))
        UniswapV3 = HexAddress(HexStr("0xe592427a0aece92de3edee1f18e0157c05861564"))

        podrouter = UniswapV2

    class Arbitrum:
        UniswapV2 = HexAddress(HexStr("0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24"))
        UniswapV3 = HexAddress(HexStr("0xe592427a0aece92de3edee1f18e0157c05861564"))
        Camelot = HexAddress(HexStr("0xc873fEcbd354f5A56E00E710B90EF4201db2448d"))

        pod_router = Camelot

    class Linea:
        Lynex = HexAddress(HexStr("0x610D2f07b7EdC67565160F587F37636194C34E74"))

    @classmethod
    def for_network(cls, network: type[Network] = get_current_network()):
        if network.chain_id == Ethereum.chain_id:
            return cls.Ethereum
        if network.chain_id == Arbitrum.chain_id:
            return cls.Arbitrum


class Factories:
    class Ethereum:
        UniswapV2 = HexAddress(HexStr("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"))
        UniswapV3 = HexAddress(HexStr("0x1F98431c8aD98523631AE4a59f267346ea31F984"))
        SushiSwap = HexAddress(HexStr("0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"))
        ShibaSwap = HexAddress(HexStr("0x115934131916C8b277DD010Ee02de363c09d037c"))

        pod_factory = UniswapV2
        all_factories = [UniswapV2, UniswapV3]

    class Arbitrum:
        UniswapV2 = HexAddress(HexStr("0xf1D7CC64Fb4452F05c498126312eBE29f30Fbcf9"))
        UniswapV3 = HexAddress(HexStr("0x1F98431c8aD98523631AE4a59f267346ea31F984"))
        Camelot_V2 = HexAddress(HexStr("0x6EcCab422D763aC031210895C81787E87B43A652"))
        Camelot_V3 = HexAddress(HexStr("0x1a3c9B1d2F0529D97f2afC5136Cc23e58f1FD35B"))

        pod_factory = Camelot_V2
        all_factories = [UniswapV2, UniswapV3, Camelot_V2, Camelot_V3]

    class Linea:
        Lynex = HexAddress(HexStr("0xBc7695Fd00E3b32D08124b7a4287493aEE99f9ee"))

    @classmethod
    def for_network(cls, network: type[Network] = get_current_network()):
        if network.chain_id == Ethereum.chain_id:
            return cls.Ethereum
        if network.chain_id == Arbitrum.chain_id:
            return cls.Arbitrum
