from typing import Optional

from eth_typing import HexStr
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from eth_rpc.types import HexInteger
from .access_list import AccessList


class BaseTransaction(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    hash: HexStr
    access_list: Optional[list[AccessList]] = None
    chain_id: Optional[HexInteger] = None
    from_: HexStr = Field(alias="from")
    gas: HexInteger
    gas_price: HexInteger
    max_fee_per_gas: Optional[HexInteger] = None
    max_priority_fee_per_gas: Optional[HexInteger] = None
    input: HexStr
    nonce: HexInteger
    r: HexStr
    s: HexStr
    v: HexInteger
    to: Optional[HexStr]
    type: Optional[HexInteger] = None
    value: HexInteger
    y_parity: HexInteger | None = None


class Transaction(BaseTransaction):
    block_hash: HexStr
    block_number: HexInteger
    transaction_index: HexInteger


class PendingTransaction(BaseTransaction):
    block_hash: HexStr | None = None  # not set on pending transactions
    block_number: HexInteger | None = None  # not set on pending transactions
    transaction_index: HexInteger | None = None  # not set on pending transactions
