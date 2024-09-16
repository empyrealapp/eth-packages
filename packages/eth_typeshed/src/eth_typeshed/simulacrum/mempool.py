from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, primitives


class Mempool(ProtocolBase):
    size_of: Annotated[
        ContractFunc[
            NoArgs,
            primitives.uint256,
        ],
        Name("sizeOf"),
    ] = METHOD
