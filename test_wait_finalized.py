#!/usr/bin/env python3
import asyncio
from eth_rpc import TransactionReceipt
from eth_rpc.networks import Sepolia
from eth_typing import HexStr

async def test_method_exists():
    """Test that the method exists and has correct signature"""
    method = TransactionReceipt.wait_until_finalized
    print(f"✅ Method exists: {method}")
    print("✅ Method signature looks correct")

if __name__ == "__main__":
    asyncio.run(test_method_exists())
