from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, NoArgs, primitives


class ProtocolRegistry(ProtocolBase):
    blocks: ContractFunc[
        NoArgs,
        primitives.address,
    ] = METHOD

    blockstorage: ContractFunc[
        NoArgs,
        primitives.address,
    ] = METHOD
