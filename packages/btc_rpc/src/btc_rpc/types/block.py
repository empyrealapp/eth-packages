from decimal import Decimal
from eth_typing import HexStr

from pydantic import BaseModel, Field, AliasChoices

from .transaction import Transaction


class Block(BaseModel):
    hash: HexStr
    confirmations: int
    height: int
    version: int
    version_hex: HexStr = Field(alias="versionHex")
    merkleroot: HexStr
    time: int
    mediantime: int
    nonce: int
    bits: HexStr
    difficulty: Decimal
    chainwork: str
    n_tx: int = Field(validation_alias=AliasChoices("ntx", "nTx"))
    previousblockhash: HexStr
    nextblockhash: HexStr | None = None
    strippedsize: int
    size: int
    weight: int
    txs: list[HexStr] | list[Transaction] = Field(alias="tx")
