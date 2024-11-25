from abc import ABC, abstractmethod
from typing import Literal

from eth_rpc import Block, PrivateKeyWallet
from eth_rpc.utils import to_checksum
from eth_rpc.networks import Arbitrum, Avalanche
from eth_typing import ChecksumAddress, HexAddress, HexStr
from hexbytes import HexBytes
from pydantic import BaseModel, PrivateAttr

from eth_typeshed.gmx.synthetics_reader.enums import OrderType, DecreasePositionSwapType
from eth_typeshed.gmx.synthetics_reader.schemas import ExecutionPriceParams, PriceProps

from ..loaders import MarketsLoader
from ..synthetics_reader import PRECISION, SyntheticsReader
from ..types import OraclePrice, MarketInfo
from ..exchange_router import ExchangeRouter
from ..datastore import Datastore
from ..utils import get_execution_fee, get_gas_limits
from .approve import check_if_approved


class OrderT(ABC, BaseModel):
    network: Literal["arbitrum", "avalanche"]

    market_key: str
    collateral_address: HexAddress
    index_token_address: HexAddress
    is_long: bool
    size_delta: float
    initial_collateral_delta_amount: int
    slippage_percent: float
    swap_path: list[HexAddress]
    max_fee_per_gas: int | None = None
    debug_mode: bool = False
    auto_cancel: bool = False
    execution_buffer: float = 1.3

    _datastore: Datastore = PrivateAttr()
    _reader: SyntheticsReader = PrivateAttr()
    _exchange_router: ExchangeRouter = PrivateAttr()
    _market_loader: MarketsLoader = PrivateAttr()

    @abstractmethod
    async def estimated_swap_output(self, market: MarketInfo, token_in: HexAddress, amount_in: int) -> dict:
        pass

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
            block = await Block[self.network_type].latest()
            self.max_fee_per_gas = block['baseFeePerGas'] * 1.35
        self._is_swap = False

    @abstractmethod
    async def determine_gas_limits(self):
        pass

    async def check_for_approval(self, wallet: PrivateKeyWallet):
        """
        Check for Approval
        """
        spender = self._exchange_router._contract.address

        await check_if_approved(
            wallet,
            spender,
            self.collateral_address,
            self.initial_collateral_delta_amount,
            self.max_fee_per_gas,
            approve=True,
        )

    async def _submit_transaction(
        self,
        wallet: PrivateKeyWallet,
        multicall_args: list[bytes],
        **kwargs,
    ) -> HexStr:
        """
        Submit Transaction
        """
        tx_hash = await self._exchange_router.multicall(
            multicall_args,
            wallet,
            **kwargs,
        )
        return tx_hash

    def _get_prices(
        self,
        decimals: float,
        prices: dict,
        is_open: bool = False,
        is_close: bool = False,
        is_swap: bool = False,
    ):
        """
        Get Prices
        """
        price = sum(
            prices[self.index_token_address].max_price_full + prices[self.index_token_address].min_price_full
        ) / 2

        # Depending on if open/close & long/short, we need to account for
        # slippage in a different way
        if is_open:
            if self.is_long:
                slippage = str(
                    int(float(price) + float(price) * self.slippage_percent)
                )
            else:
                slippage = str(
                    int(float(price) - float(price) * self.slippage_percent)
                )
        elif is_close:
            if self.is_long:
                slippage = str(
                    int(float(price) - float(price) * self.slippage_percent)
                )
            else:
                slippage = str(
                    int(float(price) + float(price) * self.slippage_percent)
                )
        else:
            slippage = 0

        acceptable_price_in_usd = (
            int(slippage) * 10 ** (decimals - PRECISION)
        )

        return price, int(slippage), acceptable_price_in_usd

    async def order_builder(self, wallet: PrivateKeyWallet, is_open=False, is_close=False, is_swap=False) -> HexStr:
        """
        Create Order
        """

        await self.determine_gas_limits()
        await self.load()
        assert self.max_fee_per_gas, "max fee per gas must be set"

        execution_fee = int(
            await get_execution_fee(
                self._datastore,
                await get_gas_limits(self._datastore, "increase_order"),
                self.max_fee_per_gas,
            )
        )

        # Dont need to check approval when closing
        if not is_close and not self.debug_mode:
            await self.check_for_approval(wallet)

        execution_fee = int(execution_fee * self.execution_buffer)

        await self._market_loader.load()
        markets = await self._market_loader.info
        initial_collateral_delta_amount = self.initial_collateral_delta_amount
        prices: dict[ChecksumAddress, OraclePrice] = await self._reader.get_recent_prices()
        size_delta_price_price_impact = self.size_delta

        # when decreasing size delta must be negative
        if is_close:
            size_delta_price_price_impact = size_delta_price_price_impact * -1

        callback_gas_limit = 0
        min_output_amount = 0

        if is_open:
            order_type = OrderType.MarketIncrease
        elif is_close:
            order_type = OrderType.MarketDecrease
        elif is_swap:
            order_type = OrderType.MarketSwap

            # Estimate amount of token out using a reader function, necessary
            # for multi swap
            estimated_output = await self.estimated_swap_output(
                markets[self.swap_path[0]],
                self.collateral_address,
                initial_collateral_delta_amount
            )

            # this var will help to calculate the cost gas depending on the
            # operation
            self._get_limits_order_type = self._gas_limits['single_swap']
            if len(self.swap_path) > 1:
                estimated_output = self.estimated_swap_output(
                    markets[self.swap_path[1]],
                    "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
                    int(
                        estimated_output[
                            "out_token_amount"
                        ] - estimated_output[
                            "out_token_amount"
                        ] * self.slippage_percent
                    )
                )
                self._get_limits_order_type = self._gas_limits['swap_order']

            min_output_amount = estimated_output["out_token_amount"] - \
                estimated_output["out_token_amount"] * self.slippage_percent

        decrease_position_swap_type = DecreasePositionSwapType.NoSwap

        should_unwrap_native_token = True
        referral_code = HexBytes(
            "0x0000000000000000000000000000000000000000000000000000000000000000"
        )
        user_wallet_address = wallet.address
        eth_zero_address = "0x0000000000000000000000000000000000000000"
        ui_ref_address = "0x0000000000000000000000000000000000000000"
        try:
            gmx_market_address = to_checksum(self.market_key)
        except AttributeError:
            gmx_market_address = to_checksum(self.market_key)

        # parameters using to calculate execution price
        execution_price_parameters = ExecutionPriceParams(
            data_store=self._datastore._contract.address,
            market_key=self.market_key,
            index_token_price=PriceProps(
                max=int(prices[self.index_token_address].max_price_full),
                min=int(prices[self.index_token_address].min_price_full)
            ),
            position_size_in_usd=0,
            position_size_in_tokens=0,
            size_delta_usd=size_delta_price_price_impact,
            is_long=self.is_long
        )
        decimals = markets[self.market_key]['market_metadata']['decimals']

        price, acceptable_price, acceptable_price_in_usd = self._get_prices(
            decimals,
            prices,
            is_open,
            is_close,
            is_swap
        )

        mark_price = 0

        # mark price should be actual price when opening
        if is_open:
            mark_price = int(price)

        # Market address and acceptable price not important for swap
        if is_swap:
            acceptable_price = 0
            gmx_market_address = "0x0000000000000000000000000000000000000000"

        execution_price_and_price_impact_dict = await self._reader.get_execution_price(
            execution_price_parameters,
            decimals
        )

        # Prevent txn from being submitted if execution price falls outside acceptable
        if is_open:
            if self.is_long:
                if execution_price_and_price_impact_dict.execution_price > acceptable_price_in_usd:
                    raise Exception("Execution price falls outside acceptable price!")
            elif not self.is_long:
                if execution_price_and_price_impact_dict.execution_price < acceptable_price_in_usd:
                    raise Exception("Execution price falls outside acceptable price!")
        elif is_close:
            if self.is_long:
                if execution_price_and_price_impact_dict.execution_price < acceptable_price_in_usd:
                    raise Exception("Execution price falls outside acceptable price!")
            elif not self.is_long:
                if execution_price_and_price_impact_dict.execution_price > acceptable_price_in_usd:
                    raise Exception("Execution price falls outside acceptable price!")

        user_wallet_address = to_checksum(user_wallet_address)
        cancellation_receiver = user_wallet_address

        eth_zero_address = to_checksum(eth_zero_address)
        ui_ref_address = to_checksum(ui_ref_address)
        collateral_address = to_checksum(self.collateral_address)

        auto_cancel = self.auto_cancel

        arguments = (
            (
                user_wallet_address,
                cancellation_receiver,
                eth_zero_address,
                ui_ref_address,
                gmx_market_address,
                collateral_address,
                self.swap_path
            ),
            (
                self.size_delta,
                self.initial_collateral_delta_amount,
                mark_price,
                acceptable_price,
                execution_fee,
                callback_gas_limit,
                int(min_output_amount)
            ),
            order_type,
            decrease_position_swap_type,
            self.is_long,
            should_unwrap_native_token,
            auto_cancel,
            referral_code
        )

        # If the collateral is not native token (ie ETH/Arbitrum or AVAX/AVAX)
        # need to send tokens to vault

        value_amount = execution_fee
        if self.collateral_address != '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1' and not is_close:

            multicall_args = [
                HexBytes(self._send_wnt(value_amount)),
                HexBytes(
                    self._send_tokens(
                        self.collateral_address,
                        initial_collateral_delta_amount
                    )
                ),
                HexBytes(self._create_order(arguments))
            ]

        else:

            # send start token and execute fee if token is ETH or AVAX
            if is_open or is_swap:

                value_amount = initial_collateral_delta_amount + execution_fee

            multicall_args = [
                HexBytes(self._send_wnt(value_amount)),
                HexBytes(self._create_order(arguments))
            ]

        return await self._submit_transaction(
            wallet, value_amount, multicall_args, self._gas_limits
        )

    def _create_order(self, arguments):
        """
        Create Order
        """
        return self._exchange_router.encode_create_order(
            arguments,
        )

    def _send_tokens(self, amount):
        """
        Send tokens
        """
        return self._exchange_router.encode_send_tokens(
            self.collateral_address,
            "0x31eF83a530Fde1B38EE9A18093A333D8Bbbc40D5",
            amount
        )

    def _send_wnt(self, amount):
        """
        Send WNT
        """
        return self._exchange_router.encode_send_wnt(
            "0x31eF83a530Fde1B38EE9A18093A333D8Bbbc40D5",
            amount
        )
