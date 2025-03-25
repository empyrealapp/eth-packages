from typing import NewType

from .args import (
    GetBlockHashRequest,
    GetBlockRequest,
    GetTxRequest,
    RawTransactionRequest,
)
from .block import Block
from .chain import ChainInfo
from .network import Network
from .transaction import Transaction, VerboseTransaction, Verbose2Transaction

NoArgs = NewType("NoArgs", tuple[()])


__all__ = [
    "Block",
    "ChainInfo",
    "GetBlockHashRequest",
    "GetBlockRequest",
    "GetTxRequest",
    "Network",
    "NoArgs",
    "Transaction",
    "RawTransactionRequest",
    "VerboseTransaction",
    "Verbose2Transaction",
]
