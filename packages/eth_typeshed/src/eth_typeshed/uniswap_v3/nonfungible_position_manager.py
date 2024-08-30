from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, primitives
from eth_typeshed.erc20 import OwnerRequest
from eth_typeshed.multicall import multicall
from eth_typing import HexAddress, HexStr

from .position import OwnerTokenRequest, Position

NONFUNGIBLE_POSITION_MANAGER_ADDRESS = HexAddress(
    HexStr("0xC36442b4a4522E871399CD717aBDD847Ab11FE88")
)


class NonfungiblePositionManager(ProtocolBase):
    balance_of: Annotated[
        ContractFunc[
            OwnerRequest,
            Annotated[primitives.uint256, Name("amount")],
        ],
        Name("balanceOf"),
    ] = METHOD
    token_of_owner_by_index: Annotated[
        ContractFunc[
            OwnerTokenRequest,
            primitives.uint256,
        ],
        Name("tokenOfOwnerByIndex"),
    ] = METHOD
    positions: ContractFunc[
        primitives.uint256,
        Position,
    ] = METHOD

    async def get_all_indices(self, owner: HexAddress) -> list[int]:
        balance = await self.balance_of(OwnerRequest(owner=owner)).get()
        calls = []
        for i in range(balance):
            calls.append(
                self.token_of_owner_by_index(
                    OwnerTokenRequest(
                        owner=owner,
                        index=primitives.uint256(i),
                    )
                )
            )
        return await multicall.execute(*calls)

    async def get_all_positions(self, owner: HexAddress) -> list[Position]:
        indices = await self.get_all_indices(owner)
        return await multicall.execute(
            *[self.positions(primitives.uint256(index)) for index in indices]
        )
