from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, Struct, primitives


class TokenStruct(Struct):
    name: primitives.bytes32
    token_address: primitives.address


class TokenRegistry(ProtocolBase):
    lookup: ContractFunc[
        primitives.bytes32,
        primitives.address,
    ] = METHOD

    update_many: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, list[TokenStruct]],
            None,
        ],
        Name("updateMany"),
    ] = METHOD
