from .arbitrum import Arbitrum as ArbitrumNetwork
from .ethereum import Ethereum as EthereumNetwork

Arbitrum = ArbitrumNetwork()
Ethereum = EthereumNetwork()


Networks = {
    1: Ethereum,
    42161: Arbitrum,
}

__all__ = [
    "Arbitrum",
    "Ethereum",
    "Networks",
]
