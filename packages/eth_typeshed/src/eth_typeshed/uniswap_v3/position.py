from functools import cached_property
from typing import Annotated

from eth_rpc.types import BLOCK_STRINGS, Name, primitives
from eth_typeshed.constants import Factories
from eth_typeshed.erc20 import ERC20
from eth_typeshed.multicall import MULTICALL3_ADDRESS, Multicall
from eth_typing import HexAddress
from pydantic import BaseModel, Field, PrivateAttr, computed_field

from .factory import GetPoolRequest, UniswapV3Factory
from .pool import Slot0, Tick, UniswapV3Pool
from .utils import get_fees, liquidity_to_token_amounts


class OwnerTokenRequest(BaseModel):
    owner: HexAddress
    index: primitives.uint256


class Position(BaseModel):
    _pool_address: HexAddress | None = PrivateAttr(default=None)
    factory_address: HexAddress = Field(default=Factories.Ethereum.UniswapV3)

    nonce: primitives.uint96
    operator: primitives.address
    token0: primitives.address
    token1: primitives.address
    fee: primitives.uint24
    tick_lower: Annotated[
        primitives.int24,
        Name("tickLower"),
    ]
    tick_upper: Annotated[
        primitives.int24,
        Name("tickUpper"),
    ]
    liquidity: primitives.uint128
    fee_growth_inside0_last: Annotated[
        primitives.uint256,
        Name("feeGrowthInside0LastX128"),
    ]
    fee_growth_inside1_last: Annotated[
        primitives.uint256,
        Name("feeGrowthInside1LastX128"),
    ]
    tokens_owed0: Annotated[
        primitives.uint128,
        Name("tokensOwed0"),
    ]
    tokens_owed1: Annotated[
        primitives.uint128,
        Name("tokensOwed1"),
    ]

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def pool(self) -> UniswapV3Pool:
        if not self._pool_address:
            self._pool_address = (
                UniswapV3Factory(address=self.factory_address)
                .get_pool(
                    GetPoolRequest(
                        token_a=self.token0,
                        token_b=self.token1,
                        fee=self.fee,
                    )
                )
                .get()
            )
        return UniswapV3Pool(address=self._pool_address)

    async def token_amounts(self):
        slot0 = await self.pool.slot0().get()
        sqrt_price_x96 = slot0.sqrt_price_x96
        return liquidity_to_token_amounts(
            self.liquidity,
            sqrt_price_x96,
            self.tick_lower,
            self.tick_upper,
        )

    async def get_tick_lower(self):
        return await self.pool.ticks(self.tick_lower).get()

    async def get_tick_upper(self):
        return await self.pool.ticks(self.tick_upper).get()

    async def price_range(self):
        token0_decimals = await ERC20(self.token0).decimals().get()
        token1_decimals = await ERC20(self.token1).decimals().get()
        lower = 1.0001**self.tick_lower * 10 ** (token0_decimals - token1_decimals)
        upper = 1.0001**self.tick_upper * 10 ** (token0_decimals - token1_decimals)
        return [lower, upper]

    async def get_pending_fees(self, block_number: int | BLOCK_STRINGS = "latest"):
        multicall = Multicall[self.pool._network](address=MULTICALL3_ADDRESS)

        fee_growth_global0: primitives.uint256
        fee_growth_global1: primitives.uint256
        slot0: Slot0
        lower_tick: Tick
        upper_tick: Tick
        (
            fee_growth_global0,
            fee_growth_global1,
            slot0,
            lower_tick,
            upper_tick,
        ) = await multicall.execute(
            self.pool.fee_growth_global0(),
            self.pool.fee_growth_global1(),
            self.pool.slot0(),
            self.pool.ticks(self.tick_lower),
            self.pool.ticks(self.tick_upper),
            block_number=block_number,
        )

        return get_fees(
            fee_growth_global0,
            fee_growth_global1,
            lower_tick.fee_growth_outside0,
            upper_tick.fee_growth_outside0,
            self.fee_growth_inside0_last,
            lower_tick.fee_growth_outside1,
            upper_tick.fee_growth_outside1,
            self.fee_growth_inside1_last,
            self.liquidity,
            self.tick_lower,
            self.tick_upper,
            slot0.tick,
        )

    @property
    def range(self) -> tuple[primitives.int24, primitives.int24]:
        return self.tick_lower, self.tick_upper
