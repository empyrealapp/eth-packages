from typing import Annotated

from eth_rpc.contract import ContractFunc
from eth_rpc.function import Name
from eth_rpc.types import METHOD

from ..._base import ProtocolBase
from .types import (
    AddLiquidityETHRequest,
    AddLiquidityRequest,
    AddLiquidityResponse,
    RemoveLiquidityETHRequest,
    RemoveLiquidityETHResponse,
    RemoveLiquidityRequest,
    RemoveLiquidityResponse,
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

    # TODO: finish adding methods
