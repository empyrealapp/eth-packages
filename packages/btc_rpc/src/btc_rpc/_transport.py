from contextvars import ContextVar
from typing import TYPE_CHECKING

from eth_typing import HexStr
from pydantic import BaseModel, ConfigDict, Field

from .networks import Bitcoin
from .rpc.base import BaseRPC
from .types import Network

if TYPE_CHECKING:
    from .rpc.core import RPC


class Transports(BaseModel):
    default: type[Network] = Field(default=Bitcoin)
    networks: dict[HexStr, type[Network]] = {}
    rpcs: dict[HexStr, BaseRPC] = {}
    retries: int = 0
    id: int = 0

    model_config = ConfigDict(arbitrary_types_allowed=True)


_selected_transports: ContextVar["Transports"] = ContextVar(
    "_selected_transports",
    default=Transports(),
)


def _force_get_default_network() -> type[Network]:
    transport = _selected_transports.get()
    return transport.default


def _force_get_global_rpc(network: type[Network] | None = None) -> "RPC":
    from .rpc.core import RPC

    transport = _selected_transports.get()

    if not network:
        network = transport.default

    if network.id in transport.rpcs:
        return transport.rpcs[network.id]  # type: ignore
    transport.rpcs[network.id] = RPC(network=network)
    return transport.rpcs[network.id]  # type: ignore


def set_transport(networks: list[type[Network]], retries: int = 0):
    transport = _selected_transports.get()
    transport.default = networks[0]
    transport.networks = {network.id: network for network in networks}
    transport.retries = retries


def set_default_network(network: type[Network]):
    transport = _selected_transports.get()
    transport.default = network
    transport.networks[network.id] = network


def get_current_network() -> type[Network]:
    transport = _selected_transports.get()
    return transport.default


def set_rpc_timeout(timeout: float, network: type[Network] | None = None):
    rpc = _force_get_global_rpc(network)
    rpc.set_timeout(timeout)
