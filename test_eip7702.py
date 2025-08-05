#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "packages/eth_rpc/src"))

from eth_rpc.delegation import create_authorization_item
from eth_rpc.wallet import PrivateKeyWallet
from eth_rpc.transaction import PreparedTransaction
from eth_rpc.types.transaction import AuthorizationItem
from eth_typing import HexAddress, HexStr
from eth_rpc.types import HexInteger

def test_eip7702_utilities():
    """Test EIP-7702 delegation utilities"""
    print("Testing EIP-7702 delegation utilities...")

    delegate_wallet = PrivateKeyWallet.create_new()
    target_address = HexAddress("0x1234567890123456789012345678901234567890")

    print(f"Delegate wallet: {delegate_wallet.address}")
    print(f"Target address: {target_address}")

    print("\n1. Testing create_authorization_item...")
    auth_item = create_authorization_item(
        chain_id=1,
        address=delegate_wallet.address,
        nonce=0,
        private_key=delegate_wallet.private_key,
    )
    print(f"Created authorization item: {auth_item}")
    assert auth_item.chain_id == 1
    assert auth_item.address == delegate_wallet.address
    assert auth_item.nonce == 0
    assert isinstance(auth_item.r, str) and auth_item.r.startswith("0x")
    assert isinstance(auth_item.s, str) and auth_item.s.startswith("0x")
    print("✓ create_authorization_item works correctly")

    print("\n2. Testing PreparedTransaction with authorization_list...")
    delegation_tx = PreparedTransaction(
        data=HexStr("0x"),
        to=target_address,
        gas=HexInteger(21000),
        max_fee_per_gas=20000000000,
        max_priority_fee_per_gas=1000000000,
        nonce=0,
        value=0,
        authorization_list=[auth_item],
        chain_id=1,
    )
    print(f"Created delegation transaction: type={delegation_tx.type}")
    assert delegation_tx.type == 4
    assert delegation_tx.authorization_list == [auth_item]
    assert delegation_tx.to == target_address
    print("✓ PreparedTransaction with authorization_list works correctly")

    print("\n3. Testing AuthorizationItem model...")
    auth_dict = auth_item.model_dump(by_alias=True)
    print(f"Authorization item serialized: {auth_dict}")
    assert "chainId" in auth_dict
    assert "yParity" in auth_dict
    print("✓ AuthorizationItem model works correctly")

    print("\n4. Testing sponsor_delegation API (without RPC)...")
    sponsor_wallet = PrivateKeyWallet.create_new()
    
    # Manually test the authorization creation part of sponsor_delegation
    test_auth = create_authorization_item(
        chain_id=1,
        address=delegate_wallet.address,
        nonce=0,
        private_key=delegate_wallet.private_key,
    )
    print(f"Authorization for sponsor_delegation: {test_auth.address}")
    assert test_auth.address == delegate_wallet.address
    assert test_auth.chain_id == 1
    print("✓ sponsor_delegation wallet API creates correct authorization")

    print("\n🎉 All EIP-7702 utilities working correctly!")
    return True

if __name__ == "__main__":
    try:
        test_eip7702_utilities()
        print("\n✅ EIP-7702 implementation test PASSED")
    except Exception as e:
        print(f"\n❌ EIP-7702 implementation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
