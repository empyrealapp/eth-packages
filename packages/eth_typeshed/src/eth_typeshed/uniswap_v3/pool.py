import asyncio
import math
from collections.abc import Iterable
from decimal import Decimal
from typing import Annotated, cast

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from eth_typeshed.multicall import multicall
from eth_typing import HexAddress
from pydantic import BaseModel, Field, PrivateAttr

from ..erc20 import ERC20
from .constants import MIN_TICK, Q192
from .events import V3MintEvent, V3SwapEvent, V3SwapEventType
from .utils import tick_from_bitmap, tick_to_price


class Slot0(BaseModel):
    sqrt_price: primitives.uint160 = Field(serialization_alias="sqrtPriceX96")
    tick: primitives.int24
    observation_index: primitives.uint16 = Field(serialization_alias="observationIndex")
    observation_cardinality: primitives.uint16 = Field(
        serialization_alias="observationCardinality"
    )
    observation_cardinality_next: primitives.uint16 = Field(
        serialization_alias="observationCardinality"
    )
    fee_protocol: primitives.uint8 = Field(serialization_alias="feeProtocol")
    unlocked: bool


class Tick(BaseModel):
    liquidity_gross: Annotated[primitives.uint128, Name("liquidityGross")]
    liquidity_net: Annotated[primitives.int128, Name("liquidityNet")]
    fee_growth_outside0: Annotated[primitives.uint256, Name("feeGrowthOutside0X128")]
    fee_growth_outside1: Annotated[primitives.uint256, Name("feeGrowthOutside1X128")]
    tick_cumulative_outside: Annotated[primitives.int56, Name("tickCumulativeOutside")]
    seconds_per_liquidity_outside: Annotated[
        primitives.uint160, Name("secondsPerLiquidityOutsideX128")
    ]
    seconds_outside: Annotated[primitives.uint32, Name("secondsOutside")]
    initialized: bool  # liquidity_net > 0

    def __repr__(self):
        return f"<Tick liquidity_net={self.liquidity_net}>"


class ProcessedTick(BaseModel):
    index: int
    tick: Tick
    token0: ERC20
    token1: ERC20
    active_liquidity: int = 0

    @property
    def liquidity_net(self):
        return self.tick.liquidity_net

    @property
    def price0(self):
        return tick_to_price(
            self.index, self.token0.get_decimals(), self.token1.get_decimals()
        )

    @property
    def price1(self):
        return (
            tick_to_price(
                self.index, self.token0.get_decimals(), self.token1.get_decimals()
            )
            ** -1
        )

    def __repr__(self):
        return f"<ProcessedTick index={self.index}>"


