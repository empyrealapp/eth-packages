from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url

Base = Network(
    chain_id=8453,
    name="Base",
    native_currency="ETH",
    rpc=Rpcs(
        default=RpcUrl(
            http=Url("https://base.llamarpc.com	"),
            wss=Url("wss://base-rpc.publicnode.com"),
        )
    ),
    block_explorer=BlockExplorer(
        name="Basescan",
        url="https://basescan.org",
        api_url="https://api.basescan.org/api",
    ),
    alchemy_str="base-mainnet",
    apprx_block_time=2,
)
