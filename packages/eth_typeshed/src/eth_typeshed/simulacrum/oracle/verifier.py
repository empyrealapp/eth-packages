from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, primitives


class AttestationOracle(ProtocolBase):
    verify: ContractFunc[
        tuple[
            Annotated[primitives.bytes32, Name("dataType")],
            Annotated[primitives.bytes, Name("sourceData")],
            Annotated[primitives.bytes, Name("verificationData")],
        ],
        Annotated[primitives.bool, Name("success")],
    ] = METHOD
