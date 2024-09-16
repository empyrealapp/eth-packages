# Account Class

The [Account class](/api/account/){.internal-link} is part of the eth_rpc package and provides methods for interacting with Ethereum accounts via RPC calls.

```python
from eth_rpc import Account

eth_address = "0x0000000000000000000000000000000000000000"
# get an account's balance
balance = await Account.get_balance(eth_address)

# Get all account data
account_data = await Account.get_account(eth_address)

# Access and display individual fields
print(f"Account Details for {eth_address}:")
print(f"Balance: {account_data.balance} wei")
print(f"Nonce: {account_data.nonce}")
print(f"Code Hash: {account_data.code_hash}")
print(f"Storage Root: {account_data.storage_root}")

# Convert balance to Ether for better readability
balance_in_ether = int(account_data.balance, 16) / 1e18
print(f"Balance in Ether: {balance_in_ether:.6f} ETH")

# Check if the account is a contract
is_contract = account_data.code_hash != "0x0000000"
print(f"Is Contract: {'Yes' if is_contract else 'No'}")
```

!!! warning
    `get_account` will not work on the Alchemy RPC; it does not support the `eth_getAccount` method.  It will work with quicknode and some other RPC providers.
