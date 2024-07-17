from .arbitrum import Arbitrum as ArbitrumNetwork
from .ethereum import Ethereum as EthereumNetwork

Arbitrum = ArbitrumNetwork()
Ethereum = EthereumNetwork()


Networks = {
    1: Ethereum,
    42161: Arbitrum,
}


def get_network_by_chain_id(chain_id):
    return Networks.get(chain_id)


__all__ = [
    "Arbitrum",
    "Ethereum",
    "Networks",
]
