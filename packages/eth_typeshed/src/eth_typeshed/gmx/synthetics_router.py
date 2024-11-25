from typing import Annotated

from eth_rpc import ProtocolBase, ContractFunc
from eth_rpc.types import primitives, Name, NoArgs


class SyntheticsRouter(ProtocolBase):
    plugin_transfer: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.address, primitives.uint256],
            None
        ],
        Name("pluginTransfer"),
    ]

    role_store: Annotated[
        ContractFunc[
            NoArgs,
            primitives.address
        ],
        Name("roleStore"),
    ]
