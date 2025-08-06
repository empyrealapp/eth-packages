from typing import Optional

from eth_account import Account as EthAccount
from eth_typing import HexAddress, HexStr

from .transaction import PreparedTransaction
from .types import HexInteger
from .types.transaction import AuthorizationItem
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


async def prepare_delegation_transaction(
    wallet: BaseWallet,
    to: HexAddress,
    authorization_list: list[AuthorizationItem],
    value: int = 0,
    data: HexStr = HexStr("0x"),
    gas: int = 100000,
    max_fee_per_gas: int = 20000000000,
    max_priority_fee_per_gas: int = 1000000000,
    nonce: Optional[int] = None,
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
        nonce: Transaction nonce (auto-detected from wallet if None)

    Returns:
        PreparedTransaction with type 4 and authorization list
    """
    from .types import HexInteger

    if nonce is None:
        nonce = await wallet[wallet._network].get_nonce()

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


async def sponsor_delegation(
    sponsor_wallet: BaseWallet,
    delegate_wallet: BaseWallet,
    contract_address: HexAddress,
    chain_id: Optional[int] = None,
    nonce: Optional[int] = None,
    value: int = 0,
    data: HexStr = HexStr("0x"),
    gas: int = 100000,
) -> PreparedTransaction:
    """
    Create a sponsored delegation transaction where the sponsor pays gas
    for setting the delegate's code to a contract and executing contract functions.

    Automatically handles network-aware nonce lookup and sponsor == delegate cases.

    Args:
        sponsor_wallet: Wallet that will pay for gas
        delegate_wallet: Wallet that will have its code set to the contract
        contract_address: Contract address to set as the delegate's code
        chain_id: Chain ID for the authorization (auto-detected from sponsor wallet if None)
        nonce: Delegate's current nonce for authorization (auto-detected if None)
        value: ETH value to send
        data: Transaction data (contract function calls)
        gas: Gas limit for the transaction (default: 100000)

    Returns:
        PreparedTransaction ready to be signed by sponsor
    """
    if chain_id is None:
        rpc = sponsor_wallet._rpc()
        chain_id = rpc.network.chain_id

    if nonce is None:
        nonce = await delegate_wallet[sponsor_wallet._network].get_nonce()

    sponsor_is_delegate = sponsor_wallet.address == delegate_wallet.address
    if sponsor_is_delegate:
        auth_nonce = nonce + 1
    else:
        auth_nonce = nonce

    auth_item = create_authorization_item(
        chain_id=chain_id,
        contract_address=contract_address,
        nonce=auth_nonce,
        private_key=delegate_wallet.private_key,
    )

    return await prepare_delegation_transaction(
        wallet=sponsor_wallet,
        to=delegate_wallet.address,
        authorization_list=[auth_item],
        value=value,
        data=data,
        gas=gas,
        nonce=nonce if sponsor_is_delegate else None,
    )
