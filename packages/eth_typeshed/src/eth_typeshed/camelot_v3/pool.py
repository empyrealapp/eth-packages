from decimal import Decimal
from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from eth_typing import HexAddress
from pydantic import BaseModel, Field, PrivateAttr

from ..erc20 import ERC20

Q192 = Decimal(2**192)


class GlobalState(BaseModel):
    price: primitives.uint160
    tick: primitives.int24
    fee_zto: primitives.uint16 = Field(serialization_alias="feeZto")
    fee_0tz: primitives.uint16 = Field(serialization_alias="feeOtz")
    timepoint_index: primitives.uint16 = Field(serialization_alias="timepointIndex")
    community_fee_token0: primitives.uint8 = Field(
        serialization_alias="communityFeeToken0"
    )
    community_fee_token1: primitives.uint8 = Field(
        serialization_alias="communityFeeToken1"
    )
    unlocked: bool


class CamelotV3Pool(ProtocolBase):
    _tick_spacing: int | None = PrivateAttr(None)
    _token0: ERC20 | None = PrivateAttr(None)
    _token1: ERC20 | None = PrivateAttr(None)

    fee: ContractFunc[NoArgs, primitives.uint24] = METHOD
    global_state: Annotated[ContractFunc[NoArgs, GlobalState], Name("globalState")] = (
        METHOD
    )
    token0: ContractFunc[NoArgs, HexAddress] = METHOD
    token1: ContractFunc[NoArgs, HexAddress] = METHOD

    async def get_price(self, token0: bool = True):
        global_state = await self.global_state().get()
        _token0 = await self.token0().get()
        _token1 = await self.token1().get()
        token0_decimals = await ERC20(address=_token0).decimals().get()
        token1_decimals = await ERC20(address=_token1).decimals().get()
        return self.sqrt_price_x96_to_token_prices(
            global_state.price,
            token0_decimals,
            token1_decimals,
            token0,
        )

    @staticmethod
    def sqrt_price_x96_to_token_prices(
        sqrt_price_x96: int,
        token0_decimals: int,
        token1_decimals: int,
        token0: bool = True,
    ) -> Decimal:
        num = Decimal(sqrt_price_x96 * sqrt_price_x96)
        price1 = (
            (num / Q192)
            * (Decimal(10) ** token0_decimals)
            / (Decimal(10) ** token1_decimals)
        )
        price0 = Decimal(1) / price1

        return price0 if token0 else price1

    def __repr__(self):
        return f"<Pool address={self.address}>"
