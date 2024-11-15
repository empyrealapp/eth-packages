from typing import Literal

from eth_typing import ChecksumAddress, HexAddress, HexStr
from pydantic import Field, PrivateAttr

from eth_rpc.networks import Arbitrum, Avalanche
from eth_rpc.types.primitives import address, uint256
from eth_rpc.utils import to_checksum
from eth_typeshed.gmx import MarketProps, GMXEnvironment, SyntheticsReader as SyntheticsReaderContract, ExecutionPriceParams, ReaderUtilsMarketInfo
from eth_typeshed.gmx.synthetics_reader.schemas import (
    DepositAmountOutParams,
    GetMarketsParams,
    GetMarketParams,
    GetOpenInterestParams,
    GetPnlParams,
    SwapAmountOutParams,
    SwapAmountOutResponse,
    WithdrawalAmountOutParams,
    WithdrawalAmountOutResponse,
)

from .extensions.oracle import PriceOracle
from .types import ExecutionPriceResult, MarketInfo
from .utils import TokenInfo, get_tokens_address_dict

PRECISION = 30


class SyntheticsReader(PriceOracle):
    network: Literal["arbitrum", "avalanche"] = Field(default="arbitrum")
    _environment: GMXEnvironment = PrivateAttr()
    _contract: SyntheticsReaderContract = PrivateAttr()

    @property
    def network_type(self) -> type[Arbitrum] | type[Avalanche]:
        return Arbitrum if self.network == "arbitrum" else Avalanche

    @property
    def datastore(self) -> HexAddress:
        return self._environment.datastore

    def model_post_init(self, __context):
        super().model_post_init(__context)

        self._environment = GMXEnvironment.get_environment(self.network)
        self._contract = SyntheticsReaderContract[self.network_type](address=self._environment.synthetics_reader)

    async def get_execution_price(self, params: ExecutionPriceParams, decimals: int = 18) -> ExecutionPriceResult:
        result = await self._contract.get_execution_price(params).get()

        return ExecutionPriceResult(
            execution_price=result.execution_price / 10**(PRECISION - decimals),
            price_impact_usd=result.price_impact_usd / 10**PRECISION
        )

    async def get_estimated_swap_output(self, params: SwapAmountOutParams) -> SwapAmountOutResponse:
        return await self._contract.get_swap_amount_out(params).get()

    async def get_estimated_deposit_amount_out(self, params: DepositAmountOutParams):
        return await self._contract.get_deposit_amount_out(params).get()

    async def get_estimated_withdrawal_amount_out(self, params: WithdrawalAmountOutParams) -> WithdrawalAmountOutResponse:
        return await self._contract.get_withdrawal_amount_out(params).get()

    async def get_available_markets(self) -> dict[ChecksumAddress, MarketInfo]:
        markets = await self._get_raw_markets()
        token_address_dict = await get_tokens_address_dict(self.network)
        decoded_markets: dict[ChecksumAddress, MarketInfo] = {}

        for market in markets:
            try:
                if not await self._check_if_index_token_in_signed_prices_api(
                    market.index_token
                ):
                    continue
                market_symbol = token_address_dict[to_checksum(market.index_token)].symbol

                if market.long_token == market.short_token:
                    market_symbol = f"{market_symbol}2"

                decoded_markets[to_checksum(market.market_token)] = MarketInfo(
                    gmx_market_address=market.market_token,
                    market_symbol=market_symbol,
                    index_token_address=market.index_token,
                    market_metadata=token_address_dict[to_checksum(market.index_token)],
                    long_token_metadata=token_address_dict[to_checksum(market.long_token)],
                    long_token_address=market.long_token,
                    short_token_metadata=token_address_dict[to_checksum(market.short_token)],
                    short_token_address=market.short_token
                )
                if market.market_token == HexAddress(HexStr("0x0Cf1fb4d1FF67A3D8Ca92c9d6643F8F9be8e03E5")):
                    decoded_markets[to_checksum(market.market_token)].market_symbol = "wstETH"
                    decoded_markets[to_checksum(market.market_token)].index_token_address = HexAddress(HexStr("0x5979D7b546E38E414F7E9822514be443A4800529"))

            # If KeyError it is because there is no market symbol and it is a swap market
            except KeyError:
                if not await self._check_if_index_token_in_signed_prices_api(
                    market.index_token
                ):
                    continue

                long_symbol = token_address_dict[to_checksum(market.long_token)].symbol
                short_symbol = token_address_dict[to_checksum(market.short_token)].symbol
                decoded_markets[to_checksum(market.market_token)] = MarketInfo(
                    gmx_market_address=market.market_token,
                    market_symbol=f'SWAP {long_symbol}-{short_symbol}',
                    index_token_address=market.index_token,
                    market_metadata=TokenInfo(
                        symbol=f'SWAP {long_symbol}-{short_symbol}',
                        address=market.market_token,
                        decimals=18,
                    ),
                    long_token_metadata=token_address_dict[to_checksum(market.long_token)],
                    long_token_address=market.long_token,
                    short_token_metadata=token_address_dict[to_checksum(market.short_token)],
                    short_token_address=market.short_token
                )
        return decoded_markets

    async def get_open_interest_with_pnl(self, params: GetOpenInterestParams) -> int:
        return await self._contract.get_open_interest_with_pnl(params).get()

    async def get_pnl(self, params: GetPnlParams) -> int:
        return await self._contract.get_pnl(params).get()

    async def get_market_info(self, params: GetMarketParams) -> ReaderUtilsMarketInfo:
        return await self._contract.get_market_info(params).get()

    # Private Methods

    async def _check_if_index_token_in_signed_prices_api(self, index_token_address: HexAddress | address) -> bool:
        if str(index_token_address) == "0x0000000000000000000000000000000000000000":
            return True
        prices = await self.get_recent_prices()
        return index_token_address in prices

    async def _get_raw_markets(self) -> list[MarketProps]:
        return await self._contract.get_markets(
            GetMarketsParams(
                data_store=self.datastore,
                start_index=uint256(0),
                end_index=uint256(35),
            )
        ).get()
