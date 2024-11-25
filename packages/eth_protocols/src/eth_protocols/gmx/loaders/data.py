from typing import Any, Literal

from eth_typing import HexAddress, ChecksumAddress
from pydantic import BaseModel, Field, PrivateAttr

from eth_rpc.utils import to_checksum
from eth_typeshed.gmx.synthetics_reader.types import ReaderUtilsMarketInfo, MarketUtilsMarketPrices
from eth_typeshed.gmx.synthetics_reader.schemas import (
    GetMarketParams,
    GetOpenInterestParams,
    GetPnlParams,
    MarketProps,
    PriceProps,
)
from .markets import MarketsLoader
from ..synthetics_reader import SyntheticsReader


class DataLoader(BaseModel):
    network: Literal["arbitrum", "avalanche"] = Field(default="arbitrum")
    filter_swap_markets: bool = Field(default=True)

    output: dict[str, Any] = {
        "long": {},
        "short": {}
    }
    _markets: MarketsLoader = PrivateAttr()
    _synthetics_reader: SyntheticsReader = PrivateAttr()
    _long_token_address: None | ChecksumAddress = PrivateAttr(default=None)
    _short_token_address: None | ChecksumAddress = PrivateAttr(default=None)

    @property
    def markets(self):
        return self._markets

    def model_post_init(self, __context):
        self._synthetics_reader = SyntheticsReader(network=self.network)
        self._markets = MarketsLoader(network=self.network)

    async def get_data(self):
        await self._markets.load()
        if self.filter_swap_markets:
            await self._filter_swap_markets()
        data = await self._get_data_processing()
        return data

    # @abstrctmethod
    # async def _get_data_processing(self, pnl_factor_type: bytes):
    #     pass

    async def _get_token_addresses(self, market_key: str):
        self._long_token_address = self._markets.get_long_token_address(market_key)
        self._short_token_address = self._markets.get_short_token_address(market_key)

    async def _filter_swap_markets(self):
        # TODO: Move to markets MAYBE
        for market_key in self.markets.info:
            market_symbol = self.markets.get_market_symbol(market_key)
            if 'SWAP' in market_symbol:
                # Remove swap markets from dict
                del self.markets.info[market_key]

    async def _get_pnl(
        self, market: MarketProps, prices_list: PriceProps, is_long: bool, maximize: bool = False,
    ) -> tuple[int, int]:
        open_interest_pnl = await self._synthetics_reader.get_open_interest_with_pnl(
            GetOpenInterestParams(
                data_store=self._synthetics_reader.datastore,
                market=market,
                index_token_price=prices_list,
                is_long=is_long,
                maximize=maximize
            )
        )

        pnl = await self._synthetics_reader.get_pnl(
            GetPnlParams(
                data_store=self._synthetics_reader.datastore,
                market=market,
                index_token_price=prices_list,
                is_long=is_long,
                maximize=maximize
            )
        )

        return open_interest_pnl, pnl

    async def _get_oracle_prices(
        self,
        index_token_address: HexAddress,
    ) -> MarketUtilsMarketPrices:
        oracle_prices_dict = await self._synthetics_reader.get_recent_prices()
        index_token: ChecksumAddress = to_checksum(index_token_address)

        assert self._long_token_address is not None
        assert self._short_token_address is not None

        try:
            prices = MarketUtilsMarketPrices(
                index_token_price=PriceProps(
                    min=oracle_prices_dict[index_token].min_price_full,
                    max=oracle_prices_dict[index_token].max_price_full
                ),
                long_token_price=PriceProps(
                    min=oracle_prices_dict[self._long_token_address].min_price_full,
                    max=oracle_prices_dict[self._long_token_address].max_price_full
                ),
                short_token_price=PriceProps(
                    min=oracle_prices_dict[self._short_token_address].min_price_full,
                    max=oracle_prices_dict[self._short_token_address].max_price_full
                )
            )

        # TODO - this needs to be here until GMX add stables to signed price API
        except KeyError:
            prices = MarketUtilsMarketPrices(
                index_token_price=PriceProps(
                    min=oracle_prices_dict[index_token].min_price_full,
                    max=oracle_prices_dict[index_token].max_price_full
                ),
                long_token_price=PriceProps(
                    min=oracle_prices_dict[self._long_token_address].min_price_full,
                    max=oracle_prices_dict[self._long_token_address].max_price_full
                ),
                short_token_price=PriceProps(
                    min=int(1000000000000000000000000),
                    max=int(1000000000000000000000000),
                ),
            )
        return prices

    async def get_market_info(self, market_key: str, index_token_address: HexAddress) -> ReaderUtilsMarketInfo:
        prices = await self._get_oracle_prices(index_token_address)
        return await self._synthetics_reader.get_market_info(
            GetMarketParams(
                data_store=self._synthetics_reader.datastore,
                prices=prices,
                market_key=market_key,
            ),
        )
