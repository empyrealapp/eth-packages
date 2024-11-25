from typing import ClassVar

from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import AnyHttpUrl, AnyWebsocketUrl


class Sapphire(Network):
    chain_id: ClassVar[int] = 23294
    name: ClassVar[str] = "Sapphire"
    native_currency: ClassVar[str] = "ROSE"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=AnyHttpUrl("https://sapphire.oasis.io"),
            wss=AnyWebsocketUrl("wss://sapphire.oasis.io/ws"),
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Sapphire Testnet",
        url="https://explorer.oasis.io/mainnet/sapphire",
        api_url="https://nexus.oasis.io/v1/sapphire",
    )
    alchemy_str: ClassVar[str | None] = None
    apprx_block_time: ClassVar[float] = 6


class SapphireTestnet(Network):
    chain_id: ClassVar[int] = 23295
    name: ClassVar[str] = "Sapphire Testnet"
    native_currency: ClassVar[str] = "ROSE"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=AnyHttpUrl("https://testnet.sapphire.oasis.io"),
            wss=AnyWebsocketUrl("wss://testnet.sapphire.oasis.io/ws"),
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Sapphire Testnet",
        url="https://explorer.oasis.io/testnet/sapphire",
        api_url="https://testnet.nexus.oasis.io/v1/sapphire",
    )
    alchemy_str: ClassVar[str | None] = None
    apprx_block_time: ClassVar[float] = 6
