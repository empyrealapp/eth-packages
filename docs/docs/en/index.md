---
hide:
  - navigation
search:
  exclude: true
---

# eth-packages

<b>Typed Ethereum Functionality for Web3 Development</b>

---

# Features

`eth-packages` is a set of tools from the [Empyreal](https://empyrealsdk.com){:target="_blank"} to simplify the process of writing or generating code for interacting with the ethereum RPC.  This includes:

- Sending Requests to the RPC to fetch data about Blocks, Transactions, Logs
- Creating Typed Bindings for Contracts
- Creating Typed Bindings for Log Events
- Subscribing to log events
- Building pipelines for data ingest from RPC nodes

It was designed to be extremely lightweight with minimable dependencies, making it well suited for Cloud Functions/AWS Lambda.

All tooling in eth-rpc is used daily by the Empyreal development team, and we hope that sharing this tooling with you will facilitate your development.  Particular attention has been paid to creating typed bindings to smart contracts, especially in the pursuit of simplified code generation with Large Language Models.

By creating typed bindings, we have made an async-first, meaningfully abstracted library for interacting with and monitoring ethereum smart contracts.  This means a user can have greater type safety and easier debugging, especially when relying on generated code.  Without this type safety, it is very difficult to integrate multiple actions together across a codebase.

---

# Install

All the libraries in eth-packages works on Linux, macOS, Windows and most Unix-style operating systems. You can install it with pip as usual:

```sh
pip install eth-rpc-py
pip install eth-typeshed-py
```

!!! tip
    There are several modules in eth-packages.  Our initial focus will be on sharing information about `eth-rpc`, as this is the library that enables all other functionality.  `eth-typeshed` utilizes this to created typed bindings to popular smart contracts so they can be further abstracted in `eth-protocols`.
---

# Quickstart

The library is designed to abstract significant aspects of the contract ABIs into typed python, making your static analsysi more effective.  This is also valuable as it enables LLMs to generate code in a much less verbose way, leaning into their strengths of structured abstraction without forcing them to impart as much domain knowledge.

In this example, we show a variety of language features.  We are able to access data from multiple blockchains, getting information about Blocks, calling smart contracts directly to access onchain data, and subscribing to log data to see historical events.

Additionally, we have integrated with Alchemy and Infura (Coming Soon!) for simple RPC access.  This makes it easy to utilize your credentials to easily access a variety of chains without having to populate the RPCs manually.

You'll also notice the `<Type>[Network]` syntax, which allows to easily specify the network for the request.

```python
from eth_rpc import *
from eth_rpc.utils import to_checksum
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
usdt = ERC20[Arbitrum](address=to_checksum('0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'))
name = await usdt.name().get()
symbol = await usdt.symbol().get()
decimals = await usdt.decimals().get()

# or do it as a multicall (defaults to the standard multicall contract)
(name, symbol, decimals) = await multicall[Arbitrum].execute(
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
