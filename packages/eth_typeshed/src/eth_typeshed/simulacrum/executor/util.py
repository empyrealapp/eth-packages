from eth_rpc import ContractFunc
from eth_rpc.networks import Base
from eth_rpc.wallet import PrivateKeyWallet
from eth_typing import HexAddress, HexStr

from .executor import ExecuteRequest, SimulacrumExecutor


class Executor:
    def __init__(
        self,
        simulacrum_wallet_address: HexAddress,
        executor_wallet: PrivateKeyWallet,
        simulacrum_executor: SimulacrumExecutor | None = None,
    ):
        self.simulacrum_wallet_address = simulacrum_wallet_address
        self.executor_wallet = executor_wallet
        self.simulacrum_executor = simulacrum_executor
        self.executor = simulacrum_executor or SimulacrumExecutor[Base](
            address=self.simulacrum_wallet_address
        )

    async def broadcast(
        self,
        contract_func: ContractFunc,
        value: int = 0,
        operation: int = 0,
        tx_gas: int = 100_000,
        executor_value: int = 0,
    ) -> HexStr:
        response_tx = await self.executor.execute(
            ExecuteRequest(
                to=contract_func.address,
                value=value,
                data=contract_func.encode(),
                operation=operation,
                txGas=tx_gas,
            )
        ).execute(wallet=self.executor_wallet, value=executor_value)
        return response_tx

    async def create(
        self,
        to_address: HexAddress,
        data: HexStr,
        value: int = 0,
        operation: int = 1,
        tx_gas: int = 100_000,
        executor_value: int = 0,
    ) -> HexStr:
        response_tx = await self.executor.execute(
            ExecuteRequest(
                to=to_address,
                value=value,
                data=bytes.fromhex(data[2:]),
                operation=operation,
                txGas=tx_gas,
            )
        ).execute(wallet=self.executor_wallet, value=executor_value)
        return response_tx
