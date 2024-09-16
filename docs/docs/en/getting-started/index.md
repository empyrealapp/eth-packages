# QUICK START

install using pip

```sh
pip install eth-rpc-py
pip install eth-typeshed-py
```

# Basic Usage

We recommend setting up an [Alchemy](https://www.alchemy.com/) account so you can utilize your API key for requests, otherwise you will use public RPCs that typically do not allow for websocket connections or frequent requests.  You can also set your RPC directly

```python
import os

from eth_rpc import set_alchemy_key, set_rpc_url
from eth_rpc.networks import Ethereum

# If you want to set an RPC for a network directly
set_rpc_url(Ethereum, os.environ["MY_PRIVATE_RPC_URL"])

# Or you can set your alchemy key and it will automatically set it as the default RPC for all networks
set_alchemy_key(os.environ["ALCHEMY_KEY"])
```
