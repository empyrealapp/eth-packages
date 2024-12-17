from typing import ClassVar

from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import AnyHttpUrl


class Solana(Network):
    chain_id: ClassVar[int] = 101
    name: ClassVar[str] = "Solana"
    native_currency: ClassVar[str] = "SOL"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=AnyHttpUrl("https://api.mainnet-beta.solana.com"),
            wss=None,
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Solana Explorer",
        url="https://explorer.solana.com",
        api_url="https://api.solana.com",
    )
    alchemy_str: ClassVar[str | None] = "solana-mainnet"
    apprx_block_time: ClassVar[float] = 1.0
