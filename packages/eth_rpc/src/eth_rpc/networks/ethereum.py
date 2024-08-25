from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url

Ethereum = Network(
    chain_id=1,
    name="Ethereum",
    native_currency="ETH",
    rpc=Rpcs(
        default=RpcUrl(
            http=Url("https://cloudflare-eth.com"),
            wss=Url("wss://mainnet.gateway.tenderly.co"),
        )
    ),
    block_explorer=BlockExplorer(
        name="Etherscan",
        url="https://etherscan.io",
        api_url="https://api.etherscan.io/api",
    ),
    alchemy_str="eth-mainnet",
    apprx_block_time=12.05,
)
