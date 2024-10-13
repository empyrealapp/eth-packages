from binascii import unhexlify

from eth_rpc import ContractFunc, Network, PreparedTransaction, PrivateKeyWallet
from eth_rpc._transport import _force_get_global_rpc
from eth_rpc.networks import SapphireTestnet
from eth_typing import HexStr

from .data_pack import make_response_async
from .sapphire import SignedArgs, _make_envelope, encrypt_tx_data


async def send_encrypted_call(
    wallet: PrivateKeyWallet,
    invocation: ContractFunc,
    network: type[Network] = SapphireTestnet,
):
    rpc = _force_get_global_rpc(network)
    pk = await rpc.oasis_calldata_public_key()
    c, envelope = _make_envelope(pk, invocation.data)
    response = await make_response_async(
        wallet.address,
        invocation.address,
        invocation.data,
        envelope,
        wallet,
    )
    params = SignedArgs(req=response)

    response = rpc.eth_call.sync(
        params,
    )
    unencrypted = c.decrypt(unhexlify(response[2:]))
    return invocation.func.decode_result(unencrypted.hex())


async def send_encrypted_tx(
    wallet: PrivateKeyWallet,
    invocation: ContractFunc,
    gas_price: int = 100000000000,
    network: type[Network] = SapphireTestnet,
):
    prepared_tx: PreparedTransaction = await invocation.prepare(
        wallet, gas_price=gas_price
    )
    _, prepared_tx.data = await encrypt_tx_data(
        prepared_tx.data,
        network=network,
    )
    signed_tx = wallet.sign_transaction(prepared_tx)
    return await wallet[network].send_raw_transaction(
        HexStr("0x" + signed_tx.raw_transaction)
    )
