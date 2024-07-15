from eth_typing import HexStr

from eth_rpc.types import HexInteger
from eth_rpc.utils import RPCModel


class Account(RPCModel):
    code_hash: HexStr
    storage_root: HexStr
    balance: HexInteger
    nonce: HexInteger
