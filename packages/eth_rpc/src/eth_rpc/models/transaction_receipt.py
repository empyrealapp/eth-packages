from typing import Optional

from eth_rpc.types import HexInteger
from eth_rpc.utils import BloomFilter
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from .log import Log


class TransactionReceipt(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    transaction_hash: HexStr
    block_hash: HexStr
    block_number: HexInteger
    logs: list[Log]
    contract_address: Optional[HexStr]
    effective_gas_price: HexInteger
    cumulative_gas_used: HexInteger
    from_: HexAddress = Field(alias="from")
    gas_used: HexInteger
    logs_bloom: HexInteger
    status: Optional[HexInteger] = None
    to: Optional[HexAddress]
    transaction_index: HexInteger
    type: HexInteger

    def has_log(self, topic: HexStr):
        """Checks is a transaction has a topic in it"""
        t = bytes.fromhex(topic.replace("0x", ""))

        return t in BloomFilter(self.logs_bloom)
