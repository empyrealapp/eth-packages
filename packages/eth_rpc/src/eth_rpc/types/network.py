from typing import ClassVar, Optional

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
    http: ClassVar[str]
    wss: ClassVar[str]

    chain_id: ClassVar[int]
    name: ClassVar[str]
    native_currency: ClassVar[str]
    rpc: ClassVar[Rpcs]
    block_explorer: ClassVar[BlockExplorer]
    alchemy_str: ClassVar[str | None] = None
    multicall3: ClassVar[HexAddress | None] = HexAddress(
        HexStr("0xca11bde05977b3631167028862be2a173976ca11")
    )
    ens_registry: ClassVar[HexAddress | None] = HexAddress(
        HexStr("0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e")
    )
    ens_universal_resolver: ClassVar[HexAddress | None] = HexAddress(
        HexStr("0xce01f8eee7E479C928F8919abD53E553a36CeF67")
    )
    apprx_block_time: ClassVar[float] = 12.0

    @classmethod
    def set(
        cls,
        http: str | None = None,
        wss: str | None = None,
        api_key: str | None = None,
    ):
        if http:
            cls.rpc.default.http = Url(http)
            cls.http = str(cls.rpc.default.http)
        if wss:
            cls.rpc.default.wss = Url(wss)
            cls.wss = str(cls.rpc.default.wss)
        if api_key:
            cls.block_explorer.api_key = api_key
        return cls

    def __init_subclass__(cls, **kwargs):
        if cls.rpc.default.http:
            cls.http = cls.rpc.default.http
        if cls.rpc.default.wss:
            cls.wss = cls.rpc.default.wss

    def __hash__(self) -> int:
        return self.chain_id

    def __str__(self):
        return f"<Network: {self.name}>"

    __repr__ = __str__
