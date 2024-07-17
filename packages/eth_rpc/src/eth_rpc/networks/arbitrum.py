from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url


class Arbitrum(Network):
    chain_id: int = 42161
    name: str = "Arbitrum"
    native_currency: str = "ETH"
    rpc: Rpcs = Rpcs(
        default=RpcUrl(
            http=Url("https://arb1.arbitrum.io/rpc"),
        )
    )
    block_explorer: BlockExplorer = BlockExplorer(
        name="Arbiscan",
        url="https://arbiscan.io",
        api_url="https://api.arbiscan.io/api",
    )
    alchemy_str: str = "arb-mainnet"
    apprx_block_time: float = 0.26
