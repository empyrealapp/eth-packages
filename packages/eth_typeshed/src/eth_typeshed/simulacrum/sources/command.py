from typing import Annotated, ClassVar

from eth_rpc import ContractFunc
from eth_rpc.types import METHOD, Name, NoArgs, primitives

from ..utils import BaseSource, Command


class CommandSource(BaseSource):
    source_name: ClassVar[str] = "Command"
    command_type: ClassVar[type] = Command

    callback_address: Annotated[
        ContractFunc[
            NoArgs,
            primitives.address,
        ],
        Name("callbackAddress"),
    ] = METHOD

    lookup_address: Annotated[
        ContractFunc[
            primitives.address,
            primitives.address,
        ],
        Name("lookupAddress"),
    ]
