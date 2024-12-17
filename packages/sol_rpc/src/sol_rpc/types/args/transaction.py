from typing import Literal

from pydantic import BaseModel
from sol_rpc.utils import CamelModel


class MessageHeader(CamelModel):
    num_readonly_signed_accounts: int
    num_readonly_unsigned_accounts: int
    num_required_signatures: int


class Instruction(CamelModel):
    accounts: list[int]
    data: str
    program_id_index: int


class Message(CamelModel):
    account_keys: list[str]
    header: MessageHeader
    instructions: list[Instruction]
    recent_blockhash: str


class Transaction(BaseModel):
    message: Message
    signatures: list[str]
    version: int | None = None


class Reward(CamelModel):
    pubkey: str
    lamports: int
    post_balance: int
    reward_type: Literal["fee", "rent", "voting", "staking"] | None = None
    commission: int | None = None


class LoadedAddresses(BaseModel):
    writable: list[str]
    readonly: list[str]


class ReturnData(BaseModel):
    program_id: str
    data: str


class TransactionMeta(CamelModel):
    err: None | str = None
    fee: int
    pre_balances: list[int]
    post_balances: list[int]
    inner_instructions: list
    pre_token_balances: list
    post_token_balances: list
    log_messages: list
    rewards: list[Reward] | None
    loaded_addresses: LoadedAddresses | None = None
    return_data: ReturnData | None = None
    compute_units_consumed: int | None = None
    status: dict
    version: int | None = None
