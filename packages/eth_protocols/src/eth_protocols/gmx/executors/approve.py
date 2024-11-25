from eth_typing import HexAddress, HexStr

from eth_rpc import PrivateKeyWallet
from eth_rpc.utils import to_checksum
from eth_typeshed.erc20 import ERC20, OwnerSpenderRequest, ApproveRequest


async def check_if_approved(
    wallet: PrivateKeyWallet,
    spender: HexAddress,
    token: HexAddress,
    amount: int,
    max_fee_per_gas: int | None = None,
    approve: bool = True,
):
    if token == "0x47904963fc8b2340414262125aF798B9655E58Cd":
        token = HexAddress(HexStr("0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f"))

    token_checksum_address = to_checksum(token)

    # TODO - for AVAX support this will need to incl WAVAX address
    if token_checksum_address == "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1":
        balance_of = await wallet.balance()
    else:
        balance_of = await ERC20(address=token).balance_of(wallet.address).get()

    if balance_of < amount:
        raise Exception("Insufficient balance!")

    amount_approved = await ERC20(address=token).allowance(
        OwnerSpenderRequest(owner=wallet.address, spender=spender)
    ).get()

    print("Checking coins for approval..")
    if amount_approved < amount and approve:
        print('Approving contract "{}" to spend {} tokens belonging to token address: {}'.format(
            spender, amount, token_checksum_address))

        txn_hash = await ERC20(address=token).approve(
            ApproveRequest(
                spender=spender,
                amount=amount,
            )
        ).execute(wallet, max_fee_per_gas=max_fee_per_gas)

        print("Txn submitted!")
        print("Check status: https://arbiscan.io/tx/{}".format(txn_hash))

    if amount_approved < amount and not approve:
        raise Exception("Token not approved for spend, please allow first!")

    print('Contract "{}" approved to spend {} tokens belonging to token address: {}'.format(
        spender, amount, token_checksum_address))
    print("Coins Approved for spend!")
