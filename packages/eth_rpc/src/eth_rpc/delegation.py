from typing import Optional

from eth_typing import HexAddress, HexStr
from eth_account import Account as EthAccount

from .types import HexInteger
from .types.transaction import AuthorizationItem
from .transaction import PreparedTransaction
from .wallet import BaseWallet


def create_authorization_item(
    chain_id: int,
    address: HexAddress,
    nonce: int,
    private_key: HexStr,
) -> AuthorizationItem:
    """
    Create a signed authorization item for EIP-7702 delegation.

    Args:
        chain_id: The chain ID for the authorization
        address: The address to authorize delegation to
        nonce: The nonce for this authorization
        private_key: Private key to sign the authorization

    Returns:
        Signed AuthorizationItem
    """
    auth = {
        "chainId": chain_id,
        "address": address,
        "nonce": nonce,
    }

    account = EthAccount.from_key(private_key)
    signed_auth = account.sign_authorization(auth)

    return AuthorizationItem(
        chain_id=HexInteger(chain_id),
        address=address,
        nonce=HexInteger(nonce),
        y_parity=HexInteger(signed_auth.y_parity),
        r=HexStr(hex(signed_auth.r)),
        s=HexStr(hex(signed_auth.s)),
    )


def prepare_delegation_transaction(
    wallet: BaseWallet,
    to: HexAddress,
    authorization_list: list[AuthorizationItem],
    value: int = 0,
    data: HexStr = HexStr("0x"),
    gas: Optional[int] = None,
    max_fee_per_gas: Optional[int] = None,
    max_priority_fee_per_gas: Optional[int] = None,
    nonce: Optional[int] = None,
) -> PreparedTransaction:
    """
    Prepare an EIP-7702 delegation transaction.

    Args:
        wallet: Wallet to send the transaction from
        to: Target address for the transaction
        authorization_list: List of authorization items for delegation
        value: ETH value to send (default: 0)
        data: Transaction data (default: "0x")
        gas: Gas limit (auto-estimated if None)
        max_fee_per_gas: Maximum fee per gas
        max_priority_fee_per_gas: Maximum priority fee per gas
        nonce: Transaction nonce (auto-determined if None)

    Returns:
        PreparedTransaction with type 4 and authorization list
    """
    base_tx = wallet.prepare(
        to=to,
        value=value,
        data=data,
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        nonce=nonce,
    )

    if gas is not None:
        base_tx.gas = gas

    base_tx.authorization_list = authorization_list
    base_tx.type = 4

    return base_tx


def sponsor_delegation(
    sponsor_wallet: BaseWallet,
    delegatee_address: HexAddress,
    delegatee_private_key: HexStr,
    target_address: HexAddress,
    chain_id: int,
    nonce: int,
    value: int = 0,
    data: HexStr = HexStr("0x"),
) -> PreparedTransaction:
    """
    Create a sponsored delegation transaction where the sponsor pays gas
    for a delegated call from the delegatee.

    Args:
        sponsor_wallet: Wallet that will pay for gas
        delegatee_address: Address that will be delegated to
        delegatee_private_key: Private key of delegatee to sign authorization
        target_address: Target address for the delegated call
        chain_id: Chain ID for the authorization
        nonce: Nonce for the authorization
        value: ETH value to send
        data: Transaction data

    Returns:
        PreparedTransaction ready to be signed by sponsor
    """
    auth_item = create_authorization_item(
        chain_id=chain_id,
        address=delegatee_address,
        nonce=nonce,
        private_key=delegatee_private_key,
    )

    return prepare_delegation_transaction(
        wallet=sponsor_wallet,
        to=target_address,
        authorization_list=[auth_item],
        value=value,
        data=data,
    )
