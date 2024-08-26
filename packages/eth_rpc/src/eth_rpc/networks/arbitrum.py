from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url

Arbitrum = Network(
    chain_id=42161,
    name="Arbitrum",
    native_currency="ETH",
    rpc=Rpcs(
        default=RpcUrl(
            http=Url("https://arb1.arbitrum.io/rpc"),
            wss=None,
            # wss=Url("wss://test.com"),
        )
    ),
    block_explorer=BlockExplorer(
        name="Arbiscan",
        url="https://arbiscan.io",
        api_url="https://api.arbiscan.io/api",
    ),
    alchemy_str="arb-mainnet",
    apprx_block_time=0.26,
)
