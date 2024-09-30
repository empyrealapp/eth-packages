from eth_typing import HexStr
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ..basic import BLOCK_STRINGS, HexInteger


class GetBlockByHashArgs(BaseModel):
    block_hash: HexStr
    with_tx_data: bool = False


class BlockNumberArg(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
    block_number: HexInteger | BLOCK_STRINGS


class GetBlockByNumberArgs(BlockNumberArg):
    with_tx_data: bool = False
