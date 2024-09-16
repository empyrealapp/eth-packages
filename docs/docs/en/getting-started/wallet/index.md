# PrivateKeyWallet

The [PrivateKeyWallet class](/api/wallet/){.internal-link} is a powerful tool for managing private keys and signing transactions in Ethereum-based applications. It seamlessly integrates with the `Contracts` class, providing a way to sign transactions and other data.

## Usage

To use the `PrivateKeyWallet`, you need to import it from the `eth_rpc.wallet` module:

```python
from eth_rpc import PrivateKeyWallet

wallet = PrivateKeyWallet(private_key="0x...")
```

Then if you have a Contracts instance, you can use the `execute` method to sign a transaction:

```python
await token.transfer(TransferRequest(recipient="0x...", amount=1)).execute(wallet=wallet)
```

Or for synchronous execution:

```python
token.transfer(TransferRequest(recipient="0x...", amount=1)).execute(wallet=wallet, sync=True)
```
