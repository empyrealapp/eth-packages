from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, Struct, primitives
from eth_typeshed.erc20 import OwnerRequest
from eth_typeshed.multicall import multicall
from eth_typing import HexAddress, HexStr

from .position import OwnerTokenRequest, Position

NONFUNGIBLE_POSITION_MANAGER_ADDRESS = HexAddress(
    HexStr("0xC36442b4a4522E871399CD717aBDD847Ab11FE88")
)


class CollectParams(Struct):
    token_id: primitives.uint256
    recipient: HexAddress
    amount0_max: primitives.uint128
    amount1_max: primitives.uint128


class DecreaseLiquidityParams(Struct):
    token_id: primitives.uint256
    liquidity: primitives.uint128
    amount0_min: primitives.uint256
    amount1_min: primitives.uint256
    deadline: primitives.uint256


class MintParams(Struct):
    """Parameters for minting a new Uniswap V3 position."""

    token0: HexAddress
    token1: HexAddress
    fee: primitives.uint24
    tickLower: primitives.int24
    tickUpper: primitives.int24
    amount0Desired: primitives.uint256
    amount1Desired: primitives.uint256
    amount0Min: primitives.uint256
    amount1Min: primitives.uint256
    recipient: HexAddress
    deadline: primitives.uint256


class MintResult(BaseModel):
    """Result from minting a new position."""

    token_id: primitives.uint256
    liquidity: primitives.uint128
    amount0: primitives.uint256
    amount1: primitives.uint256


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

    collect: ContractFunc[
        CollectParams,
        tuple[primitives.uint256, primitives.uint256],
    ] = METHOD

    mint: ContractFunc[
        MintParams,
        MintResult,
    ] = METHOD

    decrease_liquidity: Annotated[
        ContractFunc[
            DecreaseLiquidityParams,
            tuple[primitives.uint256, primitives.uint256],
        ],
        Name("decreaseLiquidity"),
    ] = METHOD

    refund_eth: Annotated[
        ContractFunc[
            NoArgs,
            None,
        ],
        Name("refundETH"),
    ] = METHOD

    unwrap_weth: Annotated[
        ContractFunc[
            tuple[primitives.uint256, primitives.address],
            None,
        ],
        Name("unwrapWETH9"),
    ] = METHOD

    sweep_token: Annotated[
        ContractFunc[
            tuple[HexAddress, primitives.uint256, HexAddress],
            None,
        ],
        Name("sweepToken"),
    ] = METHOD

    multicall: ContractFunc[
        list[bytes],
        list[bytes],
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
