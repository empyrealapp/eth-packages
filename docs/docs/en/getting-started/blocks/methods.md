# Blocks RPC Methods

## Fee History

We can also load the FeeHistory for a series of blocks to help plan our transaction:

```python
fee_history = await Block.fee_history(
    block_count=4,
    lower_percentile=25,
    upper_percentile=75,
    block_number=20_000_000,  # by default this is set to "latest"
)
# fee_history.base_fee_per_gas == [5104157871, 5171340881, 5004025121, 4936957716, 4776082506]
```

This shows the base_fee_per_gas for the last four blocks, so you can accurately estimate the minimum base_fee_per_gas needed for a transaction.

---

## Subscription

We can utilize the RPC websocket endpoint to connect and subscribe to blocks as they are ingested.  You can also backfill from a certain block number, which is useful when you have a persistent stream and want to be able to resume from a certain number.

```python
async for block in Block.subscribe_from(20_000_000):
    # print the number and their tx count
    print(block.number, len(block.transactions))
```

---

## Additional Methods

There are a few other methods supported by most RPCs that are blocks related:

```python
from eth_typing import HexStr

await Block.get_block_transaction_count(20_000_000)
await Block.load_by_number(20_000_000, with_tx_data=False)
await Block.get_number()  # get current block number
await Block.latest()
await Block.pending()
await Block.load_by_hash(
    HexStr(
        "0x13ced9eaa49a522d4e7dcf80a739a57dbf08f4ce5efc4edbac86a66d8010f693"
    )
)
```
