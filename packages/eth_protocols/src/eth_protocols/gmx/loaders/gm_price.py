from eth_typeshed.gmx.synthetics_reader.schemas import MarketProps, PriceProps, GetMarketTokenPriceResponse

from .data import DataLoader
from ..keys import (
    MAX_PNL_FACTOR_FOR_TRADERS, MAX_PNL_FACTOR_FOR_DEPOSITS,
    MAX_PNL_FACTOR_FOR_WITHDRAWALS
)


class GMPrices(DataLoader):
    async def get_price_withdraw(self):
        """
        Get GM price if withdrawing from LP
        """
        pnl_factor_type = MAX_PNL_FACTOR_FOR_WITHDRAWALS

        return await self._get_data_processing(pnl_factor_type)

    async def get_price_deposit(self):
        """
        Get GM price if depositing to LP
        """
        pnl_factor_type = MAX_PNL_FACTOR_FOR_DEPOSITS
        return await self._get_data_processing(pnl_factor_type)

    async def get_price_traders(self):
        """
        Get GM price if trading from LP
        """
        pnl_factor_type = MAX_PNL_FACTOR_FOR_TRADERS
        return await self._get_data_processing(pnl_factor_type)

    async def _get_data_processing(self, pnl_factor_type: bytes) -> dict[str, float]:
        output_list: list[GetMarketTokenPriceResponse] = []
        mapper: list[str] = []
        await self._filter_swap_markets()

        for market_key in self.markets.info:
            await self._get_token_addresses(market_key)
            index_token_address = self.markets.get_index_token_address(
                market_key
            )
            oracle_prices = await self._get_oracle_prices(
                index_token_address,
            )

            market = MarketProps(
                market_token=market_key,
                index_token=index_token_address,
                long_token=self._long_token_address,
                short_token=self._short_token_address
            )

            output = await self._make_market_token_price_query(
                market,
                oracle_prices.index_token_price,
                oracle_prices.long_token_price,
                oracle_prices.short_token_price,
                pnl_factor_type
            )

            # add the uncalled web3 object to list
            output_list.append(output)

            # add the market symbol to a list to use to map to dictionary later
            mapper.append(self.markets.get_market_symbol(market_key))

        for key, output in zip(mapper, output_list):
            # divide by 10**30 to turn into USD value
            self.output[key] = output.market_token_price / 10**30

        self.output['parameter'] = "gm_prices"
        del self.output["long"]
        del self.output["short"]

        return self.output

    async def _make_market_token_price_query(
            self,
            market: MarketProps,
            index_price_tuple: PriceProps,
            long_price_tuple: PriceProps,
            short_price_tuple: PriceProps,
            pnl_factor_type: bytes,
    ) -> GetMarketTokenPriceResponse:
        """
        Get the raw GM price from the reader contract for a given market tuple,
        index, long, and
        short max/min price tuples, and the pnl factor hash.

        Parameters
        ----------
        market : list
            list containing contract addresses of the market.
        index_price_tuple : tuple
            tuple of min and max prices.
        long_price_tuple : tuple
            tuple of min and max prices..
        short_price_tuple : tuple
            tuple of min and max prices..
        pnl_factor_type : hash
            descriptor for datastore.

        Returns
        -------
        output : TYPE
            DESCRIPTION.

        """
        # maximize to take max prices in calculation
        maximize = True
        output = await self._synthetics_reader.get_market_token_price(
            market,
            index_price_tuple,
            long_price_tuple,
            short_price_tuple,
            pnl_factor_type,
            maximize,
        )

        return output
