from decimal import Decimal

from eth_rpc import EventData, EventSubscriber
from eth_typeshed.constants import Factories
from eth_typeshed.uniswap_v2 import V2SyncEvent, V2SyncEventType
from eth_typing import HexAddress
from pydantic import BaseModel, Field, PrivateAttr

from .factory import V2Factory
from .pair import V2Pair


class TerminateError(Exception):
    """This is a custom error used to interrupt the subscription"""


class UniswapV2PriceSubscriber(BaseModel):
    """
    from eth_typeshed.constants import Tokens, Routers
    from eth_rpc import PrivateKeyWallet

    class MyLimitOrder(UniswapV2PriceSubscriber):
        limit_price: float
        router: UniswapV2Router
        wallet: PrivateKeyWallet

        async def handle_price_update(self, price: Decimal, event: EventData[V2SyncEventType]):
            if price < limit_price:
                await self.router.swap(
                    mint_amount_out=min_amount_out,
                    path=[Tokens.Ethereum.WETH, Tokens.Ethereum.USDC],
                    recipient=self.wallet.address,
                ).execute(self.wallet)
                self.terminate()

    async def amain():
        limit_order = MyLimitOrder(
            wallet=PrivateKeyWallet(),
        )
        pair = V2Factory.load_pair(token0=Tokens.Ethereum.USDC, token1=Tokens.Ethereum.WETH)
        limit_order.add_pair(pair)
        await limit_order.subscribe()
    """

    pairs: dict[HexAddress, V2Pair] = Field(default_factory=dict)
    factory_address: HexAddress = Field(Factories.Ethereum.UniswapV2)

    _factory: V2Factory = PrivateAttr()
    _prepared: bool = PrivateAttr(False)
    _subscriber: EventSubscriber = PrivateAttr(
        default_factory=lambda: EventSubscriber()
    )

    def model_post_init(self, __context):
        self._factory = V2Factory(self.factory_address)
        self._subscriber.add_receiver(self, [V2SyncEvent])

    @property
    def factory(self):
        return self._factory

    @property
    def subscriber(self):
        return self._subscriber

    async def add_pair(
        self,
        pair: HexAddress | V2Pair,
    ):
        pair = V2Pair.load(pair)
        self.pairs[pair.address.lower()] = pair  # type: ignore

    async def subscribe(self):
        try:
            await self.subscriber.listen(
                addresses=[pair_address for pair_address in self.pairs.keys()]
            )
        except TerminateError:
            # This is a simple way to exit out of the subscribe loop
            return

    async def put(self, event_data: EventData[V2SyncEventType]):
        await self.handle_price_update(
            self.get_price(event_data.event, event_data.log.address),
            event_data,
        )

    def get_price(self, event: V2SyncEventType, address: HexAddress):
        pair = self.pairs[address.lower()]  # type: ignore
        token0_reserves = event.reserve0 / 10 ** pair.token0.sync.decimals()
        token1_reserves = event.reserve1 / 10 ** pair.token1.sync.decimals()

        if pair.flipped:
            return token1_reserves / token0_reserves
        return token0_reserves / token1_reserves

    async def handle_price_update(
        self, price: Decimal, event: EventData[V2SyncEventType]
    ):
        """Define an action based on a price"""

    def terminate(self):
        """Ends the subscription by catching a custom error"""
        raise TerminateError()
