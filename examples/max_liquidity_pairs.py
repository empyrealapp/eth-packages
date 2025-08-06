"""
Uniswap V3 Liquidity Analysis Example

This example demonstrates how to:
1. Find all Uniswap V3 pools containing a specific token
2. Analyze liquidity depth across pools to find the most liquid pair
3. Use event filtering and multicall for efficient data retrieval

Key concepts:
- Historical event analysis for pool discovery
- Multicall for efficient batch balance queries
- Liquidity analysis for DeFi applications
"""

import asyncio
import os

from eth_rpc import set_alchemy_key
from eth_rpc.utils import address_to_topic
from eth_typeshed.constants import Factories
from eth_typeshed.erc20 import ERC20
from eth_typeshed.multicall import multicall
from eth_typeshed.uniswap_v3 import V3PoolCreatedEvent, V3PoolCreatedEventType
from eth_typing import HexAddress, HexStr


async def get_all_uniswap_v3_pools(token_address: HexAddress):
    """
    Discover all Uniswap V3 pools containing a specific token.
    
    This function searches through PoolCreated events from the Uniswap V3 factory
    to find all pools where the token appears as either token0 or token1.
    
    Args:
        token_address: Address of the token to search for
        
    Returns:
        List of V3PoolCreatedEventType objects representing all pools containing the token
        
    Note:
        - topic1 corresponds to token0 in the pool
        - topic2 corresponds to token1 in the pool
        - We search both positions to find all relevant pools
        - This searches from genesis block, so it may take time for popular tokens
    """
    all_pools: list[V3PoolCreatedEventType] = []

    print(f"Searching for pools where {token_address} is token0...")
    async for event_data in V3PoolCreatedEvent.set_filter(
        addresses=[Factories.Ethereum.UniswapV3],
        topic1=address_to_topic(token_address),
    ).backfill():
        all_pools.append(event_data.event)

    print(f"Searching for pools where {token_address} is token1...")
    async for event_data in V3PoolCreatedEvent.set_filter(
        addresses=[Factories.Ethereum.UniswapV3],
        topic1=None,  # Don't filter on token0
        topic2=address_to_topic(token_address),
    ).backfill():
        all_pools.append(event_data.event)
    
    print(f"Found {len(all_pools)} total pools containing {token_address}")
    return all_pools


async def get_uniswap_v3_max_liquidity_pair(token_address: HexAddress):
    """
    Find the Uniswap V3 pool with the highest liquidity for a given token.
    
    This function analyzes all pools containing the token and determines
    which has the most liquidity by checking the token balance in each pool.
    
    Args:
        token_address: Address of the token to analyze
        
    Returns:
        Tuple of (pool_info, token_balance) for the pool with highest liquidity
        
    Note:
        - Uses multicall for efficient batch balance queries
        - Liquidity is measured by token balance in the pool
        - This is a simplified metric - actual liquidity depends on price ranges
    """
    print(f"Analyzing liquidity for token {token_address}...")
    
    token = ERC20(address=token_address)
    
    all_pools: list[V3PoolCreatedEventType] = await get_all_uniswap_v3_pools(
        token_address
    )
    
    if not all_pools:
        raise ValueError(f"No Uniswap V3 pools found for token {token_address}")

    print(f"Checking token balances across {len(all_pools)} pools...")
    
    # Batch query token balances for all pools using multicall
    reserves = await multicall.execute(
        *[token.balance_of(pool.pool) for pool in all_pools]
    )

    pool_reserves = list(zip(all_pools, reserves))
    pool_reserves.sort(key=lambda x: x[1], reverse=True)
    
    max_liquidity_pool, max_reserve = pool_reserves[0]
    
    print(f"Highest liquidity pool: {max_liquidity_pool.pool}")
    print(f"Token balance: {max_reserve:,}")
    
    return max_liquidity_pool, max_reserve


async def analyze_token_liquidity():
    """
    Example analysis of PEPE token liquidity on Uniswap V3.
    
    This demonstrates the complete workflow for finding the most liquid
    trading pair for a token, which is useful for:
    - Price discovery and trading
    - Liquidity provision decisions
    - Market analysis and monitoring
    """
    pepe_address = HexAddress(HexStr("0x6982508145454Ce325dDbE47a25d4ec3d2311933"))
    
    try:
        print("=" * 60)
        print("UNISWAP V3 LIQUIDITY ANALYSIS")
        print("=" * 60)
        print(f"Analyzing token: {pepe_address}")
        print("This may take a few minutes for the first run...\n")
        
        max_liquidity_pool, reserve_balance = await get_uniswap_v3_max_liquidity_pair(pepe_address)
        
        print("\n" + "=" * 60)
        print("RESULTS")
        print("=" * 60)
        print(f"Most liquid pool: {max_liquidity_pool.pool}")
        print(f"Token0: {max_liquidity_pool.token0}")
        print(f"Token1: {max_liquidity_pool.token1}")
        print(f"Fee tier: {max_liquidity_pool.fee}")
        print(f"PEPE balance in pool: {reserve_balance:,}")
        
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure ALCHEMY_KEY environment variable is set")
        print("2. Check that the token address is valid")
        print("3. Verify network connectivity")


if __name__ == "__main__":
    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    
    asyncio.run(analyze_token_liquidity())
