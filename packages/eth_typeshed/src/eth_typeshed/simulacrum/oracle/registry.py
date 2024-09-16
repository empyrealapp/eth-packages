from typing import Annotated

from eth_rpc import ContractFunc
from eth_rpc.contract.base import ProtocolBase
from eth_rpc.types import NoArgs, primitives


class ValidatorRegistry(ProtocolBase):
    threshold: ContractFunc[
        NoArgs,
        Annotated[primitives.uint8, "count"],
    ]

    validators: ContractFunc[
        primitives.address,
        bool,
    ]
