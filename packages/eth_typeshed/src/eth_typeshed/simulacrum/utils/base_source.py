from abc import ABC, abstractmethod
from typing import Annotated, Any, ClassVar

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from pydantic import BaseModel


class SimulacrumSubmission(BaseModel):
    source_data: bytes
    verification_data: bytes = b""
    require_success: bool = True


class BaseSource(ProtocolBase, ABC):
    name: ClassVar[str]
    input_type: ClassVar[type]

    submit: ContractFunc[
        SimulacrumSubmission,
        Annotated[primitives.bool, Name("success")],
    ] = METHOD

    submit_many: Annotated[
        ContractFunc[
            tuple[list[bytes], list[bytes], bool],
            None,
        ],
        Name("submitMany"),
    ] = METHOD

    registry: ContractFunc[
        NoArgs,
        primitives.address,
    ] = METHOD

    @classmethod
    @abstractmethod
    def validate_input(cls, input: Any): ...
