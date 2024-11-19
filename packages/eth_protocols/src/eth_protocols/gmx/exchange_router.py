from typing import Literal

from eth_rpc import PrivateKeyWallet
from eth_rpc.networks import Arbitrum, Avalanche
from eth_typeshed.gmx import GMXEnvironment, ExchangeRouter as ExchangeRouterContract
from eth_typeshed.gmx.exchange_router import CreateDepositParams
from eth_typing import HexAddress
from pydantic import BaseModel, Field, PrivateAttr
from .loaders import MarketsLoader


class ExchangeRouter(BaseModel):
    network: Literal["arbitrum", "avalanche"] = Field(default="arbitrum")
    _environment: GMXEnvironment = PrivateAttr()
    _contract: ExchangeRouterContract

    @property
    def network_type(self) -> type[Arbitrum] | type[Avalanche]:
        return Arbitrum if self.network == "arbitrum" else Avalanche

    def model_post_init(self, __context):
        super().model_post_init(__context)

        self._environment = GMXEnvironment.get_environment(self.network)
        self._contract = ExchangeRouterContract[self.network_type](address=self._environment.exchange_router)

    async def load_markets(self):
        self.all_markets_info = MarketsLoader(network=self.network).get_available_markets()

    def encode_send_tokens(self, token_address: HexAddress, amount: int):
        return self._contract.send_tokens(
            token_address,
            '0xF89e77e8Dc11691C9e8757e84aaFbCD8A67d7A55',
            amount
        ).encode()

    def encode_send_wnt(self, amount: int):
        return self._contract.send_wnt(
            '0xF89e77e8Dc11691C9e8757e84aaFbCD8A67d7A55',
            amount
        ).encode()

    def encode_create_deposit(self, params: CreateDepositParams):
        return self._contract.create_deposit(
            params,
        ).encode()

    async def multicall(self, calls: list[bytes], wallet: PrivateKeyWallet, **kwargs):
        return await self._contract.multicall(
            calls,
        ).execute(wallet, **kwargs)
