from typing import Awaitable, Callable, ClassVar, Generic, ParamSpec

from pydantic import BaseModel

from .base import Params, Response, RPCMethodBase

P = ParamSpec("P")


class Middleware(BaseModel):
    def update(self, method: "RPCMethod", make_request, params=None): ...


class RPCMethod(RPCMethodBase[Params, Response], Generic[Params, Response]):
    middlewares: ClassVar[list[Callable]] = []

    @classmethod
    def add_middleware(cls, middleware: Callable):
        cls.middlewares.append(middleware)

    def __call__(self, *params: Params) -> Awaitable[Response]:
        async def run():
            make_request = self.call_async
            for middleware in self.middlewares:
                make_request = middleware(self, make_request, is_async=True)
            return await make_request(*params)

        return run()

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
