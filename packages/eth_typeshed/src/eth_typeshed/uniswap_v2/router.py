from typing import Any, Annotated, Callable, ClassVar

from eth_typing import HexAddress

from eth_rpc.contract import ContractFunc
from eth_rpc.function import FuncSignature
from eth_rpc.types import ContractMethod

from .._base import ProtocolBase

ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"


class UniswapV2Router(ProtocolBase):
    # TODO: this is all in the deprecated format, needs to be updated
    """
    addLiquidity: Annotated[
        Callable[[HexAddress, HexAddress, int, int, int, int, HexAddress, int], ContractFunc], ContractMethod
    ]
    addLiquidityETH: Annotated[Callable[[HexAddress, int, int, int, HexAddress, int], ContractFunc], ContractMethod]
    swapExactTokensForTokens: Annotated[
        Callable[[int, int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
    ]
    swapTokensForExactTokens: Annotated[
        Callable[[int, int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
    ]
    swapExactETHForTokens: Annotated[Callable[[int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod]
    swapExactTokensForETHSupportingFeeOnTransferTokens: Annotated[
        Callable[[int, int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
    ]
    swapExactETHForTokensSupportingFeeOnTransferTokens: Annotated[
        Callable[[int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
    ]
    swapExactTokensForTokensSupportingFeeOnTransferTokens: Annotated[
        Callable[[int, int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
    ]
    """
