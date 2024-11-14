from .gmx_utils import create_hash_string, create_hash, get_datastore_contract

ACCOUNT_POSITION_LIST = create_hash_string("ACCOUNT_POSITION_LIST")
CLAIMABLE_FEE_AMOUNT = create_hash_string("CLAIMABLE_FEE_AMOUNT")
DECREASE_ORDER_GAS_LIMIT = create_hash_string("DECREASE_ORDER_GAS_LIMIT")
DEPOSIT_GAS_LIMIT = create_hash_string("DEPOSIT_GAS_LIMIT")

WITHDRAWAL_GAS_LIMIT = create_hash_string("WITHDRAWAL_GAS_LIMIT")

EXECUTION_GAS_FEE_BASE_AMOUNT = create_hash_string("EXECUTION_GAS_FEE_BASE_AMOUNT")
EXECUTION_GAS_FEE_MULTIPLIER_FACTOR = create_hash_string(
    "EXECUTION_GAS_FEE_MULTIPLIER_FACTOR")
INCREASE_ORDER_GAS_LIMIT = create_hash_string("INCREASE_ORDER_GAS_LIMIT")
MAX_OPEN_INTEREST = create_hash_string("MAX_OPEN_INTEREST")
MAX_POSITION_IMPACT_FACTOR_FOR_LIQUIDATIONS_KEY = create_hash_string(
    "MAX_POSITION_IMPACT_FACTOR_FOR_LIQUIDATIONS"
)
MAX_PNL_FACTOR_FOR_TRADERS = create_hash_string("MAX_PNL_FACTOR_FOR_TRADERS")
MAX_PNL_FACTOR_FOR_DEPOSITS = create_hash_string("MAX_PNL_FACTOR_FOR_DEPOSITS")
MAX_PNL_FACTOR_FOR_WITHDRAWALS = create_hash_string("MAX_PNL_FACTOR_FOR_WITHDRAWALS")
MIN_ADDITIONAL_GAS_FOR_EXECUTION = create_hash_string("MIN_ADDITIONAL_GAS_FOR_EXECUTION")
MIN_COLLATERAL_USD = create_hash_string("MIN_COLLATERAL_USD")
MIN_COLLATERAL_FACTOR_KEY = create_hash_string("MIN_COLLATERAL_FACTOR")
MIN_POSITION_SIZE_USD = create_hash_string("MIN_POSITION_SIZE_USD")
OPEN_INTEREST_IN_TOKENS = create_hash_string("OPEN_INTEREST_IN_TOKENS")
OPEN_INTEREST = create_hash_string("OPEN_INTEREST")
OPEN_INTEREST_RESERVE_FACTOR = create_hash_string(
    "OPEN_INTEREST_RESERVE_FACTOR"
)
POOL_AMOUNT = create_hash_string("POOL_AMOUNT")
RESERVE_FACTOR = create_hash_string("RESERVE_FACTOR")
SINGLE_SWAP_GAS_LIMIT = create_hash_string("SINGLE_SWAP_GAS_LIMIT")
SWAP_ORDER_GAS_LIMIT = create_hash_string("SWAP_ORDER_GAS_LIMIT")
VIRTUAL_TOKEN_ID = create_hash_string("VIRTUAL_TOKEN_ID")


def accountPositionListKey(account):
    return create_hash(
        ["bytes32", "address"],
        [ACCOUNT_POSITION_LIST, account]
    )


def claimable_fee_amount_key(market: str, token: str):
    return create_hash(
        ["bytes32", "address", "address"],
        [CLAIMABLE_FEE_AMOUNT, market, token]
    )


def decrease_order_gas_limit_key():
    return DECREASE_ORDER_GAS_LIMIT


def deposit_gas_limit_key():
    return DEPOSIT_GAS_LIMIT


def execution_gas_fee_base_amount_key():
    return EXECUTION_GAS_FEE_BASE_AMOUNT


def execution_gas_fee_multiplier_key():
    return EXECUTION_GAS_FEE_MULTIPLIER_FACTOR


def increase_order_gas_limit_key():
    return INCREASE_ORDER_GAS_LIMIT


def min_additional_gas_for_execution_key():
    return MIN_ADDITIONAL_GAS_FOR_EXECUTION


def min_collateral():
    return MIN_COLLATERAL_USD


def min_collateral_factor_key(market):
    return create_hash(["bytes32", "address"], [MIN_COLLATERAL_FACTOR_KEY, market])


def max_open_interest_key(market: str,
                          is_long: bool):

    return create_hash(
        ["bytes32", "address", "bool"],
        [MAX_OPEN_INTEREST, market, is_long]
    )


def max_position_impact_factor_for_liquidations_key(market):
    return create_hash(["bytes32", "address"],
                       [MAX_POSITION_IMPACT_FACTOR_FOR_LIQUIDATIONS_KEY, market])


def open_interest_in_tokens_key(
    market: str,
    collateral_token: str,
    is_long: bool
):
    return create_hash(
        ["bytes32", "address", "address", "bool"],
        [OPEN_INTEREST_IN_TOKENS, market, collateral_token, is_long]
    )


def open_interest_key(
    market: str,
    collateral_token: str,
    is_long: bool
):
    return create_hash(
        ["bytes32", "address", "address", "bool"],
        [OPEN_INTEREST, market, collateral_token, is_long]
    )


def open_interest_reserve_factor_key(
    market: str,
    is_long: bool
):
    return create_hash(
        ["bytes32", "address", "bool"],
        [OPEN_INTEREST_RESERVE_FACTOR, market, is_long]
    )


def pool_amount_key(
    market: str,
    token: str
):
    return create_hash(
        ["bytes32", "address", "address"],
        [POOL_AMOUNT, market, token]
    )


def reserve_factor_key(
    market: str,
    is_long: bool
):
    return create_hash(
        ["bytes32", "address", "bool"],
        [RESERVE_FACTOR, market, is_long]
    )


def single_swap_gas_limit_key():
    return SINGLE_SWAP_GAS_LIMIT


def swap_order_gas_limit_key():
    return SWAP_ORDER_GAS_LIMIT


def virtualTokenIdKey(token: str):
    return create_hash(["bytes32", "address"], [VIRTUAL_TOKEN_ID, token])


def withdraw_gas_limit_key():
    return WITHDRAWAL_GAS_LIMIT


if __name__ == "__main__":
    # market = '0x70d95587d40A2caf56bd97485aB3Eec10Bee6336'
    # token = '0x82aF49447D8a07e3bd95BD0d56f35241523fBab1'
    # token = '0xaf88d065e77c8cC2239327C5EDb3A432268e5831'

    token = "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1"

    hash_data = virtualTokenIdKey(token)
