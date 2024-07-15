from contextvars import ContextVar
from typing import TYPE_CHECKING

from pydantic import BaseModel, ConfigDict

from .rpc.base import BaseRPC
from .networks import Ethereum
from .types import Network

if TYPE_CHECKING:
    from .rpc.core import RPC


class Transports(BaseModel):
    default: Network = Ethereum
    networks: dict[int, Network] = {}
    rpcs: dict[int, BaseRPC] = {}
    retries: int = 0
    id: int = 0

    def get_network(self, id: int | None = None) -> Network | None:
        if not id:
            return self.default
        return self.networks.get(id)

    def force_get_network(self, id: int | None = None) -> Network:
        network = self.get_network(id=id)
        if not network:
            raise ValueError("transport not found")
        return network

    model_config = ConfigDict(arbitrary_types_allowed=True)


_selected_transports: ContextVar["Transports"] = ContextVar(
    "_selected_transports",
    default=Transports(),
)


def _force_get_default_network() -> Network:
    transport = _selected_transports.get()
    return transport.default


def _force_get_global_rpc(network: Network | None = None) -> "RPC":
    from .rpc.core import RPC

    transport = _selected_transports.get()

    if not network:
        network = transport.default

    if network.chain_id in transport.rpcs:
        return transport.rpcs[network.chain_id]  # type: ignore
    transport.rpcs[network.chain_id] = RPC(network=network)
    return transport.rpcs[network.chain_id]  # type: ignore


def set_transport(networks: list[Network], retries: int = 0):
    transport = _selected_transports.get()
    transport.default = networks[0]
    transport.networks = {network.chain_id: network for network in networks}
    transport.retries = retries


def set_default_network(network: Network):
    transport = _selected_transports.get()
    transport.default = network
    transport.networks[network.chain_id] = network


def get_current_network() -> Network:
    transport = _selected_transports.get()
    return transport.default


def set_rpc_timeout(timeout: float, network: Network | None = None):
    rpc = _force_get_global_rpc(network)
    rpc.set_timeout(timeout)


def set_alchemy_key(alchemy_key, network=Ethereum):
    if not network.alchemy_str:
        raise ValueError("Network not supported by alchemy, set Network.alchemy_str")
    set_transport(
        networks=[
            network.set(
                http=f"https://{network.alchemy_str}.g.alchemy.com/v2/{alchemy_key}",
                wss=f"wss://{network.alchemy_str}.g.alchemy.com/v2/{alchemy_key}",
            )
        ]
    )
