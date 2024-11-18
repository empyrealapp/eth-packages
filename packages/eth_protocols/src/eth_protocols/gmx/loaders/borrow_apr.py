from typing import Any

from eth_typeshed.gmx.synthetics_reader.types import ReaderUtilsMarketInfo

from .data import DataLoader


class GetBorrowAPR(DataLoader):
    async def _get_data_processing(self) -> dict[str, Any]:
        """
        Generate the dictionary of borrow APR data

        Returns
        -------
        funding_apr : dict
            dictionary of borrow data.

        """
        output_list: list[ReaderUtilsMarketInfo] = []
        mapper = []
        for market_key in self.markets.info:
            index_token_address = self.markets.get_index_token_address(
                market_key
            )

            await self._get_token_addresses(market_key)
            output = await self.get_market_info(
                market_key,
                index_token_address,
            )

            output_list.append(output)
            mapper.append(self.markets.get_market_symbol(market_key))

        for key, output in zip(mapper, output_list):
            self.output["long"][key] = (
                output.borrowing_factor_per_second_for_longs / 10 ** 28
            ) * 3600
            self.output["short"][key] = (
                output.borrowing_factor_per_second_for_shorts / 10 ** 28
            ) * 3600

        self.output['parameter'] = "borrow_apr"
        return self.output
