# eth-typeshed

A collection of typed bindings to popular smart contracts, with contract addresses and other data for easy reference.

## Example

```python
from eth_typeshed import ERC20

usdt = ERC20(address=usdt_address)
await usdt.transfer(TransferRequest(
    recipient="0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
    amount=int(1e6),
))
```
