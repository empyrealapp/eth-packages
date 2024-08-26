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
from eth_rpc.networks import Arbitrum, Base, Ethereum
from eth_typeshed import *
from eth_typeshed.erc20 import *

set_alchemy_key("<ALCHEMY_KEY>")
block = await Block[Ethereum].latest(with_tx_data=True)
total_value = 0
for tx in block.transactions:
    total_value += tx.value
block2 = await Block[Arbitrum].latest()

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

# get the balance of an address at a specific block
balance = await usdt.balance_of('0xd8da6bf26964af9d7eed9e03e53415d37aa96045').get(block_number=246_802_382)

# subscribe to transfer events on Arbitrum for USDT
async for event in TransferEvent[Arbitrum].set_filter(
    addresses=[usdt.address]
).subscribe():
    data = event.event
    print(f'{data.sender} sent {data.recipient} {data.amount / 10 ** decimals} {name}')
```


## Contributing

We welcome pull requests, and would love to find contributors interested in bringing more type
safety to pythonic blockchain development.

## License

[MIT](https://choosealicense.com/licenses/mit/)
