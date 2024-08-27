from typing import ClassVar

from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url


class Ethereum(Network):
    chain_id: ClassVar[int] = 1
    name: ClassVar[str] = "Ethereum"
    native_currency: ClassVar[str] = "ETH"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=Url("https://cloudflare-eth.com"),
            wss=Url("wss://mainnet.gateway.tenderly.co"),
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="Etherscan",
        url="https://etherscan.io",
        api_url="https://api.etherscan.io/api",
    )
    alchemy_str: ClassVar[str | None] = "eth-mainnet"
    apprx_block_time: ClassVar[float] = 12.05
