# Transport

There are a few ways to manage RPC connections.  The simplest way is to set your alchemy api key, and it will automatically use Alchemy RPC's for your connections.  This is useful when doing indexing, but sometimes you may need a private RPC or a specific RPC for a network.  In those cases, you can set the RPC like this:

```python
from eth_rpc import set_rpc_url
from eth_rpc.networks import Ethereum  # this can be any network

set_rpc_url(Ethereum, http="http://my_rpc.com", wss="wss://my_rpc.com")
```

## Setting Alchemy Key

Alchemy is a popular RPC node provider that supports many networks.  They will always be the same url for an account, and so if you provide an API key the library is able to use your alchemy RPC url by default:

```python
from eth_rpc import set_alchemy_key

set_alchemy_key("<ALCHEMY_KEY>")
```

## Networks

The [Network Class](/api/network/){.internal-link} must be implemented for each network you want to interact with.  This is because the Network must be a singleton, and it must be a proper Type so it's compatbile with Generics.  The only mutable fields on the Network class should be the rpc nodes.  This allows you to globally set the desired rpc for a network.

If you need to add a network that is not supported, please make a Pull Request!  But this is not necessary, you can simply implement the Network class.  For example, here's the implementtion for a made up network:

```python
class MyPrivateNetwork(Network):
    chain_id: ClassVar[int] = 12345
    name: ClassVar[str] = "My Private Network"
    native_currency: ClassVar[str] = "MPN"
    rpc: ClassVar[Rpcs] = Rpcs(
        default=RpcUrl(
            http=AnyHttpUrl("https://my-private.network"),
            http="wss://my-private.network",
        )
    )
    block_explorer: ClassVar[BlockExplorer] = BlockExplorer(
        name="MpnScan",
        url="https://mpnscan.org",
        api_url="https://api.mpnscan.org/api",
    )
    alchemy_str: ClassVar[str | None] = None
    apprx_block_time: ClassVar[float] = 1.23
```

Then you can use this just like the other networks, or even set it as your default network via:

```python
from eth_rpc import set_default_network

set_default_network(MyPrivateNetwork)
```
