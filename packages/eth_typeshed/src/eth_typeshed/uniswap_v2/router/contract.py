from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name

from .types import (
    AddLiquidityETHRequest,
    AddLiquidityRequest,
    AddLiquidityResponse,
    EthSwapRequest,
    RemoveLiquidityETHRequest,
    RemoveLiquidityETHResponse,
    RemoveLiquidityRequest,
    RemoveLiquidityResponse,
    TokenSwapRequest,
)

ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"


class UniswapV2Router(ProtocolBase):
    add_liquidity: Annotated[
        ContractFunc[
            AddLiquidityRequest,
            AddLiquidityResponse,
        ],
        Name("addLiquidity"),
    ] = METHOD
    add_liquidity_eth: Annotated[
        ContractFunc[
            AddLiquidityETHRequest,
            AddLiquidityResponse,
        ],
        Name("addLiquidityETH"),
    ] = METHOD

    remove_liquidity: Annotated[
        ContractFunc[
            RemoveLiquidityRequest,
            RemoveLiquidityResponse,
        ],
        Name("removeLiquidity"),
    ]
    remove_liquidity_eth: Annotated[
        ContractFunc[
            RemoveLiquidityETHRequest,
            RemoveLiquidityETHResponse,
        ],
        Name("removeLiquidityETH"),
    ]

    swap_exact_tokens_for_tokens_supporting_fee_on_transfer_tokens: Annotated[
        ContractFunc[
            TokenSwapRequest,
            None,
        ],
        Name("swapExactTokensForTokensSupportingFeeOnTransferTokens"),
    ]

    swap_exact_eth_for_tokens_supporting_fee_on_transfer_tokens: Annotated[
        EthSwapRequest,
        Name("swapExactETHForTokensSupportingFeeOnTransferTokens"),
    ]

    # TODO: finish adding methods
