# Multicall

> bundling multiple calls into a single transaction/eth_call

## Basic Usage

Multicall is very useful for querying multiple datapoints in a single call to the RPC node.  This helps significantly with latency, and can save you compute units with your RPC provider.  It's very straightforward to call the Multicall function, just provide your calls in order and they'll return their outputs of the expected type:

```python
from eth_rpc.networks import Arbitrum
from eth_typeshed import multicall

# create an ERC20 contract object on Arbitrum and access its name, symbol and decimals
usdt = ERC20[Arbitrum](address=to_checksum('0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'))

(name, symbol, decimals) = await multicall[Arbitrum].execute(
    usdt.name(),
    usdt.symbol(),
    usdt.decimals(),
)
```

## Error Handling

If you want to call the multicall, but ignore errors during execution, just add:

```python
results: list[TryResult] = await multicall[Arbitrum].try_execute(
    usdt.name(),
    usdt.symbol(),
    usdt.decimals(),
)
name = results[0].result
symbol = results[1].result
decimals = results[2].result
has_error = not (results[0].success and results[1].success and results[2].success)
```
