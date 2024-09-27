import os
from contextvars import ContextVar
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from .exceptions import UnsupportedChainIDException
from .networks import Networks, get_network_by_chain_id
from .networks.ethereum import Ethereum
from .rpc.base import BaseRPC
from .types import Network

if TYPE_CHECKING:
    from .rpc.core import RPC
    from .wallet import PrivateKeyWallet


class Transports(BaseModel):
    default: type[Network] = Ethereum
    networks: dict[int, type[Network]] = {}
    rpcs: dict[int, BaseRPC] = {}
    retries: int = 0
    id: int = 0

    def get_network(self, id: int | None = None) -> type[Network] | None:
        if not id:
            return self.default
        return self.networks.get(id)

    def force_get_network(self, id: int | None = None) -> type[Network]:
        network = self.get_network(id=id)
        if not network:
            raise ValueError("transport not found")
        return network

    model_config = ConfigDict(arbitrary_types_allowed=True)


_selected_transports: ContextVar["Transports"] = ContextVar(
    "_selected_transports",
    default=Transports(),
)


_selected_wallet: ContextVar["PrivateKeyWallet | None"] = ContextVar(
    "_selected_wallet",
    default=None,
)


def _force_get_default_network() -> type[Network]:
    transport = _selected_transports.get()
    return transport.default


def _force_get_global_rpc(network: type[Network] | None = None) -> "RPC":
    from .rpc.core import RPC

    transport = _selected_transports.get()

    if not network:
        network = transport.default

    if network.chain_id in transport.rpcs:
        return transport.rpcs[network.chain_id]  # type: ignore
    transport.rpcs[network.chain_id] = RPC(network=network)
    return transport.rpcs[network.chain_id]  # type: ignore


def set_transport(
    networks: list[type[Network]], retries: int = 0, set_default: bool = False
):
    transport = _selected_transports.get()
    if set_default:
        set_default_network(networks[0])
    transport.networks.update({network.chain_id: network for network in networks})
    transport.retries = retries


def set_default_network(network: type[Network]):
    transport = _selected_transports.get()
    transport.default = network
    transport.networks[network.chain_id] = network


def get_current_network() -> type[Network]:
    transport = _selected_transports.get()
    return transport.default


def set_rpc_timeout(timeout: float, network: type[Network] | None = None) -> None:
    rpc = _force_get_global_rpc(network)
    rpc.set_timeout(timeout)


def set_alchemy_transport(alchemy_key: str, network: type[Network]):
    set_transport(
        networks=[
            network.set(
                http=f"https://{network.alchemy_str}.g.alchemy.com/v2/{alchemy_key}",
                wss=f"wss://{network.alchemy_str}.g.alchemy.com/v2/{alchemy_key}",
            )
        ],
    )


def set_alchemy_key(alchemy_key: str, network: type[Network] | None = None) -> None:
    """
    Set Alchemy as the rpc url.
    """
    # TODO: it'd be nice to set this for all networks if no network is provided
    if network and not network.alchemy_str:
        raise ValueError("Network not supported by alchemy, set Network.alchemy_str")
    if network:
        set_alchemy_transport(alchemy_key, network)
    else:
        for network in Networks.values():
            set_alchemy_transport(alchemy_key, network)


def configure_rpc_from_env():
    chain_id = int(os.getenv("CHAIN_ID", 1))
    alchemy_key = os.getenv("ALCHEMY_KEY")

    if not alchemy_key:
        raise EnvironmentError(
            "No Alchemy key set. Please set the ALCHEMY_KEY environment variable."
        )

    network = get_network_by_chain_id(chain_id)
    if not network:
        raise UnsupportedChainIDException(f"Unsupported chain ID: {chain_id}")

    set_alchemy_key(alchemy_key, network=network)
    set_default_network(network)


def set_selected_wallet(wallet: "PrivateKeyWallet"):
    _selected_wallet.set(wallet)


def get_selected_wallet():
    return _selected_wallet.get()


def set_rpc_url(network: Network, http: str | None = None, wss: str | None = None):
    set_transport(
        networks=[
            network.set(
                http=http,
                wss=wss,
            )
        ],
    )
