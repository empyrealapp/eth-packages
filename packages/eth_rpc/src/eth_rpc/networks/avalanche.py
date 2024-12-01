from typing import ClassVar

from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import AnyHttpUrl


class Avalanche(Network):
    chain_id: ClassVar[int] = 43114
    name: ClassVar[str] = "Avalanche"
    native_currency: ClassVar[str] = "AVAX"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=AnyHttpUrl("https://avalanche-fuji.publicnode.com"),
            wss=None,
            # wss=Url("wss://test.com"),
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Snowtrace",
        url="https://snowtrace.io",
        api_url="https://api.snowtrace.io/api",
    )
    alchemy_str: ClassVar[str | None] = "avalanche-fuji"
    apprx_block_time: ClassVar[float] = 3.0
