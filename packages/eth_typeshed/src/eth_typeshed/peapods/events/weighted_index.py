from typing import Annotated

from eth_rpc.event import Event
from eth_rpc.types import Indexed, primitives
from eth_typing import HexAddress
from pydantic import BaseModel


class BondType(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    token: Annotated[HexAddress, Indexed]
    amount_tokens_bonded: primitives.uint256
    amount_tokens_minted: primitives.uint256


class DebondType(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    amount_debonded: primitives.uint256


class AddLiquidityType(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    amount_tokens: primitives.uint256
    amount_DAI: primitives.uint256


class RemoveLiquidityType(BaseModel):
    wallet: Annotated[HexAddress, Indexed]
    amount_liquidity: primitives.uint256


class FlashLoanType(BaseModel):
    executor: Annotated[HexAddress, Indexed]
    recipient: Annotated[HexAddress, Indexed]
    token: HexAddress
    amount: primitives.uint256


class CreateType(BaseModel):
    new_idx: Annotated[HexAddress, Indexed]
    wallet: Annotated[HexAddress, Indexed]


CreateEvent = Event[CreateType](name="Create")
FlashLoanEvent = Event[FlashLoanType](name="FlashLoan")
AddLiquidityEvent = Event[AddLiquidityType](name="AddLiquidity")
RemoveLiquidityEvent = Event[RemoveLiquidityType](name="RemoveLiquidity")
BondEvent = Event[BondType](name="Bond")
DebondEvent = Event[DebondType](name="Debond")
