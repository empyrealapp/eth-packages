# Blocks

The [Block class](/api/block/){.internal-link} is your connection to the different RPC endpoints that are specific to Blocks onchain.  Typically you will want to check things like the current block number, or you might want to access all the transactions for a specific block.

The returned `Block` is a Pydantic BaseModel, providing typed access to all associated fields.

```python
from eth_rpc import Block

block = await Block.load_by_number(3_000_000)
```

If you want to load with transactions, just specify in the request:

```python
from eth_rpc import Block, Transaction

block = await Block.load_by_number(3_000_000, with_tx_data=True)
transactions: list[Transaction] = block.transactions
```

Now we have access to a Transaction, which is also a Pydantic BaseModel, and it exposes the ability to access it's `TransactionReceipt`.  So similar to an ORM, all the different types are able to communicate with the RPC in a meaningful way.

```python
tx = transactions[0]
await tx.receipt()
```
