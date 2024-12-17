from typing import Literal

from sol_rpc.utils import CamelModel
from .transaction import Transaction, TransactionMeta


class GetTransactionParams(CamelModel):
    commitment: Literal["confirmed", "finalized"] = "finalized"
    max_supported_transaction_version: int | None = None
    encoding: Literal["json", "jsonParsed", "base64", "base58"] | None = None


class GetTransactionArgs(CamelModel):
    signature: str
    encoding: Literal["base58", "base64"] = "base58"


class GetTransactionResponse(CamelModel):
    slot: int
    transaction: str | Transaction
    block_time: int
    meta: TransactionMeta
    version: int | None = None
