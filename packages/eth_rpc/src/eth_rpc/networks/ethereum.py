from eth_rpc.types import BlockExplorer, Network, Rpcs, RpcUrl
from pydantic.networks import Url


class Ethereum(Network):
    chain_id: int = 1
    name: str = "Ethereum"
    native_currency: str = "ETH"
    rpc: Rpcs = Rpcs(
        default=RpcUrl(
            http=Url("https://cloudflare-eth.com"),
            wss=Url("wss://mainnet.gateway.tenderly.co"),
        )
    )
    block_explorer: BlockExplorer = BlockExplorer(
        name="Etherscan",
        url="https://etherscan.io",
        api_url="https://api.etherscan.io/api",
    )
    alchemy_str: str = "eth-mainnet"
    apprx_block_time: float = 12.05
