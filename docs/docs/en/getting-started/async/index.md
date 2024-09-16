# Async/Sync Execution

We have made this library to support asynchronous and synchronous execution.  For most RPC calls, you can simply call the `.sync` property instead of awaiting the call, ie:

```python
from eth_rpc import Block

latest = Block.latest().sync
```
