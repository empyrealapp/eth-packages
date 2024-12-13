from eth_rpc import ContractFunc
from eth_rpc.types import METHOD, NoArgs, primitives

from eth_rpc import ProtocolBase


class ProtocolRegistry(ProtocolBase):
    blocks: ContractFunc[
        NoArgs,
        primitives.address,
    ] = METHOD

    blockstorage: ContractFunc[
        NoArgs,
        primitives.address,
    ] = METHOD
