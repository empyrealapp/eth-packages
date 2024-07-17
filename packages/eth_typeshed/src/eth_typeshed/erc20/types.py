from typing import Annotated

from eth_rpc.types import Indexed, Name, primitives
from eth_typing import HexAddress
from pydantic import BaseModel


class ApprovalEventType(BaseModel):
    owner: Annotated[primitives.address, Indexed]
    spender: Annotated[primitives.address, Indexed]
    value: primitives.uint256


class TransferEventType(BaseModel):
    sender: Annotated[primitives.address, Indexed]
    recipient: Annotated[primitives.address, Indexed]
    amount: primitives.uint256

    def is_mint(self):
        return int(self.sender, 16) == 0

    def is_burn(self):
        return int(self.recipient, 16) in (0, 0xDEAD)


class OwnerRequest(BaseModel):
    owner: Annotated[HexAddress, Name("owner")]


class OwnerSpenderRequest(OwnerRequest):
    spender: Annotated[HexAddress, Name("spender")]


class ApproveRequest(BaseModel):
    spender: primitives.address
    amount: primitives.uint256


class TransferRequest(BaseModel):
    recipient: primitives.address
    amount: primitives.uint256


class TransferFromRequest(BaseModel):
    owner: primitives.address
    recipient: primitives.address
    amount: primitives.uint256
