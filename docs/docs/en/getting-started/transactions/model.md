# Transaction Model

`Transaction` and `TransactionReceipt` are both Pydantic BaseModels.  It has all the fields provided by the standard Ethereum RPC.


```python
class Transaction(BaseModel):
    hash: HexStr
    access_list: Optional[list[AccessList]] = None
    chain_id: Optional[HexInteger] = None
    from_: HexStr = Field(alias="from")
    gas: HexInteger
    gas_price: HexInteger
    max_fee_per_gas: Optional[HexInteger] = None
    max_priority_fee_per_gas: Optional[HexInteger] = None
    input: HexStr
    nonce: HexInteger
    r: HexStr
    s: HexStr
    v: HexInteger
    to: Optional[HexStr]
    type: Optional[HexInteger] = None
    value: HexInteger
    y_parity: HexInteger | None = None
    block_hash: HexStr
    block_number: HexInteger
    transaction_index: HexInteger


class TransactionReceipt(BaseModel):
    transaction_hash: HexStr
    block_hash: HexStr
    block_number: HexInteger
    logs: list[Log]
    contract_address: Optional[HexStr]
    effective_gas_price: HexInteger
    cumulative_gas_used: HexInteger
    from_: HexAddress = Field(alias="from")
    gas_used: HexInteger
    logs_bloom: HexInteger
    status: Optional[HexInteger] = None
    to: Optional[HexAddress]
    transaction_index: HexInteger
    type: HexInteger
```
