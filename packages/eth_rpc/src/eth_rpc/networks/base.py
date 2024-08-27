from typing import ClassVar

from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url


class Base(Network):
    chain_id: ClassVar[int] = 8453
    name: ClassVar[str] = "Base"
    native_currency: ClassVar[str] = "ETH"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=Url("https://base.llamarpc.com"),
            wss=None,
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Basescan",
        url="https://basescan.org",
        api_url="https://api.basescan.org/api",
    )
    alchemy_str: ClassVar[str | None] = "base-mainnet"
    apprx_block_time: ClassVar[float] = 2.0


class BaseSepolia(Network):
    chain_id: ClassVar[int] = 84532
    name: ClassVar[str] = "BaseSepolia"
    native_currency: ClassVar[str] = "ETH"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=Url("https://sepolia.base.org/"),
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="BaseScan-Sepolia",
        url="https://sepolia.basescan.org",
        api_url="https://api-sepolia.basescan.org/api",
    )
    alchemy_str: ClassVar[str] = "base-sepolia"
    apprx_block_time: ClassVar[float] = 2.0
