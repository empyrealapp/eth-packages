from typing import Literal

from pydantic import BaseModel, Field
from sol_rpc.utils import CamelModel
from .transaction import Transaction, TransactionMeta, Reward


class BlockConfiguration(CamelModel):
    encoding: str = "json"
    max_supported_transaction_version: int | None = Field(default=None)
    transaction_details: Literal["full", "accounts", "signatures", "none"] = Field(default="full")
    rewards: bool = False


class BlockArgs(CamelModel):
    number: int = Field(lt=int(2 ** 64 - 1))
    configuration: BlockConfiguration | None = None


class TransactionWithMeta(BaseModel):
    meta: TransactionMeta | None = None
    transaction: Transaction


class Block(CamelModel):
    block_height: int | None
    block_time: int | None
    blockhash: str
    parent_slot: int
    previous_blockhash: str
    signatures: list[str] | None = None
    rewards: list[Reward]
    transactions: list[TransactionWithMeta] | list[str]
