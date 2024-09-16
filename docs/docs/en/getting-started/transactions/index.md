# Transactions

The [Transaction class](/api/transaction/){.internal-link} abstracts all requests related to Ethereum Transactions.  With the transactions model you can access Transactions and TransactionReceipts.

```python
from eth_typing import HexStr

from eth_rpc import Transaction, TransactionReceipt


tx_hash: HexStr = HexStr(
    "0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060"
)

tx: Transaction = await Transaction.get_by_hash(tx_hash)
# get the receipt
tx_reciept: TransactionReceipt = await Transaction.get_receipt_by_hash(tx.hash)

# you can also access the receipt directly from the tx object
tx_receipt: TransactionReceipt = await tx.receipt()

# you can get a transaction from a block by its index
tx: Transaction = await Transaction.get_by_index(
    transaction_index=0,
    block_hash=HexStr(
        "0x4e3a3754410177e6937ef1f84bba68ea139e8d1a2258c5f85db9f1cd715a1bdd",
    ),
)
```

---

# Pending Transactions

You can also load pending transactions by hash, from a mempool monitor

```python
# subscribe to all pending transactions, and print the hash
async for tx in Transaction.subscribe_pending():
    print(tx.hash)
```

---

# Getting a transactions block

You can access the transactions block by calling the `get_block` method on a transaction object.  As usual, `with_tx_data` is an optional argument.

```python
tx: Transaction = await Transaction.get_by_hash(tx_hash)
block: Block = await tx.get_block(with_tx_data=True)
```
