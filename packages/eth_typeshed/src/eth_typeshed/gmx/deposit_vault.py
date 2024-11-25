from typing import Annotated

from eth_rpc import ProtocolBase, ContractFunc
from eth_rpc.types import primitives, Name, NoArgs


class DepositVault(ProtocolBase):
    data_store: Annotated[
        ContractFunc[
            NoArgs,
            primitives.address
        ],
        Name("dataStore"),
    ]

    record_transfer_in: Annotated[
        ContractFunc[
            primitives.address,
            primitives.uint256
        ],
        Name("recordTransferIn"),
    ]

    role_store: Annotated[
        ContractFunc[
            NoArgs,
            primitives.address
        ],
        Name("roleStore"),
    ]

    sync_token_balance: Annotated[
        ContractFunc[
            primitives.address,
            primitives.uint256
        ],
        Name("syncTokenBalance"),
    ]

    token_balances: Annotated[
        ContractFunc[
            primitives.address,
            primitives.uint256
        ],
        Name("tokenBalances"),
    ]

    def transfer_out(
        self,
        arg1: primitives.address,
        arg2: primitives.address,
        arg3: primitives.uint256,
        arg4: primitives.bool | None = None,
    ) -> None:
        if arg4 is None:
            return self.transfer_out_1((arg1, arg2, arg3))
        return self.transfer_out_2((arg1, arg2, arg3, arg4))

    transfer_out_1: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.uint256],
            None
        ],
        Name("transferOut"),
    ]

    transfer_out_2: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.address, primitives.uint256, bool],
            None
        ],
        Name("transferOut"),
    ]

    transfer_out_native_token: Annotated[
        ContractFunc[
            tuple[primitives.address, primitives.uint256],
            None
        ],
        Name("transferOutNativeToken"),
    ]
