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

from eth_rpc import TransactionReceipt
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
        address public lastToEverUpdate;

        function increment() external {
            count++;
            lastToEverUpdate = msg.sender;
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

    counter_address = HexAddress("0x0271297dcc0CceA3640bbaf34801025E6F63F448")
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
    
    print("   Using the enhanced execute method with delegation...")
    tx_hash = await counter.increment().execute(
        wallet=sponsor_wallet,
        delegate_wallet=delegate_wallet,
    )
    print(f"   ✅ Transaction sent using enhanced execute method: {tx_hash}")
    
    print(f"\n5. Demonstrating simple wallet delegation (without contract data)...")
    print("   Using the wallet delegation utility method...")
    
    simple_delegate = PrivateKeyWallet.create_new()
    print(f"   New delegate wallet: {simple_delegate.address}")
    
    delegation_tx_hash = await simple_delegate.delegate_to_contract(
        sponsor_wallet=sponsor_wallet,
        contract_address=counter_address,
    )
    print(f"   Delegation transaction sent: {delegation_tx_hash}")
    
    print(f"\n🎉 EIP-7702 delegation workflow complete!")
    print("   Both utility methods successfully demonstrated.")

    print("Waiting for transaction to be mined...")
    while True:
        receipt = await TransactionReceipt[Sepolia].get_by_hash(tx_hash)
        if receipt:
            if receipt.status == 1:
                print("Transaction mined successfully")
                break
            if receipt.status == 0:
                raise Exception(f"Transaction failed: {receipt.status}")
        await asyncio.sleep(4)

    counter = Counter[Sepolia](address=delegate_wallet.address)
    print(f"   Counter.number: {await counter.number().get()}")
    print(f"   Counter.last_to_ever_update: {await counter.last_to_ever_update().get()}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
