from typing import Literal

from sol_rpc.utils import CamelModel


class SendTransactionParams(CamelModel):
    encoding: Literal["base58", "base64"] = "base58"
    skip_preflight: bool = False
    preflight_commitment: Literal["confirmed", "finalized", "processed"] = "finalized"
    max_retries: int = 1


class SendTransactionArgs(CamelModel):
    transaction: str
    params: SendTransactionParams | None = None
