from typing import Awaitable, Callable, ClassVar, Generic, ParamSpec, TypeVar

from eth_rpc.types import HexAddress, HexInt, NoArgs
from eth_typing import HexStr
from pydantic import BaseModel

from .base import RPCMethodBase

Params = TypeVar(
    "Params",
    bound=BaseModel
    | HexInt
    | HexStr
    | list[HexInt | HexStr]
    | list[HexAddress]
    | NoArgs,
)
Response = TypeVar("Response")
P = ParamSpec("P")


class Middleware(BaseModel):
    def update(self, method: "RPCMethod", make_request, params=None): ...


class RPCMethod(RPCMethodBase[Params, Response], Generic[Params, Response]):
    middlewares: ClassVar[list[Callable]] = []

    @classmethod
    def add_middleware(cls, middleware: Callable):
        cls.middlewares.append(middleware)

    def __call__(self, *params: Params) -> Awaitable[Response]:
        make_request = self.call_async
        for middleware in self.middlewares:
            make_request = middleware(self, make_request)
        return make_request(*params)

    @property
    def sync(self) -> Callable[..., Response]:
        make_request = self.call_sync

        for middleware in self.middlewares:
            make_request = middleware(self, make_request)

        return make_request


def add_middleware(middleware: list[Callable] | Callable):
    if not isinstance(middleware, list):
        middleware = [middleware]

    for elem in middleware:
        RPCMethod.add_middleware(elem)
