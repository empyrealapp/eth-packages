import asyncio
from eth_typing import HexAddress, HexStr
import os

from eth_rpc import set_alchemy_key
from eth_rpc.utils import address_to_topic
from eth_typeshed.erc20 import ERC20
from eth_typeshed.multicall import multicall
from eth_typeshed.uniswap_v3 import V3PoolCreatedEvent, V3PoolCreatedEventType
from eth_typeshed.constants import Factories


async def get_all_uniswap_v3_pools(token_address: HexAddress):
    """
    Get All Pools for a token address on UniswapV3
    """
    all_pools: list[V3PoolCreatedEventType] = []

    # get all pairs created where the token is topic1
    async for event_data in V3PoolCreatedEvent.set_filter(
        addresses=[Factories.Ethereum.UniswapV3],
        topic1=address_to_topic(token_address),
    ).backfill():
        all_pools.append(event_data.event)

    # get all pairs created where the token is topic2
    async for event_data in V3PoolCreatedEvent.set_filter(
        addresses=[Factories.Ethereum.UniswapV3],
        topic1=None,
        topic2=address_to_topic(token_address),
    ).backfill():
        all_pools.append(event_data.event)
    return all_pools


async def get_uniswap_v3_max_liquidity_pair(token_address: HexAddress):
    """
    A helper function to get the highest liquidity pair on UniswapV3 for a token.
    """
    token = ERC20(address=token_address)
    all_pools: list[V3PoolCreatedEventType] = await get_all_uniswap_v3_pools(token_address)

    # get the token balance of each pool to find the deepest liquidity pool
    reserves = await multicall.execute(*[token.balance_of(pool.pool) for pool in all_pools])

    # zip together the pool with the reserves and find the highest reserve balance
    max_reserve = sorted(
        zip(all_pools, reserves),
        reverse=True,
        key=lambda x: x[1],
    )[0]

    # return the row with the hightest reserve balance
    return max_reserve


async def amain():
    pepe_address = HexAddress(HexStr("0x6982508145454Ce325dDbE47a25d4ec3d2311933"))
    max_liquidity_pair_v3 = await get_uniswap_v3_max_liquidity_pair(pepe_address)
    print("max liquidity pool:", max_liquidity_pair_v3)


if __name__ == "__main__":
    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    asyncio.run(amain())
