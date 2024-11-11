from typing import Annotated

from eth_rpc import ProtocolBase, ContractFunc
from eth_rpc.types import primitives, Name, Struct


class GlvShiftNumbers(Struct):
    market_token_amount: Annotated[primitives.uint256, Name("marketTokenAmount")]
    min_market_tokens: Annotated[primitives.uint256, Name("minMarketTokens")]
    updated_at_time: Annotated[primitives.uint256, Name("updatedAtTime")]


class GlvShiftAddresses(Struct):
    glv: primitives.address
    from_market: Annotated[primitives.address, Name("fromMarket")]
    to_market: Annotated[primitives.address, Name("toMarket")]


class GlvWithdrawalFlags(Struct):
    should_unwrap_native_token: Annotated[bool, Name("shouldUnwrapNativeToken")]


class GlvWithdrawalNumbers(Struct):
    glv_token_amount: Annotated[primitives.uint256, Name("glvTokenAmount")]
    min_long_token_amount: Annotated[primitives.uint256, Name("minLongTokenAmount")]
    min_short_token_amount: Annotated[primitives.uint256, Name("minShortTokenAmount")]
    updated_at_time: Annotated[primitives.uint256, Name("updatedAtTime")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]


class GlvWithdrawalAddresses(Struct):
    glv: primitives.address
    market: primitives.address
    account: primitives.address
    receiver: primitives.address
    callback_contract: Annotated[primitives.address, Name("callbackContract")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    long_token_swap_path: Annotated[list[primitives.address], Name("longTokenSwapPath")]
    short_token_swap_path: Annotated[list[primitives.address], Name("shortTokenSwapPath")]


class GlvDepositFlags(Struct):
    should_unwrap_native_token: Annotated[bool, Name("shouldUnwrapNativeToken")]
    is_market_token_deposit: Annotated[bool, Name("isMarketTokenDeposit")]


class GlvDepositNumbers(Struct):
    market_token_amount: Annotated[primitives.uint256, Name("marketTokenAmount")]
    initial_long_token_amount: Annotated[primitives.uint256, Name("initialLongTokenAmount")]
    initial_short_token_amount: Annotated[primitives.uint256, Name("initialShortTokenAmount")]
    min_glv_tokens: Annotated[primitives.uint256, Name("minGlvTokens")]
    updated_at_time: Annotated[primitives.uint256, Name("updatedAtTime")]
    execution_fee: Annotated[primitives.uint256, Name("executionFee")]
    callback_gas_limit: Annotated[primitives.uint256, Name("callbackGasLimit")]


class GlvDepositAddresses(Struct):
    glv: primitives.address
    account: primitives.address
    receiver: primitives.address
    callback_contract: Annotated[primitives.address, Name("callbackContract")]
    ui_fee_receiver: Annotated[primitives.address, Name("uiFeeReceiver")]
    market: primitives.address
    initial_long_token: Annotated[primitives.address, Name("initialLongToken")]
    initial_short_token: Annotated[primitives.address, Name("initialShortToken")]
    long_token_swap_path: Annotated[list[primitives.address], Name("longTokenSwapPath")]
    short_token_swap_path: Annotated[list[primitives.address], Name("shortTokenSwapPath")]


class PriceProps(Struct):
    min: primitives.uint256
    max: primitives.uint256


class GlvShiftProps(Struct):
    addresses: GlvShiftAddresses
    numbers: GlvShiftNumbers


class GlvProps(Struct):
    glv_token: Annotated[primitives.address, Name("glvToken")]
    long_token: Annotated[primitives.address, Name("longToken")]
    short_token: Annotated[primitives.address, Name("shortToken")]


class GlvReaderGlvInfo(Struct):
    glv: GlvProps
    markets: list[primitives.address]


class GlvWithdrawalProps(Struct):
    addresses: GlvWithdrawalAddresses
    numbers: GlvWithdrawalNumbers
    flags: GlvWithdrawalFlags


class GlvDepositProps(Struct):
    addresses: GlvDepositAddresses
    numbers: GlvDepositNumbers
    flags: GlvDepositFlags


class GLVReader(ProtocolBase):
    get_account_glv_deposits: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.uint256, primitives.uint256],
            list[GlvDepositProps]
        ],
        Name("getAccountGlvDeposits"),
    ]

    get_account_glv_withdrawals: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.uint256, primitives.uint256],
            list[GlvWithdrawalProps]
        ],
        Name("getAccountGlvWithdrawals"),
    ]

    get_glv: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address],
            GlvProps
        ],
        Name("getGlv"),
    ]

    get_glv_by_salt: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            GlvProps
        ],
        Name("getGlvBySalt"),
    ]

    get_glv_deposit: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            GlvDepositProps
        ],
        Name("getGlvDeposit"),
    ]

    get_glv_deposits: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.uint256, primitives.uint256],
            list[GlvDepositProps]
        ],
        Name("getGlvDeposits"),
    ]

    get_glv_info: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address],
            GlvReaderGlvInfo
        ],
        Name("getGlvInfo"),
    ]

    get_glv_info_list: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.uint256, primitives.uint256],
            list[GlvReaderGlvInfo]
        ],
        Name("getGlvInfoList"),
    ]

    get_glv_shift: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            GlvShiftProps
        ],
        Name("getGlvShift"),
    ]

    get_glv_shifts: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.uint256, primitives.uint256],
            list[GlvShiftProps]
        ],
        Name("getGlvShifts"),
    ]

    get_glv_token_price: Annotated[
        ContractFunc[
            tuple[primitives.address, list[primitives.address], list[PriceProps], PriceProps, PriceProps, primitives.address, bool],
            tuple[primitives.uint256, primitives.uint256, primitives.uint256]
        ],
        Name("getGlvTokenPrice"),
    ]

    get_glv_value: Annotated[
        ContractFunc[
            tuple[primitives.address, list[primitives.address], list[PriceProps], PriceProps, PriceProps, primitives.address, bool],
            primitives.uint256
        ],
        Name("getGlvValue"),
    ]

    get_glv_withdrawal: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.bytes32],
            GlvWithdrawalProps
        ],
        Name("getGlvWithdrawal"),
    ]

    get_glv_withdrawals: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.uint256, primitives.uint256],
            list[GlvWithdrawalProps]
        ],
        Name("getGlvWithdrawals"),
    ]

    get_glvs: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.uint256, primitives.uint256],
            list[GlvProps]
        ],
        Name("getGlvs"),
    ]
