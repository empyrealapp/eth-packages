from copy import deepcopy
from typing import TYPE_CHECKING, ClassVar, get_args, _LiteralGenericAlias  # type: ignore

from eth_rpc.types.args import EthCallParams, TraceArgs
from pydantic import BaseModel, PrivateAttr

from ._transport import _force_get_global_rpc
from .types import BlockReference, Network

if TYPE_CHECKING:
    from .rpc.core import RPC


class Request(BaseModel):
    _network: ClassVar[Network | None] = PrivateAttr(default=None)  # type: ignore

    def model_post_init(self, __context):
        network = self.__class__._network
        object.__setattr__(self, "_network", network)
        # overwrite the .rpc() classmethod
        object.__setattr__(self, "rpc", self._rpc)

    def __class_getitem__(cls, params):
        if isinstance(params, _LiteralGenericAlias):
            maybe_network = get_args(params)[0]
            if isinstance(maybe_network.value, Network):
                cls._network = params
                return cls
        else:
            try:
                return super().__class_getitem__(params)
            except AttributeError:
                pass
        return cls

    def __getitem__(self, params):
        if isinstance(params, _LiteralGenericAlias):
            maybe_network = get_args(params)[0]
            if isinstance(maybe_network.value, Network):
                if self._network != params:
                    self = deepcopy(self)
                    object.__setattr__(self, "_network", params)
        return self

    def _rpc(self) -> "RPC":
        """
        This uses the default network, unless a network has been provided
        """
        if self._network is None:
            return _force_get_global_rpc()
        network = get_args(self._network)[0].value
        response = _force_get_global_rpc(network)
        return response

    @classmethod
    def rpc(cls) -> "RPC":
        """
        This uses the default network, unless a network has been provided
        """
        from ._transport import _force_get_global_rpc

        if cls._network is None:
            return _force_get_global_rpc()
        network = get_args(cls._network)[0].value
        response = _force_get_global_rpc(network)
        return response

    def _get_debug_tracecall(
        self, address, data, block_number: BlockReference = "latest"
    ):
        return self.rpc().debug_tracecall(
            TraceArgs(
                params=EthCallParams(
                    to=address,
                    data=data,
                ),
                block_number=block_number,
            )
        )
