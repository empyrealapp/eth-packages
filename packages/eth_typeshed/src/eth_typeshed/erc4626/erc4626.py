from typing import Annotated

from eth_rpc import ContractFunc
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from eth_typeshed.erc20 import ERC20


class ERC4626(ERC20):
    asset: ContractFunc[
        NoArgs,
        Annotated[primitives.address, Name("assetTokenAddress")],
    ] = METHOD
    total_assets: Annotated[
        ContractFunc[
            NoArgs,
            Annotated[primitives.uint256, Name("totalManagedAssets")],
        ],
        Name("totalAssets"),
    ] = METHOD
    convert_to_shares: Annotated[
        ContractFunc[
            Annotated[primitives.uint256, Name("assets")],
            Annotated[primitives.uint256, Name("shares")],
        ],
        Name("convertToShares"),
    ] = METHOD
    convert_to_assets: Annotated[
        ContractFunc[
            Annotated[primitives.uint256, Name("shares")],
            Annotated[primitives.uint256, Name("assets")],
        ],
        Name("convertToAssets"),
    ] = METHOD
    max_deposit: Annotated[
        ContractFunc[
            Annotated[primitives.address, Name("receiver")],
            Annotated[primitives.uint256, Name("maxAssets")],
        ],
        Name("maxDeposit"),
    ] = METHOD
    preview_deposit: Annotated[
        ContractFunc[
            Annotated[primitives.uint256, Name("assets")],
            Annotated[primitives.uint256, Name("shares")],
        ],
        Name("previewDeposit"),
    ] = METHOD
    deposit: Annotated[
        ContractFunc[
            tuple[
                Annotated[primitives.uint256, Name("assets")],
                Annotated[primitives.address, Name("receiver")],
            ],
            Annotated[primitives.uint256, Name("shares")],
        ],
        Name("deposit"),
    ] = METHOD
    max_mint: Annotated[
        ContractFunc[
            Annotated[primitives.address, Name("receiver")],
            Annotated[primitives.uint256, Name("maxShares")],
        ],
        Name("maxMint"),
    ] = METHOD
    preview_mint: Annotated[
        ContractFunc[
            Annotated[primitives.uint256, Name("shares")],
            Annotated[primitives.uint256, Name("assets")],
        ],
        Name("previewMint"),
    ] = METHOD
    mint: Annotated[
        ContractFunc[
            tuple[
                Annotated[primitives.uint256, Name("shares")],
                Annotated[primitives.address, Name("receiver")],
            ],
            Annotated[primitives.uint256, Name("assets")],
        ],
        Name("mint"),
    ] = METHOD
    max_withdraw: Annotated[
        ContractFunc[
            Annotated[primitives.address, Name("owner")],
            Annotated[primitives.uint256, Name("maxAssets")],
        ],
        Name("maxWithdraw"),
    ] = METHOD
    preview_withdraw: Annotated[
        ContractFunc[
            Annotated[primitives.uint256, Name("assets")],
            Annotated[primitives.uint256, Name("shares")],
        ],
        Name("previewWithdraw"),
    ] = METHOD
    withdraw: Annotated[
        ContractFunc[
            tuple[
                Annotated[primitives.uint256, Name("assets")],
                Annotated[primitives.address, Name("receiver")],
                Annotated[primitives.address, Name("owner")],
            ],
            Annotated[primitives.uint256, Name("shares")],
        ],
        Name("withdraw"),
    ] = METHOD
    max_redeem: Annotated[
        ContractFunc[
            Annotated[primitives.address, Name("owner")],
            Annotated[primitives.uint256, Name("maxShares")],
        ],
        Name("maxRedeem"),
    ] = METHOD
    preview_redeem: Annotated[
        ContractFunc[
            Annotated[primitives.uint256, Name("shares")],
            Annotated[primitives.uint256, Name("assets")],
        ],
        Name("previewRedeem"),
    ] = METHOD
    redeem: Annotated[
        ContractFunc[
            tuple[
                Annotated[primitives.uint256, Name("shares")],
                Annotated[primitives.address, Name("receiver")],
                Annotated[primitives.address, Name("owner")],
            ],
            Annotated[primitives.uint256, Name("assets")],
        ],
        Name("redeem"),
    ] = METHOD
