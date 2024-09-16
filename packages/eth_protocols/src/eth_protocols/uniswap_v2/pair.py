import asyncio
from decimal import Decimal
from typing import ClassVar, Optional

from eth_hash.auto import keccak as keccak_256
from eth_protocols.tokens import ERC20
from eth_protocols.types import DexPair
from eth_rpc import Contract, get_current_network
from eth_rpc.types import BLOCK_STRINGS, MaybeAwaitable, Network
from eth_rpc.utils import to_checksum
from eth_typeshed.multicall import multicall
from eth_typeshed.uniswap_v2 import UniswapV2Pair
from eth_typing import HexAddress, HexStr
from pydantic import PrivateAttr


class V2Pair(DexPair):
    _network: ClassVar[Network | None] = None
    _contract: UniswapV2Pair = PrivateAttr()

    def __class_getitem__(cls, network: Network):
        cls._network = network

    @classmethod
    def load_static(
        cls,
        pair_address: HexAddress,
        tokena: HexAddress,
        tokenb: HexAddress,
    ):
        token0, token1 = (
            (tokena, tokenb) if tokena.lower() < tokenb.lower() else (tokenb, tokena)
        )
        network = cls._network or get_current_network()
        return V2Pair(
            pair_address=pair_address,  # type: ignore
            token0=ERC20.load(token0, network=network),
            token1=ERC20.load(token1, network=network),
        )

    @classmethod
    async def load_pair(
        cls,
        pair_address: HexAddress,
    ):
        _contract = UniswapV2Pair(address=pair_address)
        token0, token1 = await multicall.execute(
            _contract.token0(),
            _contract.token1(),
        )
        network = cls._network or get_current_network()
        return V2Pair(
            pair_address=pair_address,  # type: ignore
            token0=ERC20.load(token0, network=network),
            token1=ERC20.load(token1, network=network),
        )

    def model_post_init(self, __context):
        self._contract = UniswapV2Pair(address=self.pair_address)

    def get_reserves(
        self, block_number: int | BLOCK_STRINGS = "latest", sync: bool = False
    ) -> MaybeAwaitable[tuple[int, int]]:
        if sync:
            reserve0, reserve1, _ = self._contract.get_reserves().get(
                block_number=block_number, sync=sync
            )
            self.set_reserves(reserve0, reserve1)
            return reserve0, reserve1

        # create an async function that loads the reserves
        async def get_reserves() -> tuple[int, int]:
            reserve0, reserve1, _ = await self._contract.get_reserves().get(
                block_number=block_number
            )
            self.set_reserves(reserve0, reserve1)
            return reserve0, reserve1

        return get_reserves

    def get_price(
        self, token: HexAddress, block_number: Optional[int | BLOCK_STRINGS] = None
    ) -> Decimal:
        token = to_checksum(token)
        assert (
            token.lower() == self.token0.address.lower()
            or token.lower() == self.token1.address.lower()
        ), "invalid token"
        token_a, token_b = (
            (self.token0, self.token1)
            if token.lower() == self.token0.address.lower()
            else (self.token1, self.token0)
        )

        if block_number:
            reserve0, reserve1, _ = self._contract.get_reserves().get(
                block_number=block_number
            )
            if token == self.token0.address:
                reserve_a = Decimal(reserve0 / 10**self.decimals0)
                reserve_b = Decimal(reserve1 / 10**self.decimals1)
                return Decimal(reserve_b / reserve_a)
            if token == self.token1.address:
                reserve_a = Decimal(reserve1 / 10**self.decimals1)
                reserve_b = Decimal(reserve0 / 10**self.decimals0)
                return Decimal(reserve_b / reserve_a)
            return Decimal("0")

        reserve_a = self.get_reserve(token_a.address)
        reserve_b = self.get_reserve(token_b.address)

        return Decimal(reserve_b / reserve_a)

    def get_other_token(self, token: HexAddress) -> HexAddress:
        token = to_checksum(token)
        if token == self.token0.address:
            return self.token1.address
        if token == self.token1.address:
            return self.token0.address
        raise ValueError(
            f"{token=} cannot be found {self.token0.address=} {self.token1.address=}"
        )

    async def load_decimals(self):
        await asyncio.gather(
            self.token0.decimals(),
            self.token1.decimals(),
        )


def get_uniswap_v2_pair_addr(token_a: HexAddress, token_b: HexAddress) -> HexAddress:
    # get factory address
    factory_address = HexAddress(HexStr("0x5C69BEE701EF814A2B6A3EDD4B1652CB9CC5AA6F"))
    factory_contract = Contract(address=factory_address)

    # sort tokens and create salt
    token_a, token_b = sorted([token_a, token_b])
    salt = keccak_256(bytes.fromhex(token_a[2:]) + bytes.fromhex(token_b[2:]))

    # hard coded init code because it's deployed via a contract.  this would require a trace to do it generically
    keccak_init_code = bytes.fromhex(
        "96e8ac4277198ff8b6f785478aa9a39f403cb768dd02cbee326c3e7da348845f"
    )

    return to_checksum(factory_contract.create2(salt, keccak_init_code))
