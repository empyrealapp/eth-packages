from typing import Annotated

from eth_rpc import ContractFunc
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from eth_typeshed.erc20 import ERC20


class WETH(ERC20):
    withdraw: Annotated[
        ContractFunc[primitives.uint256, NoArgs],
        Name("withdraw"),
    ] = METHOD
    deposit: Annotated[
        ContractFunc[NoArgs, NoArgs],
        Name("deposit"),
    ] = METHOD
