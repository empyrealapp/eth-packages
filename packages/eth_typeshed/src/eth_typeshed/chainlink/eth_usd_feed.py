from typing import Annotated, NamedTuple  # noqa: D100

from eth_rpc import ContractFunc, ProtocolBase, get_current_network
from eth_rpc.networks import Arbitrum, Ethereum
from eth_rpc.types import METHOD, Name, Network, NoArgs, primitives
from eth_typing import HexAddress, HexStr


class ChainlinkPriceOracle:
    class Ethereum:
        ADA = HexAddress(HexStr("0xAE48c91dF1fE419994FFDa27da09D5aC69c30f55"))
        AMPL = HexAddress(HexStr("0x492575FDD11a0fCf2C6C719867890a7648d526eB"))
        AVAX = HexAddress(HexStr("0xFF3EEb22B5E3dE6e705b44749C2559d704923FD7"))
        BNB = HexAddress(HexStr("0x14e613AC84a31f709eadbdF89C6CC390fDc9540A"))
        BTC_ETH = HexAddress(HexStr("0xdeb288F737066589598e9214E782fa5A8eD689e8"))
        BTC_USD = HexAddress(HexStr("0xF4030086522a5bEEa4988F8cA5B36dbC97BeE88c"))
        BUSD = HexAddress(HexStr("0x833D8Eb16D306ed1FbB5D7A2E019e106B960965A"))
        DOGE = HexAddress(HexStr("0x2465CefD3b488BE410b941b1d4b2767088e2A028"))
        ETH = HexAddress(HexStr("0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419"))
        EUR = HexAddress(HexStr("0xb49f677943BC038e9857d61E7d053CaA2C1734C1"))
        FRAX = HexAddress(HexStr("0xB9E1E3A9feFf48998E45Fa90847ed4D467E8BcfD"))
        JPY = HexAddress(HexStr("0xBcE206caE7f0ec07b545EddE332A47C2F75bbeb3"))
        LTC = HexAddress(HexStr("0x6AF09DF7563C363B5763b9102712EbeD3b9e859B"))
        LUSD = HexAddress(HexStr("0x3D7aE7E594f2f2091Ad8798313450130d0Aba3a0"))
        SOL = HexAddress(HexStr("0x4ffC43a60e009B551865A93d232E33Fce9f01507"))
        UNI = HexAddress(HexStr("0x553303d460EE0afB37EdFf9bE42922D8FF63220e"))
        USDC = HexAddress(HexStr("0x8fFfFfd4AfB6115b954Bd326cbe7B4BA576818f6"))
        USDT = HexAddress(HexStr("0x3E7d1eAB13ad0104d2750B8863b489D65364e32D"))

    class Arbitrum:
        ETH = HexAddress(HexStr("0x639Fe6ab55C921f74e7fac1ee960C0B6293ba612"))

    @classmethod
    def for_network(cls, network: type[Network] | None = None):
        if network is None:
            network = get_current_network()
        if network.chain_id == Ethereum.chain_id:
            return cls.Ethereum
        if network.chain_id == Arbitrum.chain_id:
            return cls.Arbitrum


class LatestRoundData(NamedTuple):
    round_id: Annotated[primitives.uint256, Name("roundId")]
    answer: primitives.int256
    started_at: Annotated[primitives.uint256, Name("startedAt")]
    updated_at: Annotated[primitives.uint256, Name("updatedAt")]
    answerer_in_round: Annotated[primitives.uint80, Name("answeredInRound")]


class ETHUSDPriceFeed(ProtocolBase):
    decimals: ContractFunc[
        NoArgs,
        primitives.uint256,
    ] = METHOD
    latest_round_data: Annotated[
        ContractFunc[
            NoArgs,
            LatestRoundData,
        ],
        Name("latestRoundData"),
    ] = METHOD
