"""
Token Balance Discovery Example

This example demonstrates how to:
1. Discover all tokens an address has interacted with by analyzing Transfer events
2. Get current balances for all discovered tokens using multicall for efficiency
3. Handle both incoming and outgoing transfers to build a complete token list

Key concepts:
- Event filtering and historical analysis
- Multicall for efficient batch operations
- Topic filtering for indexed event parameters
"""

from eth_rpc import EventData
from eth_rpc.types import BlockReference, primitives
from eth_rpc.utils import address_to_topic
from eth_typeshed.erc20 import ERC20, TransferEvent, TransferEventType
from eth_typeshed.multicall import multicall
from eth_typing import HexAddress, HexStr


async def get_tokens_held(address: HexAddress, start_block=0):
    """
    Discover all tokens an address has interacted with by analyzing Transfer events.
    
    This function searches for both incoming and outgoing transfers to build
    a comprehensive list of tokens the address has held at some point.
    
    Args:
        address: The address to analyze
        start_block: Starting block for historical analysis (0 = from genesis)
        
    Returns:
        Set of token contract addresses that have been transferred to/from the address
        
    Note:
        - topic1 = sender address (outgoing transfers)
        - topic2 = recipient address (incoming transfers)
        - We search both to catch all token interactions
    """
    topic = address_to_topic(address)
    transfers: list[EventData[TransferEventType]] = []
    
    async for event in TransferEvent.set_filter(topic1=topic).backfill(start_block):
        transfers.append(event)
    
    async for event in TransferEvent.set_filter(topic1=None, topic2=topic).backfill(
        start_block
    ):
        transfers.append(event)

    tokens = set([event.log.address for event in transfers])

    return tokens


async def get_balance_at_block(
    address: HexAddress,
    tokens: list[HexAddress],
    block_number: BlockReference = "latest",
):
    """
    Get token balances for multiple tokens at a specific block using multicall.
    
    This function efficiently batches multiple balance_of calls into a single
    RPC request, significantly reducing latency compared to individual calls.
    
    Args:
        address: Address to check balances for
        tokens: List of token contract addresses
        block_number: Block number or tag ("latest", "pending", etc.)
        
    Returns:
        Dictionary mapping token addresses to their balances (only non-zero balances)
        
    Note:
        - Uses try_execute to handle failed calls gracefully
        - Filters out zero balances and failed calls
        - Much more efficient than individual RPC calls
    """
    calls = [
        ERC20(address=token_address).balance_of(primitives.address(address))
        for token_address in tokens
    ]
    
    results = await multicall.try_execute(*calls, block_number=block_number)
    
    return {
        token_addr: balance.result
        for token_addr, balance in zip(tokens, results)
        if balance.success and balance.result
    }


async def get_all_balances(address: HexAddress):
    """
    Complete workflow: discover tokens and get current balances.
    
    This combines token discovery and balance checking into a single
    convenient function that returns all current token holdings.
    
    Args:
        address: Address to analyze
        
    Returns:
        Dictionary of token addresses to current balances
    """
    tokens = await get_tokens_held(address)
    
    return await get_balance_at_block(address, list(tokens))


if __name__ == "__main__":
    import asyncio
    import os

    from eth_rpc import set_alchemy_key

    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    
    binance_wallet = HexAddress(HexStr("0xf977814e90da44bfa03b6295a0616a897441acec"))
    
    async def main():
        print(f"Analyzing token holdings for {binance_wallet}...")
        print("This may take a while as we scan historical transfer events...\n")
        
        try:
            balances = await get_all_balances(binance_wallet)
            
            print(f"Found {len(balances)} tokens with non-zero balances:")
            print("-" * 60)
            
            sorted_balances = sorted(
                balances.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            for token_address, balance in sorted_balances[:10]:  # Show top 10
                print(f"{token_address}: {balance:,}")
                
            if len(sorted_balances) > 10:
                print(f"... and {len(sorted_balances) - 10} more tokens")
                
        except Exception as e:
            print(f"Error analyzing balances: {e}")
            print("Make sure you have a valid ALCHEMY_KEY environment variable set")
    
    asyncio.run(main())
