import asyncio
from decimal import Decimal
from typing import ClassVar, Optional

from eth_protocols.logger import logger
from eth_protocols.uniswap_v2.pair import V2Pair
from eth_protocols.uniswap_v3.pool import V3Pool
from eth_rpc import EventData, EventSubscriber, get_current_network
from eth_rpc.types import Network
from eth_rpc.utils import to_checksum
from eth_typeshed.chainlink.eth_usd_feed import ChainlinkPriceOracle, ETHUSDPriceFeed
from eth_typeshed.constants import Tokens
from eth_typeshed.uniswap_v2 import V2SyncEvent, V2SyncEventType
from eth_typeshed.uniswap_v3 import V3SwapEvent, V3SwapEventType
from eth_typing import HexAddress
from pydantic import BaseModel, Field, PrivateAttr


class EthPriceProvider(BaseModel):
    feed: ClassVar[ETHUSDPriceFeed] = ETHUSDPriceFeed(
        address=ChainlinkPriceOracle.for_network().ETH
    )
    price: float | None = None
    decimals: int = Field(default=8)

    def __init__(self, block_number: int | None = None, **kwargs):
        super().__init__(**kwargs)
        if block_number:
            asyncio.run(self.refresh_price(block_number=block_number))

    async def refresh_price(self, block_number: int | None = None):
        if block_number:
            latest_round_data = (
                await self.feed.latest_round_data().get(block_number=block_number)
            )[1]
        else:
            latest_round_data = (await self.feed.latest_round_data().get())[1]

        self.price = latest_round_data / 10**self.decimals

    def get_eth_price(self):
        return Decimal(self.price)


class PriceTracker(BaseModel):
    token_address_to_pairs: dict[HexAddress, list[V2Pair | V3Pool]] = Field(
        default_factory=dict
    )
    pair_address_to_pairs: dict[HexAddress, V2Pair | V3Pool] = Field(
        default_factory=dict
    )
    _eth_price_provider: EthPriceProvider = PrivateAttr(
        default_factory=EthPriceProvider
    )
    network: Network = Field(default_factory=get_current_network)

    @property
    def stables(self):
        return Tokens.for_network(self.network).stables

    @property
    def WETH(self):
        return Tokens.for_network(self.network).WETH

    @property
    def pairs(self):
        return [
            pair for sublist in self.token_address_to_pairs.values() for pair in sublist
        ]

    async def get_pair_reserves(self, pair_address: HexAddress):
        pair_address = to_checksum(pair_address)
        pair = self.pair_address_to_pairs[pair_address]
        if not pair:
            return 0, 0
        return await pair.reserves()

    def update_pairs(self, pairs: dict[HexAddress, list[V2Pair | V3Pool]]):
        if not pairs:
            return
        for k, pairs_list in pairs.items():
            k = to_checksum(k)
            tmp_pairs = []
            for pair in pairs_list:
                address = to_checksum(pair.pair_address)
                tmp_pairs.append(pair)
                self.pair_address_to_pairs[address] = pair
            self.token_address_to_pairs[k] = tmp_pairs

    def is_stable(self, token: HexAddress):
        for s in self.stables:
            if s.lower() == token.lower():
                return True
        return False

    @staticmethod
    def find_highest_reserve_pair(
        token_address: HexAddress, pairs: list[V2Pair | V3Pool]
    ):
        highest_liq = Decimal(0)
        ret = None
        for pair in pairs:
            reserve = pair.get_reserve(token_address)
            if reserve > highest_liq:
                ret = pair
                highest_liq = reserve
        return ret

    def get_highest_liq_pair(self, token_address: HexAddress):
        if not self.token_address_to_pairs:
            raise ValueError("token address_to_pairs not set")
        pairs_list = self.token_address_to_pairs.get(to_checksum(token_address), [])
        return self.find_highest_reserve_pair(token_address, pairs_list)

    def get_tvl_in_usd(self, pair_address):
        if to_checksum(pair_address) not in self.pair_address_to_pairs:
            logger.warning(f"not found {pair_address=}")
            return 0
        pair = self.pair_address_to_pairs[to_checksum(pair_address)]
        return pair.get_reserve(pair.token0.address) * (
            self.get_price_in_usd(pair.token0.address)
        ) + pair.get_reserve(pair.token1.address) * (
            self.get_price_in_usd(pair.token1.address)
        )

    def get_price_in_usd(
        self, token_address: HexAddress, block_number: Optional[int] = None
    ):
        """
        Recurse the token address following its deepest liquidity until we reach a token with a known price.
        """
        if to_checksum(token_address) == to_checksum(self.WETH):
            return self._eth_price_provider.get_eth_price()
        if not token_address:
            return 0
        if self.is_stable(token_address):
            return 1
        pair = self.get_highest_liq_pair(token_address)
        if not pair:
            # FIXME: check if any data is missing for specific pairs
            return 0
        price_a_to_b = pair.get_price(token_address, block_number)
        tokenb = pair.get_other_token(token_address)
        if self.is_stable(tokenb):  # in self.stables:
            return price_a_to_b
        # if not found, recurse
        return price_a_to_b * self.get_price_in_usd(tokenb, block_number=block_number)

    async def subscribe(self):
        """
        subscribe to events from all pairs that you're tracking price
        if new pair added, add to pairs list and restart tracking from last hear block number
        """
        pair_addresses = [pair.pair_address for pair in self.pairs]
        subscriber = EventSubscriber()
        subscriber.add_receiver(self, [V3SwapEvent, V2SyncEvent])
        await subscriber.listen(addresses=pair_addresses)

    async def put(self, event: EventData[V3SwapEventType | V2SyncEventType]):
        match event.event:
            case V2SyncEventType(reserve0=reserve0, reserve1=reserve1):
                pair = self.pair_address_to_pairs[event.tx.address]
                pair.set_reserves(reserve0, reserve1)
                self.pair_address_to_pairs[event.tx.address]
            case V3SwapEventType():
                # TODO: handle event ingest
                #       maybe simulate reserves for V3
                pass
