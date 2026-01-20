import asyncio
import itertools
import time
from typing import TYPE_CHECKING, Generic, Optional, TypeVar

import httpx
from pydantic import BaseModel, ConfigDict, PrivateAttr

from eth_rpc.types import HexInt, HexStr
from btc_rpc._response import RPCResponse

if TYPE_CHECKING:
    from ..core import RPC

Params = TypeVar("Params", bound=BaseModel | HexInt | HexStr | list[HexInt | HexStr])
Response = TypeVar("Response")


class RPCMethodBase(BaseModel, Generic[Params, Response]):
    name: str
    client: Optional[httpx.AsyncClient] = None
    index: Optional[itertools.count] = None
    retries: int = 10
    _rpc: "RPC | None" = PrivateAttr(default=None)

    def set_rpc(self, rpc: "RPC") -> "RPCMethodBase":
        self._rpc = rpc
        return self

    def set_client(self, client: httpx.AsyncClient, index: itertools.count):
        self.client = client
        self.index = index

    def call_sync(self, *params: Params) -> Response:
        _, Output = self.__pydantic_generic_metadata__["args"]

        if not self._rpc:
            raise ValueError("RPC not set")

        payload = {
            "method": self.name,
            "id": next(self._rpc.index),
            "jsonrpc": "2.0",
        }
        if not params:
            payload["params"] = []
        elif isinstance(params[0], HexInt):
            payload["params"] = hex(params[0])
        elif isinstance(params[0], str) or isinstance(params[0], list):
            payload["params"] = params[0]
        elif isinstance(params[0], BaseModel):
            payload["params"] = list(params[0].model_dump().values()) if params else []
        else:
            raise TypeError(f"Invalid Input Type: {type(params[0])}")
        while True:
            tries = 0
            try:
                response = self._send_sync(self._rpc, payload)
                break
            except (httpx.ReadTimeout, httpx.ConnectTimeout) as exc:
                tries += 1
                time.sleep(1)
                if tries == self._rpc.retries:
                    raise exc
        if "error" in response and response["error"]:
            raise ValueError(response["error"]["message"])
        return RPCResponse[Output](**response).result  # type: ignore

    async def call_async(self, *params: Params):
        _, Output = self.__pydantic_generic_metadata__["args"]

        if not self._rpc:
            raise ValueError("RPC not set")

        payload = {
            "method": self.name,
            "id": next(self._rpc.index),
            "jsonrpc": "2.0",
        }
        if not params:
            payload["params"] = []
        elif isinstance(params[0], HexInt):
            payload["params"] = hex(params[0])
        elif isinstance(params[0], str) or isinstance(params[0], list):
            # this is a HexStr or list of Hex Strings
            payload["params"] = params[0]
        elif isinstance(params[0], BaseModel):
            payload["params"] = list(params[0].model_dump().values()) if params else []

        while True:
            tries = 0
            try:
                response = await self._send_async(self._rpc, payload)
                break
            except httpx.ReadTimeout as exc:
                tries += 1
                await asyncio.sleep(1)
                if tries == self._rpc.retries:
                    raise exc
        if "error" in response and response["error"]:
            raise ValueError(response["error"]["message"])
        return RPCResponse[Output](**response).result  # type: ignore

    @staticmethod
    def _send_sync(rpc: "RPC", payload: dict) -> dict:
        result = httpx.post(rpc.http, json=payload, timeout=rpc.timeout)
        return result.json()

    @staticmethod
    async def _send_async(rpc: "RPC", payload: dict) -> dict:
        result = await rpc.client.post(rpc.http, json=payload)
        return result.json()

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
