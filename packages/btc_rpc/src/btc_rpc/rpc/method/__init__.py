from typing import Awaitable, Callable, Generic, TypeVar, ParamSpec

from eth_typing import HexStr
from pydantic import BaseModel

from eth_rpc.types import HexInt
from .base import RPCMethodBase

Params = TypeVar("Params", bound=BaseModel | HexInt | HexStr | list[HexInt | HexStr])
Response = TypeVar("Response")
P = ParamSpec("P")


class RPCMethod(RPCMethodBase[Params, Response], Generic[Params, Response]):
    def __call__(self, *params: Params) -> Awaitable[Response]:
        return self.call_async(*params)

    @property
    def sync(self) -> Callable[..., Response]:
        return self.call_sync
