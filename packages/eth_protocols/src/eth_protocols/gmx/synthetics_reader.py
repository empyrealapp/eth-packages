from typing import ClassVar, Literal

from pydantic import BaseModel, PrivateAttr

from eth_rpc.networks import Arbitrum, Avalanche
from eth_typeshed.gmx import SyntheticsReader as SyntheticsReaderContract, ExecutionPriceParams
from eth_typeshed.gmx.synthetics_reader.schemas import (
    DepositAmountOutParams,
    SwapAmountOutParams,
    SwapAmountOutResponse,
    WithdrawalAmountOutParams,
    WithdrawalAmountOutResponse,
)

PRECISION = 30

class ExecutionPriceResult(BaseModel):
    execution_price: float
    price_impact_usd: float


class SyntheticsReader(BaseModel):
    """
    SyntheticsReader contract
    """
    contract_addresses: ClassVar[dict[Literal["arbitrum", "avalanche"], str]] = {
        "arbitrum": "0x5Ca84c34a381434786738735265b9f3FD814b824",
        "avalanche": "0xBAD04dDcc5CC284A86493aFA75D2BEb970C72216"
    }

    network: Literal["arbitrum", "avalanche"]
    _contract: SyntheticsReaderContract = PrivateAttr()

    @property
    def network_type(self) -> type[Arbitrum] | type[Avalanche]:
        return Arbitrum if self.network == "arbitrum" else Avalanche

    def model_post_init(self, __context):
        contract_address = self.contract_addresses[self.network]
        self._contract = SyntheticsReaderContract[self.network_type](address=contract_address)

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
