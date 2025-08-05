#!/usr/bin/env python3
"""
EIP-7702 Delegation Example: Counter Contract

This example demonstrates how to use EIP-7702 delegation utilities to sponsor
a delegated call to a Counter contract's increment method.

Usage:
    export DELEGATE_PRIVATE_KEY="0x..."
    python example_eip7702.py

The workflow:
1. Sponsor wallet pays gas for the transaction
2. Delegate wallet authorizes the delegation via EIP-7702
3. Counter contract's increment method is called on behalf of the delegate
4. The delegate's account code is temporarily set to the Counter contract
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages/eth_rpc/src"))

from eth_rpc.contract import ProtocolBase, ContractFunc
from eth_rpc.delegation import sponsor_delegation
from eth_rpc.wallet import PrivateKeyWallet
from eth_rpc.types import NoArgs
from eth_typing import HexAddress, HexStr


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
    increment: ContractFunc[NoArgs, None] = "increment"


def main():
    """Demonstrate EIP-7702 delegation workflow with Counter contract"""
    print("🔗 EIP-7702 Delegation Example: Counter Contract")
    print("=" * 50)
    
    delegate_private_key = os.getenv("DELEGATE_PRIVATE_KEY")
    if not delegate_private_key:
        print("❌ Error: DELEGATE_PRIVATE_KEY environment variable not set")
        print("Usage: export DELEGATE_PRIVATE_KEY='0x...' && python example_eip7702.py")
        sys.exit(1)
    
    print("\n1. Setting up wallets...")
    sponsor_wallet = PrivateKeyWallet.create_new()
    delegate_wallet = PrivateKeyWallet(HexStr(delegate_private_key))
    
    print(f"   Sponsor wallet: {sponsor_wallet.address}")
    print(f"   Delegate wallet: {delegate_wallet.address}")
    
    counter_address = HexAddress("0x1234567890123456789012345678901234567890")
    print(f"   Counter contract: {counter_address}")
    
    print("\n2. Creating Counter contract instance...")
    counter = Counter(counter_address)
    print(f"   Counter.increment function: {counter.increment}")
    
    print("\n3. Preparing increment call...")
    increment_call_data = counter.increment().data
    print(f"   Increment call data: {increment_call_data}")
    
    # Create sponsored delegation transaction
    print("\n4. Creating sponsored delegation transaction...")
    print("   This transaction will:")
    print("   - Be paid for by the sponsor wallet")
    print("   - Temporarily delegate the delegate's account to the Counter contract")
    print("   - Call the increment method on behalf of the delegate")
    
    sponsored_tx = sponsor_delegation(
        sponsor_wallet=sponsor_wallet,
        delegate_wallet=delegate_wallet,
        target_address=counter_address,
        chain_id=1,  # Ethereum mainnet
        nonce=0,     # Delegate's authorization nonce
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
    print("   - The delegate's account will temporarily become the Counter contract")
    print("   - The increment() method will be called")
    print("   - The sponsor pays all gas fees")
    print("   - The delegate's counter will be incremented")
    
    print(f"\n🎉 EIP-7702 delegation workflow complete!")
    print("   Transaction is ready to be signed by sponsor and submitted to the network.")
    
    return sponsored_tx


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
