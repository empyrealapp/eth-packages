from typing import TYPE_CHECKING, Literal

from eth_typing import HexAddress, ChecksumAddress
from pydantic import BaseModel, PrivateAttr

if TYPE_CHECKING:
    from ..synthetics_reader import MarketInfo


class MarketsLoader(BaseModel):
    network: Literal["arbitrum", "avalanche"] = "arbitrum"

    _info: dict[HexAddress, "MarketInfo"] | None = PrivateAttr(default=None)

    @property
    def info(self):
        return self._info

    async def load(self):
        from ..synthetics_reader import SyntheticsReader

        self._info = await SyntheticsReader(network=self.network).get_available_markets()

    def get_index_token_address(self, market_key: str) -> ChecksumAddress:
        return self.info[market_key].index_token_address

    def get_long_token_address(self, market_key: str) -> ChecksumAddress:
        return self.info[market_key].long_token_address

    def get_short_token_address(self, market_key: str) -> ChecksumAddress:
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
