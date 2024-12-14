from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, primitives
from pydantic import BaseModel, Field


class DeployArgs(BaseModel):
    owner_id: primitives.bytes32
    namespace: primitives.bytes32 = Field(default=primitives.bytes32(b""))
    index: primitives.uint256 = Field(default=primitives.uint256(0))


class AccountManager(ProtocolBase):
    deploy: ContractFunc[
        tuple[DeployArgs],
        primitives.address,
    ] = METHOD

    compute_address: Annotated[
        ContractFunc[
            DeployArgs,
            primitives.address,
        ],
        Name("computeAddress"),
    ] = METHOD
