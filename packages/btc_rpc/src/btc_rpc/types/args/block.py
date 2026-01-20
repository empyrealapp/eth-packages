from typing import Literal

from eth_typing import HexStr
from pydantic import BaseModel


class GetBlockHashRequest(BaseModel):
    height: int


class GetBlockRequest(BaseModel):
    blockhash: HexStr | None = None
    verbose: Literal[0, 1, 2] = 0
