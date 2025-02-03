from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, primitives
from pydantic import BaseModel


class ExecuteRequest(BaseModel):
    to: primitives.address
    value: primitives.uint256
    data: primitives.bytes
    operation: primitives.uint8
    txGas: primitives.uint256


class ExecuteResponse(BaseModel):
    success: primitives.bool
    returnData: primitives.bytes


class SimulacrumExecutor(ProtocolBase):
    execute: Annotated[
        ContractFunc[
            ExecuteRequest,
            ExecuteResponse,
        ],
        Name("execute"),
    ] = METHOD
