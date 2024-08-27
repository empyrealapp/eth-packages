from .arbitrum import Arbitrum
from .base import Base, BaseSepolia
from .ethereum import Ethereum

Networks = {
    1: Ethereum,
    8453: Base,
    84532: BaseSepolia,
    42161: Arbitrum,
}


def get_network_by_chain_id(chain_id):
    return Networks.get(chain_id)


__all__ = [
    "Arbitrum",
    "Base",
    "BaseSepolia",
    "Ethereum",
    "Networks",
]
