from eth_protocols.uniswap_v2 import V2Pair
from eth_protocols.uniswap_v3 import V3Pool
from eth_rpc.types.primitives import uint24
from eth_typeshed.constants import Factories, Tokens
from eth_typeshed.erc20 import OwnerRequest
from eth_typeshed.uniswap_v2 import GetPairRequest, UniswapV2Factory, UniswapV2Pair
from eth_typeshed.uniswap_v3 import GetPoolRequest, UniswapV3Factory, UniswapV3Pool
from eth_typeshed.utils import try_execute_with_setters
from eth_typing import HexAddress
from pydantic import BaseModel


class DexPairHelper(BaseModel):
    @staticmethod
    async def find_all_pairs(
        addresses: list[HexAddress],
        find_pairs: list[HexAddress] = Tokens.Ethereum.main,
        uniswap_v2_factory_address: HexAddress = Factories.Ethereum.UniswapV2,
        uniswap_v3_factory_address: HexAddress = Factories.Ethereum.UniswapV3,
        fee_tiers: list[int] = [500, 3000, 10000],
        block_number: int | None = None,
    ) -> dict[HexAddress, list[V2Pair | V3Pool]]:
        data: dict[HexAddress, list[V2Pair | V3Pool]] = {}
        calls_with_setters = []
        for addr in addresses:
            if addr not in data:
                data[addr] = []
            for paired_with in find_pairs:
                calls_with_setters.extend(
                    [
                        (
                            UniswapV2Factory(
                                address=uniswap_v2_factory_address
                            ).get_pair(
                                GetPairRequest(token_a=addr, token_b=paired_with)
                            ),
                            lambda result, addr=addr, paired_with=paired_with: (
                                data.setdefault(addr, []).append(
                                    V2Pair.load_static(
                                        pair_address=result,
                                        tokena=addr,
                                        tokenb=paired_with,
                                    )
                                )
                            ),
                        ),
                    ]
                )

                for fee in fee_tiers:
                    calls_with_setters.extend(
                        [
                            (
                                UniswapV3Factory(
                                    address=uniswap_v3_factory_address
                                ).get_pool(
                                    GetPoolRequest(
                                        token_a=addr,
                                        token_b=paired_with,
                                        fee=uint24(fee),
                                    )
                                ),
                                lambda result, addr=addr, paired_with=paired_with, fee=fee: (  # type: ignore
                                    data.setdefault(addr, []).append(
                                        V3Pool.load_static(
                                            tokena=addr,
                                            tokenb=paired_with,
                                            pair_address=result,
                                            fee=fee,
                                        )
                                    )
                                ),
                            ),
                        ]
                    )
        await try_execute_with_setters(
            calls_with_setters, block_number=block_number or "latest"
        )
        await DexPairHelper.add_reserves_to_pairs(data, block_number=block_number)
        return data

    @staticmethod
    async def add_reserves_to_pairs(
        data: dict[HexAddress, list[V2Pair | V3Pool]],
        block_number: int | None = None,
    ):
        calls_with_setters = []

        for pairs in data.values():
            for pair in pairs:
                if isinstance(pair, V2Pair):
                    calls_with_setters.append(
                        (
                            UniswapV2Pair(address=pair.pair_address).get_reserves(),
                            lambda result, pair=pair: (
                                pair.set_reserves(result[0], result[1])
                            ),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token0.raw.decimals(),
                            lambda result, pair=pair: (
                                pair.token0.set_decimals(result)
                            ),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token0.raw.symbol(),
                            lambda result, pair=pair: (pair.token0.set_symbol(result)),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token1.raw.decimals(),
                            lambda result, pair=pair: (
                                pair.token1.set_decimals(result)
                            ),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token1.raw.symbol(),
                            lambda result, pair=pair: (pair.token1.set_symbol(result)),
                        )
                    )
                elif isinstance(pair, V3Pool):
                    calls_with_setters.append(
                        (
                            UniswapV3Pool(address=pair.pair_address).slot0(),
                            lambda result, pair=pair: (pair.set_slot0(result)),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token0.raw.balance_of(
                                OwnerRequest(owner=pair.pair_address)
                            ),
                            lambda result, pair=pair: (pair.set_reserve0(result)),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token1.raw.balance_of(
                                OwnerRequest(owner=pair.pair_address)
                            ),
                            lambda result, pair=pair: (pair.set_reserve1(result)),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token0.raw.decimals(),
                            lambda result, pair=pair: (
                                pair.token0.set_decimals(result)
                            ),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token0.raw.symbol(),
                            lambda result, pair=pair: (pair.token0.set_symbol(result)),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token1.raw.decimals(),
                            lambda result, pair=pair: (
                                pair.token1.set_decimals(result)
                            ),
                        )
                    )
                    calls_with_setters.append(
                        (
                            pair.token1.raw.symbol(),
                            lambda result, pair=pair: (pair.token1.set_symbol(result)),
                        )
                    )
        await try_execute_with_setters(
            calls_with_setters, block_number=block_number or "latest"
        )