class UniswapV3Pool(ProtocolBase):
    _tick_spacing: int | None = PrivateAttr(None)
    _token0: ERC20 | None = PrivateAttr(None)
    _token1: ERC20 | None = PrivateAttr(None)

    tick_bitmap: Annotated[
        ContractFunc[primitives.int16, primitives.uint256],
        Name("tickBitmap"),
    ] = METHOD
    fee: ContractFunc[NoArgs, primitives.uint24] = METHOD
    slot0: ContractFunc[NoArgs, Slot0] = METHOD
    token0: ContractFunc[NoArgs, HexAddress] = METHOD
    token1: ContractFunc[NoArgs, HexAddress] = METHOD
    ticks: ContractFunc[primitives.int24, Tick] = METHOD
    liquidity: ContractFunc[NoArgs, primitives.uint128] = METHOD
    tick_spacing: Annotated[
        ContractFunc[NoArgs, primitives.int24],
        Name("tickSpacing"),
    ] = METHOD
    fee_growth_global0: Annotated[
        ContractFunc[NoArgs, primitives.uint256], Name("feeGrowthGlobal0X128")
    ] = METHOD
    fee_growth_global1: Annotated[
        ContractFunc[NoArgs, primitives.uint256], Name("feeGrowthGlobal1X128")
    ] = METHOD

    async def get_price(self, token0: bool = True):
        slot0 = await self.slot0().get()
        _token0 = await self.token0().get()
        _token1 = await self.token1().get()
        token0_decimals = await ERC20(address=_token0).decimals().get()
        token1_decimals = await ERC20(address=_token1).decimals().get()
        return self.sqrt_price_x96_to_token_prices(
            slot0.sqrt_price,
            token0_decimals,
            token1_decimals,
            token0,
        )

    @staticmethod
    def sqrt_price_x96_to_token_prices(
        sqrt_price_x96: int,
        token0_decimals: int,
        token1_decimals: int,
        token0: bool = True,
    ) -> Decimal:
        num = Decimal(sqrt_price_x96 * sqrt_price_x96)
        price1 = (
            (num / Q192)
            * (Decimal(10) ** token0_decimals)
            / (Decimal(10) ** token1_decimals)
        )
        price0 = Decimal(1) / price1

        return price0 if token0 else price1

    async def all_tick_values(self):
        tick_spacing = await self.get_tick_spacing()
        min_tick, max_tick = await self.tick_range()
        return list(range(min_tick, max_tick, tick_spacing))

    async def get_token0(self):
        if not self._token0:
            self._token0 = ERC20(await self.token0().get())
        return self._token0

    async def get_token1(self):
        if not self._token1:
            self._token1 = ERC20(await self.token1().get())
        return self._token1

    async def get_tick_spacing(self):
        if not self._tick_spacing:
            self._tick_spacing = await self.tick_spacing().get()
        return self._tick_spacing

    async def get_swaps(
        self, start_block, end_block
    ) -> dict[int, list[V3SwapEventType]]:
        ticks: dict[int, list[V3SwapEventType]] = {}
        tick_values = await self.all_tick_values()
        async for event in V3SwapEvent.set_filter(addresses=[self.address]).backfill(
            start_block, end_block
        ):
            tick = event.event.tick
            closest_tick = max(t for t in tick_values if t <= tick)
            if tick in ticks:
                ticks[closest_tick].append(event.event)
            else:
                ticks[closest_tick] = [event.event]
        return ticks

    async def get_ticks(self, indices: Iterable[int]) -> list[ProcessedTick]:
        calls = []
        for tick in indices:
            calls.append(self.ticks(primitives.int24(tick)))
        ticks: list[Tick] = await multicall.execute(*calls)

        processed_ticks = []
        for idx, tick_data in zip(indices, ticks):
            processed_ticks.append(
                ProcessedTick(
                    index=idx,
                    tick=tick_data,
                    token0=await self.get_token0(),
                    token1=await self.get_token1(),
                )
            )
        return processed_ticks

    async def tvl(self, block_number=None) -> list[ProcessedTick]:
        liquidity, initialized_ticks, active_tick_index = await asyncio.gather(
            self.liquidity().get(),
            self.get_initialized_ticks(),
            self.active_tick(),
        )
        ticks = await self.get_ticks(initialized_ticks)

        if active_tick_index in initialized_ticks:
            active_tick = [t for t in ticks if t.index == active_tick_index][0]
            active_tick.active_liquidity = liquidity
            current_liquidity = liquidity - active_tick.liquidity_net
            previous_tick_net = active_tick.liquidity_net
        else:
            current_liquidity = liquidity
            previous_tick_net = 0

        for tick in [tick for tick in ticks if tick.index < active_tick_index][::-1]:
            tick.active_liquidity = current_liquidity - previous_tick_net
            current_liquidity = tick.active_liquidity
            previous_tick_net = tick.liquidity_net

        current_liquidity = liquidity
        previous_tick_net = 0
        for tick in [tick for tick in ticks if tick.index > active_tick_index]:
            tick.active_liquidity = current_liquidity + tick.liquidity_net
            current_liquidity = tick.active_liquidity
        return ticks

    async def get_tick_range(self, lower: int, upper: int) -> list[ProcessedTick]:
        if not self._tick_spacing:
            self._tick_spacing = await self.tick_spacing().get()
        assert self._tick_spacing
        return await self.get_ticks(range(lower, upper, self._tick_spacing))

    async def tick_range(self):
        tick_spacing = await self.get_tick_spacing()
        min_tick = math.ceil(MIN_TICK / tick_spacing) * tick_spacing
        return min_tick, -min_tick

    async def bitmap_range(self) -> tuple[int, int]:
        min_tick, max_tick = await self.tick_range()
        return (min_tick // 60 // 256), (max_tick // 60 // 256)

    async def get_initialized_ticks(self) -> list[int]:
        min_bitmap, max_bitmap = await self.bitmap_range()
        tick_spacing = await self.get_tick_spacing()
        bitmaps = await multicall.execute(
            *[
                self.tick_bitmap(primitives.int16(idx))
                for idx in range(min_bitmap, max_bitmap + 1)
            ]
        )
        initialized_ticks = []
        for idx, row in zip(range(min_bitmap, max_bitmap + 1), bitmaps):
            initialized_ticks.extend(tick_from_bitmap(idx, row, tick_spacing))
        return initialized_ticks

    async def active_tick(self) -> int:
        slot0 = await self.slot0().get()
        if not self._tick_spacing:
            self._tick_spacing = await self.tick_spacing().get()
        return slot0.tick // self._tick_spacing * self._tick_spacing

    async def liquidity_at_current_tick(self, tick: int) -> tuple[float, float]:
        tick_spacing, slot0, liquidity = cast(
            tuple[int, Slot0, int],
            await multicall.execute(
                self.tick_spacing(),
                self.slot0(),
                self.liquidity(),
            ),
        )
        bottom_tick = tick
        top_tick = tick + tick_spacing

        price = tick_to_price(slot0.tick)
        sa = tick_to_price(bottom_tick // 2)
        sb = tick_to_price(top_tick // 2)
        sqrt_price = math.sqrt(price)

        amount0 = liquidity * (sb - sqrt_price) / (sqrt_price * sb)
        amount1 = liquidity * (sqrt_price - sa)

        return (amount0, amount1)

    async def get_all_positions(self):
        events = []
        async for event in V3MintEvent.set_filter(addresses=[self.address]).backfill():
            events.append(event.event)
        return events

    def __repr__(self):
        return f"<Pool address={self.address}>"
