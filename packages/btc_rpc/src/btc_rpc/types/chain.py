from eth_typing import HexStr
from pydantic import BaseModel


class ChainInfo(BaseModel):
    chain: str
    blocks: int
    headers: int
    bestblockhash: HexStr
    difficulty: float
    time: int
    mediantime: int
    verificationprogress: float
    initialblockdownload: bool
    chainwork: HexStr
    size_on_disk: int
    pruned: bool
    warnings: str
