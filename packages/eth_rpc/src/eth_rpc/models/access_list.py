from eth_typing import HexAddress, HexStr

from eth_rpc.types import HexInteger
from eth_rpc.utils import RPCModel


class AccessList(RPCModel):
    address: HexAddress
    storage_keys: list[HexStr]


class AccessListResponse(RPCModel):
    access_list: list[AccessList]
    gas_used: HexInteger
