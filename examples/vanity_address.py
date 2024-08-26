from eth_rpc.wallet import PrivateKeyWallet


def find_start_wallet_with_start_string(start_number: int):
    while True:
        wallet = PrivateKeyWallet.create_new()
        if wallet.address.lower().startswith(hex(start_number)):
            return wallet


if __name__ == "__main__":
    BEEF: int = 0xBEEF
    wallet: PrivateKeyWallet = find_start_wallet_with_start_string(BEEF)
    print(f"address: {wallet.address} | pk: {wallet.private_key}")
