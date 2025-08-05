from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from . import HexInteger


class AuthorizationItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    chain_id: HexInteger
    address: HexAddress
    nonce: HexInteger
    y_parity: HexInteger
    r: HexStr
    s: HexStr


class SignedTransaction(BaseModel):
    raw_transaction: HexStr
    hash: HexStr
    r: int
    s: int
    v: int
