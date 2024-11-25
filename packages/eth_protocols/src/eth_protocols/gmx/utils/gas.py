from typing import Literal

from ..datastore import Datastore
from ..keys import (
    decrease_order_gas_limit_key, increase_order_gas_limit_key,
    execution_gas_fee_base_amount_key, execution_gas_fee_multiplier_key,
    single_swap_gas_limit_key, swap_order_gas_limit_key, deposit_gas_limit_key,
    withdraw_gas_limit_key
)
from . import apply_factor


async def get_execution_fee(datastore: Datastore, estimated_gas_limit: int, gas_price: int) -> float:
    """
    Given a dictionary of gas_limits, the uncalled datastore object of a given operation, and the
    latest gas price, calculate the minimum execution fee required to perform an action

    Parameters
    ----------
    gas_limits : dict
        dictionary of uncalled datastore limit obkects.
    estimated_gas_limit : datastore_object
        the uncalled datastore object specific to operation that will be undertaken.
    gas_price : int
        latest gas price.

    """

    base_gas_limit = await datastore.get_uint(execution_gas_fee_base_amount_key())
    multiplier_factor = await datastore.get_uint(execution_gas_fee_multiplier_key())
    adjusted_gas_limit = base_gas_limit + apply_factor(estimated_gas_limit, multiplier_factor)

    return adjusted_gas_limit * gas_price


async def get_gas_limits(
    datastore: Datastore,
    name: Literal[
        "deposit", "withdraw", "single_swap", "swap_order", "increase_order",
        "decrease_order", "estimated_fee_base_gas_limit", "estimated_fee_multiplier_factor"
    ],
) -> int:
    """
    Given a Web3 contract object of the datstore, return a dictionary with the uncalled gas limits
    that correspond to various operations that will require the execution fee to calculated for.

    Parameters
    ----------
    datastore_object : web3 object
        contract connection.
    """
    gas_limits: dict[str, int] = {
        "deposit": datastore.get_uint(deposit_gas_limit_key()),
        "withdraw": datastore.get_uint(withdraw_gas_limit_key()),
        "single_swap": datastore.get_uint(single_swap_gas_limit_key()),
        "swap_order": datastore.get_uint(swap_order_gas_limit_key()),
        "increase_order": datastore.get_uint(increase_order_gas_limit_key()),
        "decrease_order": datastore.get_uint(decrease_order_gas_limit_key()),
        "estimated_fee_base_gas_limit": datastore.get_uint(
            execution_gas_fee_base_amount_key()),
        "estimated_fee_multiplier_factor": datastore.get_uint(
            execution_gas_fee_multiplier_key())
    }

    return await gas_limits[name]
