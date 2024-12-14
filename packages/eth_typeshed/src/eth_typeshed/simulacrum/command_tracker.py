from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, primitives


class CommandTracker(ProtocolBase):
    errors: ContractFunc[primitives.bytes32, bytes] = METHOD

    get_error: Annotated[
        ContractFunc[primitives.bytes32, bytes],
        Name("getError"),
    ] = METHOD

    set_error: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.bytes32, primitives.bytes32, bytes],
            None,
        ],
        Name("setError"),
    ] = METHOD

    set_success: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.bytes32, primitives.bytes32, bytes],
            None,
        ],
        Name("setSuccess"),
    ] = METHOD

    success: ContractFunc[primitives.bytes32, bytes] = METHOD
