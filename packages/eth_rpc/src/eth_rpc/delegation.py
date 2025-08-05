from typing import Optional

from eth_typing import HexAddress, HexStr
from eth_account import Account as EthAccount

from .types import HexInteger
from .types.transaction import AuthorizationItem
from .transaction import PreparedTransaction
from .wallet import BaseWallet


def create_authorization_item(
    chain_id: int,
    contract_address: HexAddress,
    nonce: int,
    private_key: HexStr,
) -> AuthorizationItem:
    """
    Create a signed authorization item for EIP-7702 delegation.

    Args:
        chain_id: The chain ID for the authorization
        contract_address: The contract address to set as the EOA's code
        nonce: The nonce for this authorization
        private_key: Private key of the EOA to sign the authorization

    Returns:
        Signed AuthorizationItem
    """
    auth = {
        "chainId": chain_id,
        "address": contract_address,
        "nonce": nonce,
    }

    account = EthAccount.from_key(private_key)
    signed_auth = account.sign_authorization(auth)

    return AuthorizationItem(
        chain_id=HexInteger(chain_id),
        address=contract_address,
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
    gas: int = 100000,
    max_fee_per_gas: int = 20000000000,
    max_priority_fee_per_gas: int = 1000000000,
    nonce: int = 0,
) -> PreparedTransaction:
    """
    Prepare an EIP-7702 delegation transaction.

    Args:
        wallet: Wallet to send the transaction from (sponsor)
        to: Target address for the transaction (delegate's EOA address)
        authorization_list: List of authorization items for setting EOA code
        value: ETH value to send (default: 0)
        data: Transaction data for contract function calls (default: "0x")
        gas: Gas limit (auto-estimated if None)
        max_fee_per_gas: Maximum fee per gas
        max_priority_fee_per_gas: Maximum priority fee per gas
        nonce: Transaction nonce (auto-determined if None)

    Returns:
        PreparedTransaction with type 4 and authorization list
    """
    from .types import HexInteger
    
    base_tx = PreparedTransaction(
        data=data,
        to=to,
        gas=HexInteger(gas),
        max_fee_per_gas=max_fee_per_gas,
        max_priority_fee_per_gas=max_priority_fee_per_gas,
        nonce=nonce,
        value=value,
        authorization_list=authorization_list,
        chain_id=authorization_list[0].chain_id,
        type=4,
    )

    return base_tx


def sponsor_delegation(
    sponsor_wallet: BaseWallet,
    delegate_wallet: BaseWallet,
    contract_address: HexAddress,
    chain_id: int,
    nonce: int,
    value: int = 0,
    data: HexStr = HexStr("0x"),
    gas: int = 100000,
) -> PreparedTransaction:
    """
    Create a sponsored delegation transaction where the sponsor pays gas
    for setting the delegate's code to a contract and executing contract functions.

    Args:
        sponsor_wallet: Wallet that will pay for gas
        delegate_wallet: Wallet that will have its code set to the contract
        contract_address: Contract address to set as the delegate's code
        chain_id: Chain ID for the authorization
        nonce: Nonce for the authorization
        value: ETH value to send
        data: Transaction data (contract function calls)
        gas: Gas limit for the transaction (default: 100000)

    Returns:
        PreparedTransaction ready to be signed by sponsor
    """
    auth_item = create_authorization_item(
        chain_id=chain_id,
        contract_address=contract_address,
        nonce=nonce,
        private_key=delegate_wallet.private_key,
    )

    return prepare_delegation_transaction(
        wallet=sponsor_wallet,
        to=delegate_wallet.address,
        authorization_list=[auth_item],
        value=value,
        data=data,
        gas=gas,
    )
