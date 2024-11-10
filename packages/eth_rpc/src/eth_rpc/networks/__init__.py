from eth_rpc.types import Network

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


def get_network_by_name(network_name: str) -> type[Network]:
    """gets the network by the name by matching against the networks"""

    matching_network = [
        network
        for network in Networks.values()
        if network.__name__.lower() == network_name.lower()
    ]
    if not len(matching_network) != 1:
        raise ValueError("Network not found")
    return matching_network[0]


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
