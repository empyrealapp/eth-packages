from typing import Optional

from eth_typing import HexAddress, HexStr
from pydantic import AnyHttpUrl, BaseModel, Field
from pydantic.networks import AnyWebsocketUrl, Url


class BlockExplorer(BaseModel):
    name: str
    url: str
    api_url: str
    api_key: str | None = None


class RpcUrl(BaseModel):
    http: AnyHttpUrl
    wss: Optional[AnyWebsocketUrl] = Field(default=None)


class Rpcs(BaseModel):
    default: RpcUrl
    backups: list[RpcUrl] = []


class Network(BaseModel):
    chain_id: int
    name: str
    native_currency: str
    rpc: Rpcs
    block_explorer: BlockExplorer
    alchemy_str: str | None = None
    multicall3: HexAddress | None = HexAddress(
        HexStr("0xca11bde05977b3631167028862be2a173976ca11")
    )
    ens_registry: HexAddress | None = HexAddress(
        HexStr("0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e")
    )
    ens_universal_resolver: HexAddress | None = HexAddress(
        HexStr("0xce01f8eee7E479C928F8919abD53E553a36CeF67")
    )
    apprx_block_time: float = 12.0

    def set(
        self,
        http: str | None = None,
        wss: str | None = None,
        api_key: str | None = None,
    ):
        if http:
            self.rpc.default.http = Url(http)
        if wss:
            self.rpc.default.wss = Url(wss)
        if api_key:
            self.block_explorer.api_key = api_key
        return self

    @property
    def http(self) -> str | None:
        if self.rpc.default.http:
            return str(self.rpc.default.http)
        return None

    @property
    def wss(self) -> str | None:
        if self.rpc.default.wss:
            return str(self.rpc.default.wss)
        return None

    def __hash__(self) -> int:
        return self.chain_id

    def __str__(self):
        return f"<Network: {self.name}>"

    __repr__ = __str__
