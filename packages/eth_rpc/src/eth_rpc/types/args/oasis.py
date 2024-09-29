from eth_typing import HexStr
from pydantic import BaseModel


class OasisCalldataPublicKey(BaseModel):
    key: HexStr
    checksum: HexStr
    signature: HexStr
    epoch: int
