from asyncio import iscoroutine
from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Any, TypeVar, cast

if TYPE_CHECKING:
    from eth_rpc.types import MaybeAwaitable

T = TypeVar("T")


async def handle_maybe_awaitable(t: "MaybeAwaitable[T]") -> T:
    if iscoroutine(t):
        return await t
    else:
        return cast(T, t)


def run(
    corofunc: Callable[..., Coroutine[Any, Any, T]], *args, sync: bool = False, **kwargs
) -> T | Coroutine[Any, Any, T]:
    if sync:
        try:
            next(corofunc(*args, sync=sync, **kwargs).__await__())
        except StopIteration as ex:
            return ex.value
        raise RuntimeError("Not a sync execution")
    return corofunc(*args, sync=sync, **kwargs)


class DualAsync:
    @staticmethod
    def dual(method, sync: bool = False):
        def _method(self: "DualAsync", *args, **kwargs):
            return method(self, *args, is_async=not sync, **kwargs)

        return _method
