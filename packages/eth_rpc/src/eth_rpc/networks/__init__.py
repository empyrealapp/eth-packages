from .arbitrum import Arbitrum, ArbitrumSepolia
from .base import Base, BaseSepolia
from .ethereum import Ethereum
from .linea import Linea
from .sapphire import Sapphire, SapphireTestnet

Networks = {
    1: Ethereum,
    8453: Base,
    84532: BaseSepolia,
    42161: Arbitrum,
    421614: ArbitrumSepolia,
    23294: Sapphire,
    23295: SapphireTestnet,
    59144: Linea,
}


def get_network_by_chain_id(chain_id):
    return Networks.get(chain_id)


__all__ = [
    "Arbitrum",
    "ArbitrumSepolia",
    "Base",
    "BaseSepolia",
    "Ethereum",
    "Linea",
    "Networks",
    "Sapphire",
    "SapphireTestnet",
]
