from eth_typing import HexStr
from pydantic import BaseModel


class SignedTransaction(BaseModel):
    raw_transaction: HexStr
    hash: HexStr
    r: int
    s: int
    v: int
