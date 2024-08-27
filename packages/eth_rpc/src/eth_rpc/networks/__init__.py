from enum import Enum
from typing import Literal

from .arbitrum import Arbitrum as ArbitrumMainnet
from .base import Base as BaseMainnet
from .ethereum import Ethereum as EthereumMainnet

AllNetworks = {
    1: EthereumMainnet,
    8453: BaseMainnet,
    42161: ArbitrumMainnet,
}


class Networks(Enum):
    Arbitrum = ArbitrumMainnet
    Base = BaseMainnet
    Ethereum = EthereumMainnet


Arbitrum = Literal[Networks.Arbitrum]
Base = Literal[Networks.Base]
Ethereum = Literal[Networks.Ethereum]


def get_network_by_chain_id(chain_id):
    return Networks.get(chain_id)


__all__ = [
    "Arbitrum",
    "Base",
    "Ethereum",
    "Networks",
]
