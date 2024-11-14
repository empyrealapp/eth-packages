from typing import Annotated

from eth_rpc import ProtocolBase, ContractFunc
from eth_rpc.types import primitives, Name, Struct


class WithdrawalFlags(Struct):
    should_unwrap_native_token: Annotated[bool, Name("shouldUnwrapNativeToken")]


class WithdrawalNumbers(Struct):
    market_token_amount: Annotated[primitives.uint256, Name("marketTokenAmount")]
    min_long_token_amount: Annotated[primitives.uint256, Name("minLongTokenAmount")]
    min_short_token_amount: Annotated[primitives.uint256, Name("minShortTokenAmount")]
    updated_at_block: Annotated[primitives.uint256, Name("updatedAtBlock")]
    updated_at_time: Annotated[primitives.uint256, Name("updatedAtTime")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]


class WithdrawalAddresses(Struct):
    account: primitives.address
    receiver: primitives.address
    callback_contract: Annotated[primitives.address, Name("callbackContract")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    market: primitives.address
    long_token_swap_path: Annotated[list[primitives.address], Name("longTokenSwapPath")]
    short_token_swap_path: Annotated[list[primitives.address], Name("shortTokenSwapPath")]


class ShiftNumbers(Struct):
    market_token_amount: Annotated[primitives.uint256, Name("marketTokenAmount")]
    min_market_tokens: Annotated[primitives.uint256, Name("minMarketTokens")]
    updated_at_time: Annotated[primitives.uint256, Name("updatedAtTime")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]


class ShiftAddresses(Struct):
    account: primitives.address
    receiver: primitives.address
    callback_contract: Annotated[primitives.address, Name("callbackContract")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    from_market: Annotated[primitives.address, Name("fromMarket")]
    to_market: Annotated[primitives.address, Name("toMarket")]


class ReaderUtilsVirtualInventory(Struct):
    virtual_pool_amount_for_long_token: Annotated[primitives.uint256, Name("virtualPoolAmountForLongToken")]
    virtual_pool_amount_for_short_token: Annotated[primitives.uint256, Name("virtualPoolAmountForShortToken")]
    virtual_inventory_for_positions: Annotated[primitives.int256, Name("virtualInventoryForPositions")]


class MarketUtilsCollateralType(Struct):
    long_token: Annotated[primitives.uint256, Name("longToken")]
    short_token: Annotated[primitives.uint256, Name("shortToken")]


class MarketUtilsPositionType(Struct):
    long: Annotated[MarketUtilsCollateralType, Name("long")]
    short: Annotated[MarketUtilsCollateralType, Name("short")]


class MarketUtilsGetNextFundingAmountPerSizeResult(Struct):
    longs_pay_shorts: Annotated[bool, Name("longsPayShorts")]
    funding_factor_per_second: Annotated[primitives.uint256, Name("fundingFactorPerSecond")]
    next_saved_funding_factor_per_second: Annotated[primitives.int256, Name("nextSavedFundingFactorPerSecond")]
    funding_fee_amount_per_size_delta: Annotated[MarketUtilsPositionType, Name("fundingFeeAmountPerSizeDelta")]
    claimable_funding_amount_per_size_delta: Annotated[MarketUtilsPositionType, Name("claimableFundingAmountPerSizeDelta")]


class ReaderUtilsBaseFundingValues(Struct):
    funding_fee_amount_per_size: Annotated[MarketUtilsPositionType, Name("fundingFeeAmountPerSize")]
    claimable_funding_amount_per_size: Annotated[MarketUtilsPositionType, Name("claimableFundingAmountPerSize")]


class DepositFlags(Struct):
    should_unwrap_native_token: Annotated[bool, Name("shouldUnwrapNativeToken")]


class DepositNumbers(Struct):
    initial_long_token_amount: Annotated[primitives.uint256, Name("initialLongTokenAmount")]
    initial_short_token_amount: Annotated[primitives.uint256, Name("initialShortTokenAmount")]
    min_market_tokens: Annotated[primitives.uint256, Name("minMarketTokens")]
    updated_at_block: Annotated[primitives.uint256, Name("updatedAtBlock")]
    updated_at_time: Annotated[primitives.uint256, Name("updatedAtTime")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]


class DepositAddresses(Struct):
    account: primitives.address
    receiver: primitives.address
    callback_contract: Annotated[primitives.address, Name("callbackContract")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    market: primitives.address
    initial_long_token: Annotated[primitives.address, Name("initialLongToken")]
    initial_short_token: Annotated[primitives.address, Name("initialShortToken")]
    long_token_swap_path: Annotated[list[primitives.address], Name("longTokenSwapPath")]
    short_token_swap_path: Annotated[list[primitives.address], Name("shortTokenSwapPath")]


class PositionFlags(Struct):
    is_long: Annotated[bool, Name("isLong")]


class PositionNumbers(Struct):
    size_in_usd: Annotated[primitives.uint256, Name("sizeInUsd")]
    size_in_tokens: Annotated[primitives.uint256, Name("sizeInTokens")]
    collateral_amount: Annotated[primitives.uint256, Name("collateralAmount")]
    borrowing_factor: Annotated[primitives.uint256, Name("borrowingFactor")]
    funding_fee_amount_per_size: Annotated[primitives.uint256, Name("fundingFeeAmountPerSize")]
    long_token_claimable_funding_amount_per_size: Annotated[primitives.uint256, Name("longTokenClaimableFundingAmountPerSize")]
    short_token_claimable_funding_amount_per_size: Annotated[primitives.uint256, Name("shortTokenClaimableFundingAmountPerSize")]
    increased_at_block: Annotated[primitives.uint256, Name("increasedAtBlock")]
    decreased_at_block: Annotated[primitives.uint256, Name("decreasedAtBlock")]
    increased_at_time: Annotated[primitives.uint256, Name("increasedAtTime")]
    decreased_at_time: Annotated[primitives.uint256, Name("decreasedAtTime")]


class PositionAddresses(Struct):
    account: primitives.address
    market: primitives.address
    collateral_token: Annotated[primitives.address, Name("collateralToken")]


class PositionPricingUtilsPositionReferralFees(Struct):
    referral_code: primitives.bytes32
    affiliate: primitives.address 
    trader: primitives.address
    total_rebate_factor: Annotated[primitives.uint256, Name("totalRebateFactor")]
    affiliate_reward_factor: Annotated[primitives.uint256, Name("affiliateRewardFactor")]
    adjusted_affiliate_reward_factor: Annotated[primitives.uint256, Name("adjustedAffiliateRewardFactor")]
    trader_discount_factor: Annotated[primitives.uint256, Name("traderDiscountFactor")]
    total_rebate_amount: Annotated[primitives.uint256, Name("totalRebateAmount")]
    trader_discount_amount: Annotated[primitives.uint256, Name("traderDiscountAmount")]
    affiliate_reward_amount: Annotated[primitives.uint256, Name("affiliateRewardAmount")]


class PositionPricingUtilsPositionFundingFees(Struct):
    funding_fee_amount: Annotated[primitives.uint256, Name("fundingFeeAmount")]
    claimable_long_token_amount: Annotated[primitives.uint256, Name("claimableLongTokenAmount")]
    claimable_short_token_amount: Annotated[primitives.uint256, Name("claimableShortTokenAmount")]
    latest_funding_fee_amount_per_size: Annotated[primitives.uint256, Name("latestFundingFeeAmountPerSize")]
    latest_long_token_claimable_funding_amount_per_size: Annotated[primitives.uint256, Name("latestLongTokenClaimableFundingAmountPerSize")]
    latest_short_token_claimable_funding_amount_per_size: Annotated[primitives.uint256, Name("latestShortTokenClaimableFundingAmountPerSize")]


class PositionPricingUtilsPositionBorrowingFees(Struct):
    borrowing_fee_usd: Annotated[primitives.uint256, Name("borrowingFeeUsd")]
    borrowing_fee_amount: Annotated[primitives.uint256, Name("borrowingFeeAmount")]
    borrowing_fee_receiver_factor: Annotated[primitives.uint256, Name("borrowingFeeReceiverFactor")]
    borrowing_fee_amount_for_fee_receiver: Annotated[primitives.uint256, Name("borrowingFeeAmountForFeeReceiver")]


class PositionPricingUtilsPositionUiFees(Struct):
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    ui_fee_receiver_factor: Annotated[primitives.uint256, Name("uiFeeReceiverFactor")]
    ui_fee_amount: Annotated[primitives.uint256, Name("uiFeeAmount")]


class PriceProps(Struct):
    min: primitives.uint256
    max: primitives.uint256


class PositionPricingUtilsPositionFees(Struct):
    referral: PositionPricingUtilsPositionReferralFees
    funding: PositionPricingUtilsPositionFundingFees
    borrowing: PositionPricingUtilsPositionBorrowingFees
    ui: PositionPricingUtilsPositionUiFees
    collateral_token_price: Annotated[PriceProps, Name("collateralTokenPrice")]
    position_fee_factor: Annotated[primitives.uint256, Name("positionFeeFactor")]
    protocol_fee_amount: Annotated[primitives.uint256, Name("protocolFeeAmount")]
    position_fee_receiver_factor: Annotated[primitives.uint256, Name("positionFeeReceiverFactor")]
    fee_receiver_amount: Annotated[primitives.uint256, Name("feeReceiverAmount")]
    fee_amount_for_pool: Annotated[primitives.uint256, Name("feeAmountForPool")]
    position_fee_amount_for_pool: Annotated[primitives.uint256, Name("positionFeeAmountForPool")]
    position_fee_amount: Annotated[primitives.uint256, Name("positionFeeAmount")]
    total_cost_amount_excluding_funding: Annotated[primitives.uint256, Name("totalCostAmountExcludingFunding")]
    total_cost_amount: Annotated[primitives.uint256, Name("totalCostAmount")]


class OrderFlags(Struct):
    is_long: Annotated[bool, Name("isLong")]
    should_unwrap_native_token: Annotated[bool, Name("shouldUnwrapNativeToken")]
    is_frozen: Annotated[bool, Name("isFrozen")]
    auto_cancel: Annotated[bool, Name("autoCancel")]


class OrderNumbers(Struct):
    order_type: Annotated[primitives.uint8, Name("orderType")]
    decrease_position_swap_type: Annotated[primitives.uint8, Name("decreasePositionSwapType")]
    size_delta_usd: Annotated[primitives.uint256, Name("sizeDeltaUsd")]
    initial_collateral_delta_amount: Annotated[primitives.uint256, Name("initialCollateralDeltaAmount")]
    trigger_price: Annotated[primitives.uint256, Name("triggerPrice")]
    acceptable_price: Annotated[primitives.uint256, Name("acceptablePrice")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]
    min_output_amount: Annotated[primitives.uint256, Name("minOutputAmount")]
    updated_at_block: Annotated[primitives.uint256, Name("updatedAtBlock")]
    updated_at_time: Annotated[primitives.uint256, Name("updatedAtTime")]


class OrderAddresses(Struct):
    account: primitives.address
    receiver: primitives.address
    cancellation_receiver: Annotated[primitives.address, Name("cancellationReceiver")]
    callback_contract: Annotated[primitives.address, Name("callbackContract")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    market: primitives.address
    initial_collateral_token: Annotated[primitives.address, Name("initialCollateralToken")]
    swap_path: Annotated[list[primitives.address], Name("swapPath")]


class WithdrawalProps(Struct):
    addresses: WithdrawalAddresses
    numbers: WithdrawalNumbers
    flags: WithdrawalFlags


class SwapPricingUtilsSwapFees(Struct):
    fee_receiver_amount: Annotated[primitives.uint256, Name("feeReceiverAmount")]
    fee_amount_for_pool: Annotated[primitives.uint256, Name("feeAmountForPool")]
    amount_after_fees: Annotated[primitives.uint256, Name("amountAfterFees")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    ui_fee_receiver_factor: Annotated[primitives.uint256, Name("uiFeeReceiverFactor")]
    ui_fee_amount: Annotated[primitives.uint256, Name("uiFeeAmount")]


class ShiftProps(Struct):
    addresses: ShiftAddresses
    numbers: ShiftNumbers


class MarketPoolValueInfoProps(Struct):
    pool_value: Annotated[primitives.int256, Name("poolValue")]
    long_pnl: Annotated[primitives.int256, Name("longPnl")]
    short_pnl: Annotated[primitives.int256, Name("shortPnl")]
    net_pnl: Annotated[primitives.int256, Name("netPnl")]
    long_token_amount: Annotated[primitives.uint256, Name("longTokenAmount")]
    short_token_amount: Annotated[primitives.uint256, Name("shortTokenAmount")]
    long_token_usd: Annotated[primitives.uint256, Name("longTokenUsd")]
    short_token_usd: Annotated[primitives.uint256, Name("shortTokenUsd")]
    total_borrowing_fees: Annotated[primitives.uint256, Name("totalBorrowingFees")]
    borrowing_fee_pool_factor: Annotated[primitives.uint256, Name("borrowingFeePoolFactor")]
    impact_pool_amount: Annotated[primitives.uint256, Name("impactPoolAmount")]


class MarketProps(Struct):
    market_token: Annotated[primitives.address, Name("marketToken")]
    index_token: Annotated[primitives.address, Name("indexToken")]
    long_token: Annotated[primitives.address, Name("longToken")]
    short_token: Annotated[primitives.address, Name("shortToken")]


class ReaderUtilsMarketInfo(Struct):
    market: MarketProps
    borrowing_factor_per_second_for_longs: Annotated[primitives.uint256, Name("borrowingFactorPerSecondForLongs")]
    borrowing_factor_per_second_for_shorts: Annotated[primitives.uint256, Name("borrowingFactorPerSecondForShorts")]
    base_funding: Annotated[ReaderUtilsBaseFundingValues, Name("baseFunding")]
    next_funding: Annotated[MarketUtilsGetNextFundingAmountPerSizeResult, Name("nextFunding")]
    virtual_inventory: Annotated[ReaderUtilsVirtualInventory, Name("virtualInventory")]
    is_disabled: Annotated[bool, Name("isDisabled")]


class ReaderPricingUtilsExecutionPriceResult(Struct):
    price_impact_usd: Annotated[primitives.int256, Name("priceImpactUsd")]
    price_impact_diff_usd: Annotated[primitives.uint256, Name("priceImpactDiffUsd")]
    execution_price: Annotated[primitives.uint256, Name("executionPrice")]


class DepositProps(Struct):
    addresses: DepositAddresses
    numbers: DepositNumbers
    flags: DepositFlags


class MarketUtilsMarketPrices(Struct):
    index_token_price: Annotated[PriceProps, Name("indexTokenPrice")]
    long_token_price: Annotated[PriceProps, Name("longTokenPrice")]
    short_token_price: Annotated[PriceProps, Name("shortTokenPrice")]


class PositionProps(Struct):
    addresses: PositionAddresses
    numbers: PositionNumbers
    flags: PositionFlags


class ReaderUtilsPositionInfo(Struct):
    position: PositionProps
    fees: PositionPricingUtilsPositionFees
    execution_price_result: Annotated[
        ReaderPricingUtilsExecutionPriceResult,
        Name("executionPriceResult"),
    ]
    base_pnl_usd: Annotated[primitives.int256, Name("basePnlUsd")]
    uncapped_base_pnl_usd: Annotated[primitives.int256, Name("uncappedBasePnlUsd")]
    pnl_after_price_impact_usd: Annotated[primitives.int256, Name("pnlAfterPriceImpactUsd")]


class OrderProps(Struct):
    addresses: OrderAddresses
    numbers: OrderNumbers
    flags: OrderFlags


class SyntheticsReader(ProtocolBase):
    get_account_orders: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.uint256, primitives.uint256],
            list[OrderProps]
        ],
        Name("getAccountOrders"),
    ]

    get_account_position_info_list: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, list[primitives.bytes32], list[MarketUtilsMarketPrices], primitives.address],
            list[ReaderUtilsPositionInfo]
        ],
        Name("getAccountPositionInfoList"),
    ]

    get_account_positions: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.uint256, primitives.uint256],
            list[PositionProps]
        ],
        Name("getAccountPositions"),
    ]

    get_adl_state: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, bool, MarketUtilsMarketPrices],
            tuple[primitives.uint256, bool, primitives.int256, primitives.uint256]
        ],
        Name("getAdlState"),
    ]

    get_deposit: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            DepositProps
        ],
        Name("getDeposit"),
    ]

    get_deposit_amount_out: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, MarketUtilsMarketPrices, primitives.uint256, primitives.uint256, primitives.address, primitives.uint8, bool],
            primitives.uint256
        ],
        Name("getDepositAmountOut"),
    ]

    get_execution_price: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, PriceProps, primitives.uint256, primitives.uint256, primitives.int256, bool],
            ReaderPricingUtilsExecutionPriceResult
        ],
        Name("getExecutionPrice"),
    ]

    get_market: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address],
            MarketProps
        ],
        Name("getMarket"),
    ]

    get_market_by_salt: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            MarketProps
        ],
        Name("getMarketBySalt"),
    ]

    get_market_info: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketUtilsMarketPrices, primitives.address],
            ReaderUtilsMarketInfo
        ],
        Name("getMarketInfo"),
    ]

    get_market_info_list: Annotated[
        ContractFunc[
            tuple[primitives.address, list[MarketUtilsMarketPrices], primitives.uint256, primitives.uint256],
            list[ReaderUtilsMarketInfo]
        ],
        Name("getMarketInfoList"),
    ]

    get_market_token_price: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, PriceProps, PriceProps, PriceProps, primitives.bytes32, bool],
            tuple[primitives.int256, MarketPoolValueInfoProps]
        ],
        Name("getMarketTokenPrice"),
    ]

    get_markets: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.uint256, primitives.uint256],
            list[MarketProps]
        ],
        Name("getMarkets"),
    ]

    get_net_pnl: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, PriceProps, bool],
            primitives.int256
        ],
        Name("getNetPnl"),
    ]

    get_open_interest_with_pnl: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, PriceProps, bool, bool],
            primitives.int256
        ],
        Name("getOpenInterestWithPnl"),
    ]

    get_order: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            OrderProps
        ],
        Name("getOrder"),
    ]

    get_pnl: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, PriceProps, bool, bool],
            primitives.int256
        ],
        Name("getPnl"),
    ]

    get_pnl_to_pool_factor: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, MarketUtilsMarketPrices, bool, bool],
            primitives.int256
        ],
        Name("getPnlToPoolFactor"),
    ]

    get_position: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            PositionProps
        ],
        Name("getPosition"),
    ]

    get_position_info: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.bytes32, MarketUtilsMarketPrices, primitives.uint256, primitives.address, bool],
            ReaderUtilsPositionInfo
        ],
        Name("getPositionInfo"),
    ]

    get_position_pnl_usd: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, MarketUtilsMarketPrices, primitives.bytes32, primitives.uint256],
            tuple[primitives.int256, primitives.int256, primitives.uint256]
        ],
        Name("getPositionPnlUsd"),
    ]

    get_shift: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            ShiftProps
        ],
        Name("getShift"),
    ]

    get_swap_amount_out: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, MarketUtilsMarketPrices, primitives.address, primitives.uint256, primitives.address],
            tuple[primitives.uint256, primitives.int256, SwapPricingUtilsSwapFees]
        ],
        Name("getSwapAmountOut"),
    ]

    get_swap_price_impact: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.address, primitives.address, primitives.uint256, PriceProps, PriceProps],
            tuple[primitives.int256, primitives.int256, primitives.int256]
        ],
        Name("getSwapPriceImpact"),
    ]

    get_withdrawal: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            WithdrawalProps
        ],
        Name("getWithdrawal"),
    ]

    get_withdrawal_amount_out: Annotated[
        ContractFunc[
            tuple[primitives.address, MarketProps, MarketUtilsMarketPrices, primitives.uint256, primitives.address, primitives.uint8],
            tuple[primitives.uint256, primitives.uint256]
        ],
        Name("getWithdrawalAmountOut"),
    ]
