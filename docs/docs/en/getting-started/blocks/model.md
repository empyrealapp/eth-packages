# The Blocks Model

`Block` is a Pydantic BaseModel.  It has all the fields provided by the standard Ethereum RPC.

!!! tip
    The block will either have a list of Transaction hashes or a list of Transactions, depending on whether or not you request the block `with_tx_data=True`.  By default it returns the transaction hashes.

```python
class Block(RPCModel):
    number: HexInteger
    hash: Optional[HexStr] = None
    base_fee_per_gas: Optional[HexInteger] = None
    transactions: list["Transaction"] | list[HexStr] = Field(default_factory=list)
    difficulty: HexInteger
    extra_data: HexStr
    gas_limit: HexInteger
    gas_used: HexInteger
    logs_bloom: HexStr
    miner: Optional[HexAddress] = None
    mix_hash: HexStr
    nonce: Optional[HexStr] = None
    parent_hash: HexStr
    receipts_root: HexStr
    sha3_uncles: HexStr
    size: HexInteger
    state_root: HexStr
    timestamp: datetime
    total_difficulty: Optional[HexInteger] = None
    transactions_root: HexStr
    uncles: list[HexStr] = Field(default_factory=list)
```
