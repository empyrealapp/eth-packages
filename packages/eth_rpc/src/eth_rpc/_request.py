from copy import deepcopy
from typing import TYPE_CHECKING, ClassVar

from eth_rpc.types.args import EthCallParams, TraceArgs
from pydantic import BaseModel, PrivateAttr

from .types import BlockReference, Network

if TYPE_CHECKING:
    from .rpc.core import RPC


class Request(BaseModel):
    _network_: ClassVar[Network | None] = PrivateAttr(default=None)  # type: ignore
    _network: Network | None = PrivateAttr(default=None)  # type: ignore

    def model_post_init(self, __context):
        network = self.__class__._network_
        self._network = network

    def __class_getitem__(cls, params):
        if isinstance(params, Network):
            cls._network_ = params
        else:
            try:
                return super().__class_getitem__(params)
            except AttributeError:
                pass
        return cls

    def __getitem__(self, params):
        if isinstance(params, Network) and self._network != params:
            self = deepcopy(self)
            self._network = params
        return self

    def _rpc(self) -> "RPC":
        """
        This uses the default network, unless a network has been provided
        """
        from ._transport import _force_get_global_rpc

        network = self._network
        response = _force_get_global_rpc(network)
        return response

    def _get_debug_tracecall(
        self, address, data, block_number: BlockReference = "latest"
    ):
        return self._rpc().debug_tracecall(
            TraceArgs(
                params=EthCallParams(
                    to=address,
                    data=data,
                ),
                block_number=block_number,
            )
        )
