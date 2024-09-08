from typing import ClassVar

from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url


class Arbitrum(Network):
    chain_id: ClassVar[int] = 42161
    name: ClassVar[str] = "Arbitrum"
    native_currency: ClassVar[str] = "ETH"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=Url("https://arb1.arbitrum.io/rpc"),
            wss=None,
            # wss=Url("wss://test.com"),
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Arbiscan",
        url="https://arbiscan.io",
        api_url="https://api.arbiscan.io/api",
    )
    alchemy_str: ClassVar[str | None] = "arb-mainnet"
    apprx_block_time: ClassVar[float] = 0.26


class ArbitrumSepolia(Network):
    chain_id: ClassVar[int] = 421614
    name: ClassVar[str] = "ArbitrumSepolia"
    native_currency: ClassVar[str] = "ETH"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=Url("https://arbitrum-sepolia.publicnode.com"),
            wss=None,
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Arbiscan",
        url="https://sepolia.arbiscan.io",
        api_url="https://api-sepolia.arbiscan.io/api",
    )
    alchemy_str: ClassVar[str | None] = "arb-sepolia"
    apprx_block_time: ClassVar[float] = 0.26
