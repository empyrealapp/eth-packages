from decimal import Decimal
from typing import Annotated

from eth_typing import HexAddress

from eth_rpc.types import METHOD
from eth_rpc.types import Name, NoArgs, primitives
from eth_rpc.contract import ContractFunc
from eth_typeshed.erc20 import ERC20


class UniswapV2Pair(ERC20):
    get_reserves: Annotated[
        ContractFunc[
            NoArgs,
            tuple[
                Annotated[primitives.uint112, Name("_reserve0")],
                Annotated[primitives.uint112, Name("_reserve1")],
                Annotated[primitives.uint32, Name("_blockTimestampLast")],
            ],
        ],
        Name("getReserves"),
    ] = METHOD
    token0: ContractFunc[NoArgs, HexAddress] = METHOD
    token1: ContractFunc[NoArgs, HexAddress] = METHOD

    def get_price(self, token0: bool = True):
        reserves0, reserves1, _ = self.get_reserves().get()
        price0, price1 = (reserves1 / reserves0, reserves0 / reserves1)
        return Decimal(price0) if token0 else Decimal(price1)
