from typing import Generic, Optional, TypeVar

from eth_rpc.types import Network
from eth_rpc.utils import RPCModel
from pydantic import BaseModel, Field

T = TypeVar("T")


class RPCResponse(BaseModel, Generic[T]):
    jsonrpc: float
    id: int
    result: T
    network: Optional[type[Network]] = Field(None)

    def model_post_init(self, __context):
        if isinstance(self.result, RPCModel):
            self.result.set_network(self.network)
