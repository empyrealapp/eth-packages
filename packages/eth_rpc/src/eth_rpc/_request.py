from typing import TYPE_CHECKING

from eth_rpc.types.args import EthCallParams, TraceArgs

from .types import BlockReference
from .types.network import Network

if TYPE_CHECKING:
    from .rpc.core import RPC


class Request:
    _network: type[Network] | None = None  # type: ignore

    def __class_getitem__(cls, params):
        if issubclass(params, Network):
            cls._network = params
        return cls

    def __getitem__(self, params):
        if issubclass(params, Network):
            self._network = params
        return self

    def _rpc(self) -> "RPC":
        """
        This uses the default network, unless a network has been provided, then immediately unsets the network.
        This makes it safe for async code.
        """
        from ._transport import _force_get_global_rpc

        network = self._network
        # self._network = None
        response = _force_get_global_rpc(network)
        return response

    def _rpc_(self) -> "RPC":
        """
        This uses the default network, unless a network has been provided, then immediately unsets the network.
        This makes it safe for async code.
        """
        from ._transport import _force_get_global_rpc

        network = self._network
        self._network = None  # type: ignore
        response = _force_get_global_rpc(network)
        return response

    def _get_debug_tracecall(
        self, address, data, block_number: BlockReference = "latest"
    ):
        return self._rpc().debug_tracecall.sync(
            TraceArgs(
                params=EthCallParams(
                    to=address,
                    data=data,
                ),
                block_number=block_number,
            )
        )
