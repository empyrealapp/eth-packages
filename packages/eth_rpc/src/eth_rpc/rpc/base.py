import itertools

import httpx
from pydantic import BaseModel, ConfigDict, Field

from eth_rpc.types import Network


class BaseRPC(BaseModel):
    _timeout: float = 10.0
    _retries: int = 3

    network: Network

    index: itertools.count = Field(default_factory=lambda: itertools.count())
    client: httpx.AsyncClient = Field(default_factory=lambda: httpx.AsyncClient())

    @property
    def timeout(self) -> httpx.Timeout:
        """Request Timeout"""
        return httpx.Timeout(self._timeout)

    def set_timeout(self, timeout: float):
        self._timeout = timeout

    def set_retries(self, retries: int):
        self._retries = retries

    @property
    def retries(self):
        return self._retries

    @property
    def wss(self) -> str:
        if not (wss := self.network.wss):
            raise ValueError("wss not set")
        return str(wss)

    @property
    def http(self) -> str:
        if not (http := self.network.http):
            raise ValueError("http not set")
        return str(http)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )
