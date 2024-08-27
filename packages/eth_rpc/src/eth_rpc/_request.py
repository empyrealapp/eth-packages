from copy import deepcopy
from inspect import isclass
from typing import TYPE_CHECKING, ClassVar

from eth_rpc.types.args import EthCallParams, TraceArgs
from pydantic import BaseModel, PrivateAttr

from ._transport import _force_get_global_rpc
from .types import BlockReference, Network

if TYPE_CHECKING:
    from .rpc.core import RPC


class Request(BaseModel):
    _network: ClassVar[type[Network] | None] = PrivateAttr(default=None)

    def model_post_init(self, __context):
        network = self.__class__._network
        object.__setattr__(self, "_network", network)
        # overwrite the .rpc() classmethod
        object.__setattr__(self, "rpc", self._rpc)

    def __class_getitem__(cls, params):
        if isclass(params) and issubclass(params, Network):
            cls._network = params
            return cls
        else:
            try:
                return super().__class_getitem__(params)
            except AttributeError:
                pass
        return cls

    def __getitem__(self, params):
        if isclass(params) and issubclass(params, Network):
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
        response = _force_get_global_rpc(self._network)
        return response

    @classmethod
    def rpc(cls) -> "RPC":
        """
        This uses the default network, unless a network has been provided
        """
        from ._transport import _force_get_global_rpc

        if cls._network is None:
            return _force_get_global_rpc()
        response = _force_get_global_rpc(cls._network)
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
