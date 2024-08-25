from collections.abc import Coroutine
from typing import Any, Literal, overload

import httpx
from httpx import Response

from .dual_async import DualAsync, MaybeAwaitable, run


class HTTPClient(DualAsync):
    async def _request(self, method, url, *args, sync: bool, **kwargs):
        if sync:
            return httpx.request(method, url, *args, **kwargs)
        async with httpx.AsyncClient() as client:
            return await client.request(method, url, *args, **kwargs)

    # GET
    @overload
    def get(self, url, *args, sync: Literal[True], **kwargs) -> Response: ...

    @overload
    def get(
        self, url, *args, sync: Literal[False] = ..., **kwargs
    ) -> Coroutine[Any, Any, Response]: ...

    def get(self, url, *args, sync: bool = False, **kwargs) -> MaybeAwaitable[Response]:
        return run(self._request, "GET", url, *args, sync=sync, **kwargs)

    # PUT
    @overload
    def put(self, url, *args, sync: Literal[True], **kwargs) -> Response: ...

    @overload
    def put(
        self, url, *args, sync: Literal[False] = ..., **kwargs
    ) -> Coroutine[Any, Any, Response]: ...

    def put(self, url, *args, sync: bool = False, **kwargs) -> MaybeAwaitable[Response]:
        return run(self._request, "PUT", url, *args, sync=sync, **kwargs)

    # POST
    @overload
    def post(self, url, *args, sync: Literal[True], **kwargs) -> Response: ...

    @overload
    def post(
        self, url, *args, sync: Literal[False] = ..., **kwargs
    ) -> Coroutine[Any, Any, Response]: ...

    def post(
        self, url, *args, sync: bool = False, **kwargs
    ) -> MaybeAwaitable[Response]:
        return run(self._request, "POST", url, *args, sync=sync, **kwargs)

    # DELETE
    @overload
    def delete(self, url, *args, sync: Literal[True], **kwargs) -> Response: ...

    @overload
    def delete(
        self, url, *args, sync: Literal[False] = ..., **kwargs
    ) -> Coroutine[Any, Any, Response]: ...

    def delete(
        self, url, *args, sync: bool = False, **kwargs
    ) -> MaybeAwaitable[Response]:
        return run(self._request, "DELETE", url, *args, sync=sync, **kwargs)
