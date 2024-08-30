# eth-packages

A collection of packages for working with EVM based blockchains.  This library aims to simplify the complexity of interacting with smart contracts, by created a python library that supports data validation.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install eth_rpc and/or eth_typeshed

```bash
pip install eth-rpc-py
pip install eth-typeshed-py
```

## Usage

The following example assumes the user has an alchemy key, which is the key used by alchemy to identify your account for RPC requests.  Public RPCs will typically rate limit and/or limit their supported endpoints.

```python
from eth_rpc import *
from eth_rpc.ens import lookup_addr
from eth_rpc.networks import Arbitrum, Base, Ethereum
from eth_typeshed import *
from eth_typeshed.erc20 import *

# set your alchemy key globaly to configure it for all networks
set_alchemy_key("<ALCHEMY_KEY>")

# or set the RPC url for a network directly
set_rpc_url(Ethereum, "<MY PRIVATE RPC URL>")

# get the latest block on ethereum
block: Block[Ethereum] = await Block[Ethereum].latest(with_tx_data=True)

# calculate the total value of all transactions in a block
total_value = 0
for tx in block.transactions:
    total_value += tx.value

# get the latest block on arbitrum
block2: Block[Arbitrum] = await Block[Arbitrum].latest()

# create an ERC20 contract object on Arbitrum and access its name, symbol and decimals
usdt = ERC20[Arbitrum](address='0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9')
name = await usdt.name().get()
symbol = await usdt.symbol().get()
decimals = await usdt.decimals().get()

# or do it as a multicall
multicall = Multicall[Arbitrum]()
(name, symbol, decimals) = await multicall.execute(
    usdt.name(),
    usdt.symbol(),
    usdt.decimals(),
)

# get vitalik's usdt balance at a specific block
vitalik_addr = await lookup_addr('vitalik.eth')
balance = await usdt.balance_of(vitalik_addr).get(
    block_number=246_802_382,
)

# subscribe to transfer events on Arbitrum for USDT
async for event in TransferEvent[Base].set_filter(
    addresses=[usdt.address]
).subscribe():
    data = event.event
    print(f'{data.sender} sent {data.recipient} {data.amount / 10 ** decimals} {name}')
```

### Additional Features

But this is just the tip of the iceberg.  The real focus is on making it easier to interact with deployed smart contracts and having some greater type safety.  For example, say you want to interact with a contract you just deployed, ie:

```solidity
contract MyContract {
    function foo(address[] users) external returns(bool success) {}
}
```

Rather than copying the abi into a JSON file, you can create a typed contract interface:

```python
from typing import Annotated

from eth_rpc.contract import ProtocolBase, ContractFunc
from eth_rpc import Transaction
from eth_rpc.wallet import PrivateKeyWallet
from eth_rpc.types import HexStr, Name, primitives


class MyContract(ProtocolBase):
    foo: ContractFunc[
        list[primitives.address],  # input type is a list of addresses
        Annotated[bool, Name("success")],  # response type is a boolean
    ] = METHOD  # this is necessary for the type checker to recognize it as a method

contract = MyContract(address="<Contract Address>")
# create a wallet for yourself
wallet = PrivateKeyWallet(private_key=os.environ["PK"])

# call it without execution:
response: bool = await contract.foo(['0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045', ...]).call(
    from_=wallet.address,
)

# or call it with execution:
tx_hash: HexStr = await contract.foo(['0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045', ...]).execute(wallet)
tx: Transaction[Ethereum] = await Transaction[Ethereum].get_by_hash(tx_hash)
```

## Contributing

We welcome pull requests, and would love to find contributors interested in bringing more type
safety to pythonic blockchain development.

## License

[MIT](https://choosealicense.com/licenses/mit/)
