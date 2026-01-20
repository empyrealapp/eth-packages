from typing import TYPE_CHECKING, ClassVar, Optional

if TYPE_CHECKING:
    from .types import Network
    from .rpc.core import RPC

    NetworkType = type[Network]


class Request:
    _network: ClassVar[Optional["NetworkType"]] = None

    @classmethod
    def _rpc(cls) -> "RPC":
        """
        This uses the default network, unless a network has been provided, then immediately unsets the network.
        This makes it safe for async code.
        """
        from ._transport import _force_get_global_rpc

        network = cls._network
        cls._network = None
        response = _force_get_global_rpc(network)
        return response

    def _rpc_(self) -> "RPC":
        """
        This uses the default network, unless a network has been provided, then immediately unsets the network.
        This makes it safe for async code.
        """
        from ._transport import _force_get_global_rpc

        network = self._network
        self._network = None  # type: ignore[misc]
        response = _force_get_global_rpc(network)
        return response
