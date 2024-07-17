from eth_rpc.types import BLOCK_STRINGS
from eth_typeshed.multicall import multicall


async def try_execute_with_setters(
    calls_with_setters, block_number: int | BLOCK_STRINGS = "latest"
):
    if not block_number:
        block_number = "latest"
    calls = [call for call, _ in calls_with_setters]
    results = await multicall.try_execute(*calls, block_number=block_number)
    for result, setter in zip(results, calls_with_setters):
        _, set_result = setter
        if (
            result.success
            and result.result != "0x0000000000000000000000000000000000000000"
        ):
            set_result(result.result)
