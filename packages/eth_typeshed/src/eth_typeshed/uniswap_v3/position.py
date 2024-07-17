import asyncio
from typing import Annotated

from eth_rpc.types import Name, primitives
from eth_typeshed.constants import Factories
from eth_typeshed.erc20 import ERC20
from eth_typing import HexAddress
from pydantic import BaseModel, PrivateAttr

from .factory import GetPoolRequest, UniswapV3Factory
from .pool import UniswapV3Pool
from .utils import get_fees, liquidity_to_token_amounts


class OwnerTokenRequest(BaseModel):
    owner: HexAddress
    index: primitives.uint256


class Position(BaseModel):
    _pool_address: HexAddress = PrivateAttr(None)

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

    def pool(self, factory_address=Factories.Ethereum.UniswapV3):
        if not self._pool_address:
            self._pool_address = (
                UniswapV3Factory(address=factory_address)
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
        sqrt_price_x96 = (await self.pool().slot0().get()).sqrt_price
        return liquidity_to_token_amounts(
            self.liquidity,
            sqrt_price_x96,
            self.tick_lower,
            self.tick_upper,
        )

    async def get_tick_lower(self):
        return await self.pool().ticks(self.tick_lower).get()

    async def get_tick_upper(self):
        return await self.pool().ticks(self.tick_upper).get()

    async def price_range(self):
        token0_decimals = await ERC20(self.token0).decimals().get()
        token1_decimals = await ERC20(self.token1).decimals().get()
        lower = 1.0001**self.tick_lower * 10 ** (token0_decimals - token1_decimals)
        upper = 1.0001**self.tick_upper * 10 ** (token0_decimals - token1_decimals)
        return [lower, upper]

    async def get_pending_fees(self):
        pool = self.pool()
        (
            fee_growth_global0,
            fee_growth_global1,
            slot0,
            lower_tick,
            upper_tick,
        ) = await asyncio.gather(
            pool.fee_growth_global0().get(),
            pool.fee_growth_global1().get(),
            pool.slot0().get(),
            self.get_tick_lower(),
            self.get_tick_upper(),
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
    def range(self) -> tuple[int, int]:
        return self.tick_lower, self.tick_upper
