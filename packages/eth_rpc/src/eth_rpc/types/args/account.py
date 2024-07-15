from eth_typing import HexAddress
from pydantic import BaseModel

from ..basic import BlockReference


class GetAccountArgs(BaseModel):
    address: HexAddress
    block_number: BlockReference
