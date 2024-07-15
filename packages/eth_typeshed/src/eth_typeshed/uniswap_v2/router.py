from typing import Any, Annotated, Callable, ClassVar

from eth_typing import HexAddress

from eth_rpc.contract import ContractFunc
from eth_rpc.function import FuncSignature
from eth_rpc.types import ContractMethod

from .._base import ProtocolBase

ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"


# class UniswapV2Router(ProtocolBase):
#     def add_liquidity(
#         self,
#         token_a: HexAddress,
#         token_b: HexAddress,
#         amount_a_desired: int,
#         amount_b_desired: int,
#         amount_a_min: int,
#         amount_b_min: int,
#         to: HexAddress,
#         deadline: int,
#     ) -> ContractFunc:
#         return self.addLiquidity(
#             token_a, token_b, amount_a_desired, amount_b_desired, amount_a_min, amount_b_min, to, deadline
#         )

#     addLiquidity: Annotated[
#         Callable[[HexAddress, HexAddress, int, int, int, int, HexAddress, int], ContractFunc], ContractMethod
#     ]
#     addLiquidityETH: Annotated[Callable[[HexAddress, int, int, int, HexAddress, int], ContractFunc], ContractMethod]
#     swapExactTokensForTokens: Annotated[
#         Callable[[int, int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
#     ]
#     swapTokensForExactTokens: Annotated[
#         Callable[[int, int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
#     ]
#     swapExactETHForTokens: Annotated[Callable[[int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod]
#     swapExactTokensForETHSupportingFeeOnTransferTokens: Annotated[
#         Callable[[int, int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
#     ]
#     swapExactETHForTokensSupportingFeeOnTransferTokens: Annotated[
#         Callable[[int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
#     ]
#     swapExactTokensForTokensSupportingFeeOnTransferTokens: Annotated[
#         Callable[[int, int, list[HexAddress], HexAddress, int], ContractFunc], ContractMethod
#     ]

#     # lazy load funcs
#     _funcs: ClassVar[dict[str, Any]] = {
#         "addLiquidity": lambda: FuncSignature.load(
#             name="addLiquidity",
#             inputs="address tokenA,address tokenB,uint amountADesired,uint amountBDesired,uint amountAMin,uint amountBMin,address to,uint deadline",
#             outputs="uint amountA, uint amountB, uint liquidity",
#         ),
#         "addLiquidityETH": lambda: FuncSignature.load(
#             name="addLiquidityETH",
#             inputs="address token,uint amountTokenDesired,uint amountTokenMin,uint amountETHMin,address to,uint deadline",
#             outputs="uint amountToken, uint amountETH, uint liquidity",
#             state_mutability="payable",
#         ),
#         "swapExactTokensForTokens": lambda: FuncSignature.load(
#             name="swapExactTokensForTokens",
#             inputs="uint amountIn,uint amountOutMin,address[] calldata path,address to,uint deadline",
#             outputs="uint[] memory amounts",
#         ),
#         "swapTokensForExactTokens": lambda: FuncSignature.load(
#             name="swapTokensForExactTokens",
#             inputs="uint amountOut,uint amountInMax,address[] calldata path,address to,uint deadline",
#             outputs="uint[] memory amounts",
#         ),
#         "swapExactETHForTokens": lambda: FuncSignature.load(
#             name="swapExactETHForTokens",
#             inputs="uint amountOutMin, address[] calldata path, address to, uint deadline",
#             outputs="uint[] memory amounts",
#         ),
#         "swapExactTokensForETHSupportingFeeOnTransferTokens": lambda: FuncSignature.load(
#             name="swapExactTokensForETHSupportingFeeOnTransferTokens",
#             inputs="uint amountIn,uint amountOutMin,address[] calldata path,address to,uint deadline",
#         ),
#         "swapExactETHForTokensSupportingFeeOnTransferTokens": lambda: FuncSignature.load(
#             name="swapExactETHForTokensSupportingFeeOnTransferTokens",
#             inputs="uint amountOutMin,address[] calldata path,address to,uint deadline",
#             state_mutability="payable",
#         ),
#         "swapExactTokensForTokensSupportingFeeOnTransferTokens": lambda: FuncSignature.load(
#             name="swapExactTokensForTokensSupportingFeeOnTransferTokens",
#             inputs="uint amountIn,uint amountOutMin,address[] calldata path,address to,uint deadline",
#         ),
#     }

#     def __init__(self, address=ROUTER_ADDRESS):
#         super().__init__(address=address)
