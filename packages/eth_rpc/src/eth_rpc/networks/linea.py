from typing import ClassVar

from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url


class Linea(Network):
    chain_id: ClassVar[int] = 59144
    name: ClassVar[str] = "Linea"
    native_currency: ClassVar[str] = "ETH"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=Url("https://rpc.linea.build"),
            wss=Url("wss://rpc.linea.build"),
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Lineascan",
        url="https://lineascan.build",
        api_url="https://api.lineascan.build/api",
    )
    alchemy_str: ClassVar[str | None] = "linea-mainnet"
    apprx_block_time: ClassVar[float] = 2.0
