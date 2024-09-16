from decimal import Decimal
from typing import cast

from eth_protocols.tokens import ERC20
from eth_protocols.types import DexPair
from eth_rpc.types import BLOCK_STRINGS, MaybeAwaitable
from eth_rpc.utils import to_checksum
from eth_typeshed.camelot_v3 import CamelotV3Pool, GlobalState
from eth_typeshed.erc20 import OwnerRequest
from eth_typeshed.multicall import multicall
from eth_typing import HexAddress
from pydantic import PrivateAttr

Q192 = Decimal(2**192)


class CamelotV3Pool(DexPair):
    _contract: CamelotV3Pool = PrivateAttr()

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
        return cls(
            token0=ERC20(address=token0),  # type: ignore
            token1=ERC20(address=token1),  # type: ignore
            pair_address=pair_address,
        )

    @classmethod
    async def load_pair(
        cls,
        pair_address: HexAddress,
    ):
        # TODO: type hints don't work with pydantic validators
        _contract = CamelotV3Pool(address=pair_address)
        token0, token1, fee = await multicall.execute(
            _contract.token0(),
            _contract.token1(),
        )

        return cls(
            token0=ERC20(address=token0),  # type: ignore
            token1=ERC20(address=token1),  # type: ignore
            pair_address=pair_address,  # type: ignore
        )

    def set_global_state(self, global_stage: GlobalState):
        self._global_state = global_stage

    def set_reserve0(self, reserve: int):
        self._reserve0 = reserve

    def set_reserve1(self, reserve: int):
        self._reserve1 = reserve

    def get_price(
        self,
        token: HexAddress,
        block_number: int | BLOCK_STRINGS = "latest",
    ) -> Decimal:
        token = to_checksum(token)
        assert token == self.token0.address or token == self.token1.address

        if block_number:
            global_state = self._contract.global_state().get(block_number=block_number)
        else:
            global_state = self._global_state

        sqrt_price = global_state.price

        return self.sqrt_price_x96_to_token_prices(
            sqrt_price,
            self.token0.sync.decimals(),
            self.token1.sync.decimals(),
            token == self.token0.address,
        )

    def get_other_token(self, token: HexAddress) -> HexAddress:
        token = to_checksum(token)
        if token == self.token0.address:
            return self.token1.address
        elif token == self.token1.address:
            return self.token0.address
        else:
            raise ValueError(
                f"{token=} cannot be found {self.token0.address=} {self.token1.address=}"
            )

    def get_reserves(
        self, block_number: int | BLOCK_STRINGS = "latest", sync: bool = False
    ) -> MaybeAwaitable[tuple[int, int]]:
        if sync:
            token0_reserves, token1_reserves = multicall.execute(
                *self._construct_pair_balance_request(), sync=True
            )
            self.set_reserves(token0_reserves, token1_reserves)
            return token0_reserves, token1_reserves

        async def get_reserves() -> tuple[int, int]:
            token0_reserves = await self.token0.balance_of(
                self.pair_address, block_number=block_number
            )
            token1_reserves = await self.token1.balance_of(
                self.pair_address, block_number=block_number
            )
            self.set_reserves(token0_reserves, token1_reserves)
            return token0_reserves, token1_reserves

        return get_reserves

    @staticmethod
    def sqrt_price_x96_to_token_prices(
        sqrt_price_x96: int,
        token0_decimals: int,
        token1_decimals: int,
        token0: bool = True,
    ) -> Decimal:
        num = Decimal(sqrt_price_x96 * sqrt_price_x96)
        price1: Decimal = (
            (num / Q192)
            * (Decimal(10) ** token0_decimals)
            / (Decimal(10) ** token1_decimals)
        )
        if token0:
            return Decimal(price1)
        return Decimal(1) / price1

    def _construct_pair_balance_request(self):
        return [
            self.token0.raw.balance_of(
                OwnerRequest(
                    self.pair_address,
                )
            ),
            self.token1.raw.balance_of(
                OwnerRequest(
                    self.pair_address,
                )
            ),
        ]

    @classmethod
    async def get_all_reserves(
        self, pools: list["V3Pool"], block_number: int | BLOCK_STRINGS = "latest"
    ) -> list[tuple[int, int]]:
        pool_calls = []
        for pool in pools:
            pool_calls.extend(pool._construct_pair_balance_request())
        reserves = cast(
            list[int],
            await multicall.execute(
                *pool_calls,
                block_number=block_number,
            ),
        )
        return [(reserves[i], reserves[i + 1]) for i in range(0, len(reserves), 2)]
