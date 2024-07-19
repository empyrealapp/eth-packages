from eth_rpc.types import BLOCK_STRINGS
from eth_typeshed.utils import try_execute_with_setters


class MultiCallRequestHelper:
    calls_with_setters: list
    data: dict

    def __init__(self):
        self.calls_with_setters = []
        self.data = {}

    def prepare(self, address, protocol_call_func, result_handler_func):
        self.prepare_raw(
            address,
            protocol_call_func,
            lambda result: result_handler_func(self.data[address], result),
        )

    def prepare_data(self, address, init_key, init_value):
        if address not in self.data:
            self.data[address] = {}
        if init_key not in self.data[address]:
            self.data[address][init_key] = init_value

    def prepare_raw(self, address, protocol_call_func, lambda_handler_func):
        if address not in self.data:
            self.data[address] = {}
        self.calls_with_setters.append((protocol_call_func, lambda_handler_func))

    async def call(self, block_number: int | BLOCK_STRINGS = "latest"):
        await try_execute_with_setters(
            self.calls_with_setters, block_number=block_number
        )
        return self.data
