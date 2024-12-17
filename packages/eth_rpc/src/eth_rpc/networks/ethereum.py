from typing import ClassVar

from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import AnyHttpUrl, AnyWebsocketUrl


class Ethereum(Network):
    chain_id: ClassVar[int] = 1
    name: ClassVar[str] = "Ethereum"
    native_currency: ClassVar[str] = "ETH"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=AnyHttpUrl("https://cloudflare-eth.com"),
            wss=AnyWebsocketUrl("wss://mainnet.gateway.tenderly.co"),
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Etherscan",
        url="https://etherscan.io",
        api_url="https://api.etherscan.io/api",
    )
    alchemy_str: ClassVar[str | None] = "eth-mainnet"
    apprx_block_time: ClassVar[float] = 12.05


class Sepolia(Network):
    chain_id: ClassVar[int] = 11155111
    name: ClassVar[str] = "Ethereum Sepolia"
    native_currency: ClassVar[str] = "ETH"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=AnyHttpUrl("https://sepolia.gateway.tenderly.co"),
            wss=AnyWebsocketUrl("wss://ethereum-sepolia-rpc.publicnode.com"),
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Etherscan Sepolia",
        url="https://sepolia.etherscan.io",
        api_url="https://api-sepolia.etherscan.io/api",
    )
    alchemy_str: ClassVar[str | None] = "eth-sepolia"
    apprx_block_time: ClassVar[float] = 12.05
