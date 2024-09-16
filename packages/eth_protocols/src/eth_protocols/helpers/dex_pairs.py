from itertools import combinations

from eth_protocols.camelot_v3 import CamelotV3Pool
from eth_protocols.uniswap_v2 import V2Pair
from eth_protocols.uniswap_v3 import V3Pool
from eth_rpc.types.primitives import uint24
from eth_rpc.utils import to_checksum
from eth_typeshed.camelot_v3 import CamelotV3Factory
from eth_typeshed.camelot_v3 import CamelotV3Pool as CamelotV3PoolContract
from eth_typeshed.camelot_v3 import GetPoolRequest as CamelotGetPoolRequest
from eth_typeshed.constants import Factories, Tokens
from eth_typeshed.erc20 import OwnerRequest
from eth_typeshed.uniswap_v2 import GetPairRequest, UniswapV2Factory, UniswapV2Pair
from eth_typeshed.uniswap_v3 import GetPoolRequest, UniswapV3Factory, UniswapV3Pool
from eth_typeshed.utils import try_execute_with_setters
from eth_typing import HexAddress
from pydantic import BaseModel


class DexPairHelper(BaseModel):
    @staticmethod
    def find_pair(
        data: dict[HexAddress, list[V2Pair | V3Pool]],
        addr: HexAddress,
        paired_with: HexAddress,
        fee_tiers: list[int],
        factories: list[HexAddress],
    ):
        addr = to_checksum(addr)
        paired_with = to_checksum(paired_with)

        for factory in factories:
            if (
                factory == Factories.for_network().UniswapV2
                or factory == Factories.for_network().pod_factory
            ):
                calls_list = [
                    (
                        UniswapV2Factory(address=factory).get_pair(
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

            if factory == Factories.for_network().UniswapV3:
                for fee in fee_tiers:
                    calls_list.extend(
                        [
                            (
                                UniswapV3Factory(address=factory).get_pool(
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
            if factory == Factories.Arbitrum.Camelot_V3:
                calls_list.extend(
                    [
                        (
                            CamelotV3Factory(address=factory).pool_by_pair(
                                CamelotGetPoolRequest(token_a=addr, token_b=paired_with)
                            ),
                            lambda result, addr=addr, paired_with=paired_with: (  # type: ignore
                                data.setdefault(addr, []).append(
                                    CamelotV3Pool.load_static(
                                        tokena=addr,
                                        tokenb=paired_with,
                                        pair_address=result,
                                    )
                                )
                            ),
                        ),
                    ]
                )
        return calls_list

    @staticmethod
    async def find_all_pairs(
        addresses: list[HexAddress],
        find_pairs: list[HexAddress] = Tokens.for_network().main,
        factories: list[HexAddress] = Factories.for_network().all_factories,
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
                    DexPairHelper.find_pair(
                        data,
                        addr,
                        paired_with,
                        fee_tiers,
                        factories,
                    )
                )
        await try_execute_with_setters(
            calls_with_setters, block_number=block_number or "latest"
        )
        await DexPairHelper.add_reserves_to_pairs(data, block_number=block_number)
        return data

    @staticmethod
    async def find_all_stables_pairs(
        find_pairs: list[HexAddress] = Tokens.for_network().main,
        factories=Factories.for_network().all_factories,
        fee_tiers: list[int] = [500, 3000, 10000],
        block_number: int | None = None,
    ) -> dict[HexAddress, list[V2Pair | V3Pool]]:
        data: dict[HexAddress, list[V2Pair | V3Pool]] = {}
        calls_with_setters = []

        unique_tuples = list(combinations(find_pairs, 2))

        for t in unique_tuples:
            calls_with_setters.extend(
                DexPairHelper.find_pair(
                    data,
                    t[0],
                    t[1],
                    fee_tiers,
                    factories,
                )
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
                                pair.set_reserves(result.reserve0, result.reserve1)
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

                elif isinstance(pair, CamelotV3Pool):
                    calls_with_setters.append(
                        (
                            CamelotV3PoolContract(
                                address=pair.pair_address
                            ).global_state(),
                            lambda result, pair=pair: (pair.set_global_state(result)),
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
