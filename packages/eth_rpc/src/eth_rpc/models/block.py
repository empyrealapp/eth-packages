import zlib
from datetime import datetime
from typing import Optional

from eth_rpc.types import HexInteger
from eth_typing import HexAddress, HexStr
from pydantic import Field, field_validator

from ..utils import BloomFilter, RPCModel, load_datetime_string
from .transaction import Transaction


class Block(RPCModel):
    number: HexInteger
    hash: Optional[HexStr] = None
    transactions: list[Transaction] | list[HexStr] = Field(default_factory=list)
    base_fee_per_gas: Optional[HexInteger] = None
    difficulty: HexInteger
    extra_data: HexStr
    gas_limit: HexInteger
    gas_used: HexInteger
    logs_bloom: HexStr
    miner: Optional[HexAddress] = None
    mix_hash: HexStr
    nonce: Optional[HexStr] = None
    parent_hash: HexStr
    receipts_root: HexStr
    sha3_uncles: HexStr
    size: HexInteger
    state_root: HexStr
    timestamp: datetime
    total_difficulty: Optional[HexInteger] = None
    transactions_root: HexStr
    uncles: list[HexStr] = Field(default_factory=list)

    normalize_timestamp = field_validator("timestamp", mode="before")(
        load_datetime_string
    )

    def has_log(self, topic: HexStr):
        t = bytes.fromhex(topic.replace("0x", ""))
        return t in BloomFilter(self.logs_bloom)

    def parent_block(self):
        return self.load_by_hash(self.parent_hash)

    def compress(self) -> bytes:
        return zlib.compress(self.model_dump_json().encode("utf-8"))

    def __repr__(self):
        return f"<Block number={self.number}>"

    __str__ = __repr__
