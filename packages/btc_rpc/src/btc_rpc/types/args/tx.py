from typing import Literal

from eth_typing import HexStr
from pydantic import BaseModel


class GetTxRequest(BaseModel):
    txid: HexStr
    verbose: Literal[0, 1, 2] = 0
    blockhash: HexStr | None = None


class RawTransactionRequest(BaseModel):
    raw_transaction: HexStr
