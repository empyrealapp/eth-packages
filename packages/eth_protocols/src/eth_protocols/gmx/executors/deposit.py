from typing import Literal

from eth_rpc import Block, PrivateKeyWallet
from eth_rpc.networks import Arbitrum, Avalanche
from eth_rpc.utils import to_checksum
from eth_typing import HexAddress, HexStr
from eth_typeshed.gmx.exchange_router import CreateDepositParams
from eth_typeshed.gmx.synthetics_reader import DepositAmountOutParams
from eth_typeshed.gmx.synthetics_reader.schemas import MarketProps, MarketUtilsMarketPrices, PriceProps
from eth_typeshed.gmx.synthetics_reader.enums import SwapPricingType
from hexbytes import HexBytes
from pydantic import BaseModel, Field, PrivateAttr

from ..loaders import MarketsLoader
from ..synthetics_reader import SyntheticsReader
from ..utils.gas import get_execution_fee
from ..types import MarketInfo
from ..exchange_router import ExchangeRouter
from ..utils import determine_swap_route, get_gas_limits
from ..datastore import Datastore
from .approve import check_if_approved


class Deposit(BaseModel):
    network: Literal["arbitrum", "avalanche"]
    market_key: str
    initial_long_token: HexAddress
    initial_short_token: HexAddress
    long_token_amount: int
    short_token_amount: int
    max_fee_per_gas: int | None = None
    debug_mode: bool = False
    execution_buffer: float = 1.1
    long_token_swap_path: list[str] = Field(default_factory=list)
    short_token_swap_path: list[str] = Field(default_factory=list)
    all_markets_info: dict[HexAddress, MarketInfo] | None = None

    _datastore: Datastore = PrivateAttr()
    _reader: SyntheticsReader = PrivateAttr()
    _exchange_router: ExchangeRouter = PrivateAttr()
    _market_loader: MarketsLoader = PrivateAttr()

    @property
    def network_type(self) -> type[Arbitrum] | type[Avalanche]:
        return Arbitrum if self.network == "arbitrum" else Avalanche

    def model_post_init(self, __context):
        super().model_post_init(__context)
        self._market_loader = MarketsLoader(network=self.network)
        self._exchange_router = ExchangeRouter(network=self.network)
        self._datastore = Datastore(network=self.network)

    async def load(self):
        if self.max_fee_per_gas is None:
            block = await Block.latest()
            self.max_fee_per_gas = block.base_fee_per_gas * 1.35
        await self._market_loader.load()
        self.all_markets_info = self._market_loader._info

    async def check_for_approval(self, wallet: PrivateKeyWallet):
        """
        Check for Approval

        """
        spender = self._reader._environment.synthetics_router

        if not self.max_fee_per_gas:
            await self.load()
        assert self.max_fee_per_gas

        if self.long_token_amount > 0:
            await check_if_approved(
                wallet,
                spender,
                self.initial_long_token,
                self.long_token_amount,
                self.max_fee_per_gas,
                approve=True,
            )

        if self.short_token_amount > 0:
            await check_if_approved(
                wallet,
                spender,
                self.initial_short_token,
                self.short_token_amount,
                self.max_fee_per_gas,
                approve=True,
            )

    async def _submit_transaction(
        self,
        wallet: PrivateKeyWallet,
        value: float,
        multicall_args: list[bytes],
    ) -> HexStr:
        tx_hash = await self._exchange_router.multicall(
            multicall_args,
            wallet=wallet,
            value=value,
            max_fee_per_gas=self.max_fee_per_gas,
        )
        return tx_hash

    async def create_deposit_order(self, wallet: PrivateKeyWallet):
        await self.check_for_approval(wallet)

        should_unwrap_native_token = True
        eth_zero_address = "0x0000000000000000000000000000000000000000"
        ui_ref_address = "0x0000000000000000000000000000000000000000"

        user_wallet_address = wallet.address
        eth_zero_address = to_checksum(eth_zero_address)
        ui_ref_address = to_checksum(ui_ref_address)

        # Minimum number of GM tokens we should expect
        min_market_tokens = await self._estimate_deposit()

        network = self.network_type
        base_fee_per_gas = (await Block[network].latest()).base_fee_per_gas  # type: ignore[valid-type]
        assert base_fee_per_gas, "base fee must be set"

        # Giving a 10% buffer here
        execution_fee = int(
            await get_execution_fee(
                self._datastore,
                await get_gas_limits(self._datastore, "deposit"),
                base_fee_per_gas,
            ) * self.execution_buffer
        )

        callback_gas_limit = 0

        # If we havent defined either long/short set it to market default
        self._check_initial_tokens()

        # build swap paths for long/short deposit
        self._determine_swap_paths()

        arguments = CreateDepositParams(
            receiver=user_wallet_address,
            callback_contract=eth_zero_address,
            ui_fee_receiver=ui_ref_address,
            market=self.market_key,
            initial_long_token=self.initial_long_token,
            initial_short_token=self.initial_short_token,
            long_token_swap_path=self.long_token_swap_path,
            short_token_swap_path=self.short_token_swap_path,
            min_market_tokens=min_market_tokens,
            should_unwrap_native_token=should_unwrap_native_token,
            execution_fee=execution_fee,
            callback_gas_limit=callback_gas_limit
        )

        multicall_args: list[bytes] = []
        wnt_amount = 0

        # Send long side of deposit if more than 0 tokens
        if self.long_token_amount > 0:
            if self.initial_long_token != "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1":
                multicall_args = multicall_args + [HexBytes(
                    self._send_tokens(
                        self.initial_long_token,
                        self.long_token_amount
                    )
                )]

            # If adding long side with native token append to wnt_amount
            else:
                wnt_amount = wnt_amount + self.long_token_amount

        # Send short side of deposit if more than 0 tokens
        if self.short_token_amount > 0:
            if self.initial_short_token != "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1":
                multicall_args = multicall_args + [HexBytes(
                    self._send_tokens(
                        self.initial_short_token,
                        self.short_token_amount
                    )
                )]

            # If adding short side with native token append to wnt_amount
            else:
                wnt_amount = wnt_amount + self.short_token_amount

        # Send wnt_amount, incl any deposit
        multicall_args = multicall_args + [HexBytes(
            self._send_wnt(
                int(wnt_amount + execution_fee)
            )
        )]

        # send our deposit parameters
        multicall_args = multicall_args + [HexBytes(
            self._create_order(
                arguments
            )
        )]

        await self._submit_transaction(
            wallet,
            int(wnt_amount + execution_fee),
            multicall_args,
        )

    def _check_initial_tokens(self):
        """
        Check if we need to set the long or short token address
        when depositing
        """

        if self.long_token_amount == 0:
            self.initial_long_token = self.all_markets_info[
                self.market_key
            ]['long_token_address']

        if self.short_token_amount == 0:
            self.initial_short_token = self.all_markets_info[
                self.market_key
            ]['short_token_address']

    def _determine_swap_paths(self):
        """
        Check the required markets we need to swap our tokens through
        to deposit on the long or short side
        """

        market = self.all_markets_info[self.market_key]

        if market['long_token_address'] != self.initial_long_token:

            self.long_token_swap_path, requires_multi_swap = determine_swap_route(
                self.all_markets_info,
                self.initial_long_token,
                market['long_token_address']
            )

        if market['short_token_address'] != self.initial_short_token:
            self.short_token_swap_path, requires_multi_swap = determine_swap_route(
                self.all_markets_info,
                self.initial_short_token,
                market['short_token_address']
            )

    def _create_order(self, args: CreateDepositParams):
        """
        Create Order
        """
        return self._exchange_router.encode_create_deposit(
            args,
        )

    def _send_tokens(self, token_address, amount):
        """
        Send tokens
        """
        return self._exchange_router.encode_send_tokens(
            token_address,
            '0xF89e77e8Dc11691C9e8757e84aaFbCD8A67d7A55',
            amount
        )

    def _send_wnt(self, amount):
        """
        Send WNT
        """
        return self._exchange_router.encode_send_wnt(amount)

    async def _estimate_deposit(self):
        """
        Given the amount of tokens we have to deposit, estimate
        the amount of GM we expect out

        Returns
        -------
        int
            amount of GM tokens.

        """
        data_store_contract_address = self._reader.datastore

        market = self.all_markets_info[self.market_key]
        oracle_prices_dict = await self._reader.get_recent_prices()

        index_token_address = market.index_token_address
        long_token_address = market.long_token_address
        short_token_address = market.short_token_address

        market_addresses = MarketProps(
            market_token=self.market_key,
            index_token=index_token_address,
            long_token=long_token_address,
            short_token=short_token_address,
        )
        prices = MarketUtilsMarketPrices(
            index_token_price=PriceProps(
                int(oracle_prices_dict[index_token_address]['minPriceFull']),
                int(oracle_prices_dict[index_token_address]['maxPriceFull'])
            ),
            long_token_price=PriceProps(
                int(oracle_prices_dict[long_token_address]['minPriceFull']),
                int(oracle_prices_dict[long_token_address]['maxPriceFull'])
            ),
            short_token_price=PriceProps(
                int(oracle_prices_dict[short_token_address]['minPriceFull']),
                int(oracle_prices_dict[short_token_address]['maxPriceFull'])
            )
        )

        parameters = DepositAmountOutParams(
            data_store=data_store_contract_address,
            market=market_addresses,
            prices=prices,
            long_token_amount=self.long_token_amount,
            short_token_amount=self.short_token_amount,
            ui_fee_receiver="0x0000000000000000000000000000000000000000",
            swap_pricing_type=SwapPricingType.Deposit,
            include_virtual_inventory_impact=True,
        )

        return await self._reader.get_estimated_deposit_amount_out(parameters)
