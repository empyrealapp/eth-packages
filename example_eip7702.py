#!/usr/bin/env python3
"""
EIP-7702 Delegation Example: Counter Contract

This example demonstrates how to use EIP-7702 delegation utilities to sponsor
a delegated call to a Counter contract's increment method.

Usage:
    export SPONSOR_PRIVATE_KEY="0x..."
    python example_eip7702.py

The workflow:
1. Sponsor wallet (with existing funds) pays gas for the transaction
2. Delegate wallet (randomly created) authorizes setting its code to the Counter contract via EIP-7702
3. Counter contract's increment method is executed on the delegate's account
4. The delegate's account code is set to the Counter contract during execution
"""

import asyncio
import sys
import os
from typing import Annotated

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages/eth_rpc/src"))

from eth_rpc.contract import ProtocolBase, ContractFunc
from eth_rpc.delegation import sponsor_delegation
from eth_rpc.wallet import PrivateKeyWallet
from eth_rpc.types import METHOD, Name, NoArgs
from eth_typing import HexAddress, HexStr
from eth_rpc.networks import Sepolia


class Counter(ProtocolBase):
    """
    Example Counter contract with increment method.
    
    Solidity equivalent:
    contract Counter {
        uint256 public count;
        
        function increment() external {
            count++;
        }
    }
    """
    increment: ContractFunc[NoArgs, None] = METHOD
    number: ContractFunc[NoArgs, int] = METHOD
    last_to_ever_update: Annotated[
        ContractFunc[NoArgs, HexAddress],
        Name("lastToEverUpdate"),
    ] = METHOD


async def main():
    """Demonstrate EIP-7702 delegation workflow with Counter contract"""
    print("🔗 EIP-7702 Delegation Example: Counter Contract")
    print("=" * 50)
    
    sponsor_private_key = os.getenv("SPONSOR_PRIVATE_KEY")
    
    if not sponsor_private_key:
        print("❌ Error: SPONSOR_PRIVATE_KEY environment variable not set")
        print("Usage: export SPONSOR_PRIVATE_KEY='0x...' && python example_eip7702.py")
        sys.exit(1)
    
    print("\n1. Setting up wallets...")
    sponsor_wallet = PrivateKeyWallet[Sepolia](private_key=HexStr(sponsor_private_key))
    delegate_wallet = PrivateKeyWallet.create_new()
    
    print(f"   Sponsor wallet: {sponsor_wallet.address} (has funds, pays gas fees)")
    print(f"   Delegate wallet: {delegate_wallet.address} (randomly created, authorizes code setting)")
    
    counter_address = HexAddress("0x1234567890123456789012345678901234567890")
    print(f"   Counter contract: {counter_address}")
    
    print("\n2. Creating Counter contract instance...")
    counter = Counter[Sepolia](address=counter_address)
    print(f"   Counter.increment function: {counter.increment}")
    
    print("\n3. Preparing increment call...")
    increment_call_data = counter.increment().data
    print(f"   Increment call data: {increment_call_data}")
    
    # Create sponsored delegation transaction
    print("\n4. Creating sponsored delegation transaction...")
    print("   This transaction will:")
    print("   - Be paid for by the sponsor wallet (which has ETH for gas)")
    print("   - Set the delegate's account code to the Counter contract")
    print("   - Execute the increment method within the same transaction")
    print("   - Automatically handle network-aware nonce lookup")
    
    sponsored_tx = await sponsor_delegation(
        sponsor_wallet=sponsor_wallet,
        delegate_wallet=delegate_wallet,
        contract_address=counter_address,
        value=0,     # No ETH transfer
        data=increment_call_data,  # Counter.increment() call
    )
    
    print(f"   ✅ Created EIP-7702 delegation transaction:")
    print(f"      Type: {sponsored_tx.type} (EIP-7702)")
    print(f"      To: {sponsored_tx.to}")
    print(f"      Data: {sponsored_tx.data}")
    print(f"      Authorization list: {len(sponsored_tx.authorization_list)} item(s)")
    
    auth_item = sponsored_tx.authorization_list[0]
    print(f"\n5. Authorization details:")
    print(f"   Chain ID: {auth_item.chain_id}")
    print(f"   Delegate address: {auth_item.address}")
    print(f"   Nonce: {auth_item.nonce}")
    print(f"   Signature (r): {auth_item.r[:10]}...")
    print(f"   Signature (s): {auth_item.s[:10]}...")
    
    print(f"\n6. Transaction ready for execution:")
    print("   The sponsor can now sign and submit this transaction.")
    print("   When executed:")
    print("   - The delegate's account code will be set to the Counter contract")
    print("   - The increment() method will be executed on the delegate's account")
    print("   - The sponsor pays all gas fees")
    print("   - The delegate's counter state will be incremented")
    
    print(f"\n🎉 EIP-7702 delegation workflow complete!")
    print("   Transaction is ready to be signed by sponsor and submitted to the network.")
    
    signed_tx = sponsor_wallet.sign_transaction(sponsored_tx)
    await sponsor_wallet.send_raw_transaction(
        HexStr("0x" + signed_tx.raw_transaction),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
