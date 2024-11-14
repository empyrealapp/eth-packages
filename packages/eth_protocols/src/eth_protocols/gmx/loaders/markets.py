from typing import TYPE_CHECKING, Literal

from eth_typing import HexAddress
from pydantic import BaseModel

from ..extensions.oracle import PriceOracle

if TYPE_CHECKING:
    from ..synthetics_reader import MarketInfo


class Markets(BaseModel):
    _info: dict[HexAddress, "MarketInfo"] | None = None
    network: Literal["arbitrum", "avalanche"] = "arbitrum"

    @property
    def info(self):
        return self._info

    async def load(self):
        from ..synthetics_reader import SyntheticsReader

        self._info = await SyntheticsReader(network=self.network).get_available_markets()

    def get_index_token_address(self, market_key: str) -> str:
        return self.info[market_key].index_token_address

    def get_long_token_address(self, market_key: str) -> str:
        return self.info[market_key].long_token_address

    def get_short_token_address(self, market_key: str) -> str:
        return self.info[market_key].short_token_address

    def get_market_symbol(self, market_key: str) -> str:
        return self.info[market_key].market_symbol

    def get_decimal_factor(
        self, market_key: HexAddress, long: bool = False, short: bool = False
    ) -> int:
        if long:
            return self.info[market_key].long_token_metadata.decimals
        elif short:
            return self.info[market_key].short_token_metadata.decimals
        else:
            return self.info[market_key].market_metadata.decimals

    def is_synthetic(self, market_key: str) -> bool:
        return self.info[market_key].market_metadata['synthetic']

    async def _check_if_index_token_in_signed_prices_api(self, index_token_address: HexAddress) -> bool:
        if index_token_address == "0x0000000000000000000000000000000000000000":
            return True
        prices = await PriceOracle(network=self.network).get_recent_prices()
        return index_token_address in prices
