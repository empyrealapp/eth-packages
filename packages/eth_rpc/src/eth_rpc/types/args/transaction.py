from eth_typing import HexStr
from pydantic import BaseModel

from eth_rpc.types import BlockReference, HexInteger


class TransactionRequest(BaseModel):
    tx_hash: HexStr


class GetTransactionByBlockHash(BaseModel):
    block_hash: HexStr
    index: HexInteger


class GetTransactionByBlockNumber(BaseModel):
    block_number: BlockReference
    index: HexInteger


class RawTransaction(BaseModel):
    signed_tx: HexStr
