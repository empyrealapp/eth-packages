from typing import TYPE_CHECKING

from eth_typing import HexStr
from pydantic import BaseModel

from btc_rpc._request import Request

if TYPE_CHECKING:
    from .chain import ChainInfo


class Network(BaseModel, Request):
    id: HexStr
    name: str
    http: str

    def set(self, *, http: str):
        self.http = http
        return self

    async def chain_info(self) -> "ChainInfo":
        return await self._rpc().get_chain_info()
