# eth-packages

**A comprehensive Python framework for type-safe Ethereum and EVM blockchain development**

---

<p align="center">
  <a href="https://github.com/empyrealapp/eth-packages/actions/workflows/build.yaml" target="_blank">
    <img src="https://github.com/empyrealapp/eth-packages/actions/workflows/build.yaml/badge.svg?branch=main" alt="Test Passing"/>
  </a>
  <a href="https://www.pepy.tech/projects/eth-rpc-py" target="_blank">
    <img src="https://static.pepy.tech/personalized-badge/eth-rpc-py?period=month&units=international_system&left_color=grey&right_color=green&left_text=downloads/month" alt="Downloads"/>
  </a>
  <a href="https://pypi.org/project/eth-rpc-py" target="_blank">
    <img src="https://img.shields.io/pypi/v/eth-rpc-py?label=PyPI" alt="Package version">
  </a>
  <a href="https://pypi.org/project/eth-rpc-py" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/eth-rpc-py.svg" alt="Supported Python versions">
  </a>
</p>

---

## Overview

eth-packages is a monorepo containing four interconnected Python packages designed to provide type-safe, developer-friendly interactions with Ethereum and EVM-compatible blockchain networks. Built with a focus on developer experience, the framework emphasizes strong typing, comprehensive error handling, and intuitive APIs.

### Key Features

- **Type-Safe Contract Interactions**: Generate Python classes from contract ABIs with full IDE support
- **Real-Time Event Processing**: Subscribe to blockchain events with automatic decoding
- **Multi-Network Support**: Seamlessly work across Ethereum, Arbitrum, Base, and other EVM networks
- **Efficient Data Retrieval**: Batch multiple contract calls using multicall patterns
- **Transaction Management**: Sign and submit transactions with gas estimation and nonce management
- **Protocol Abstractions**: High-level interfaces for common DeFi protocols

### Architecture

The framework consists of four main packages:

- **`eth_rpc`** - Core RPC communication, type system, and blockchain interaction primitives
- **`eth_typeshed`** - Pre-built type definitions for common Ethereum standards (ERC20, ERC721, Uniswap, etc.)
- **`eth_protocols`** - High-level abstractions for interacting with specific DeFi protocols
- **`eth_streams`** - Data streaming capabilities for blockchain data processing

---

## Documentation

Read the comprehensive documentation [here](https://eth-packages.empyrealsdk.com/)

---

## Installation

### Prerequisites

- Python 3.10 or higher
- An Ethereum RPC endpoint (Alchemy, Infura, or custom node)

### Basic Installation

Install the core packages using pip:

```bash
pip install eth-rpc-py
pip install eth-typeshed-py
```

### Development Installation

For development or to access all packages:

```bash
git clone https://github.com/empyrealapp/eth-packages.git
cd eth-packages
pip install -e packages/eth_rpc
pip install -e packages/eth_typeshed
pip install -e packages/eth_protocols
pip install -e packages/eth_streams
```

### Environment Setup

Set up your environment with an RPC provider:

```python
import os
from eth_rpc import set_alchemy_key, set_rpc_url
from eth_rpc.networks import Ethereum

# Option 1: Use Alchemy (recommended)
set_alchemy_key(os.environ["ALCHEMY_KEY"])

# Option 2: Use custom RPC endpoint
set_rpc_url(Ethereum, "https://your-rpc-endpoint.com")
```

## Quick Start

### Basic Usage Example

This comprehensive example demonstrates the key features of eth-packages:

```python
import asyncio
import os
from eth_rpc import *
from eth_rpc.ens import lookup_addr
from eth_rpc.networks import Arbitrum, Base, Ethereum
from eth_typeshed import *
from eth_typeshed.erc20 import *

async def main():
    # Configure your RPC provider
    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    
    # Alternative: set RPC URL directly for specific networks
    # set_rpc_url(Ethereum, "https://your-ethereum-rpc.com")
    
    # === BLOCK DATA RETRIEVAL ===
    # Get the latest block on Ethereum with transaction data
    eth_block: Block[Ethereum] = await Block[Ethereum].latest(with_tx_data=True)
    print(f"Latest Ethereum block: {eth_block.number}")
    
    # Calculate total ETH value in the block
    total_value = sum(tx.value for tx in eth_block.transactions)
    print(f"Total ETH in block: {total_value / 10**18:.2f} ETH")
    
    # Get latest block on Arbitrum (different network)
    arb_block: Block[Arbitrum] = await Block[Arbitrum].latest()
    print(f"Latest Arbitrum block: {arb_block.number}")
    
    # === CONTRACT INTERACTIONS ===
    # Create an ERC20 contract instance for USDT on Arbitrum
    usdt = ERC20[Arbitrum](address='0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9')
    
    # Single contract calls
    name = await usdt.name().get()
    symbol = await usdt.symbol().get()
    decimals = await usdt.decimals().get()
    print(f"Token: {name} ({symbol}) with {decimals} decimals")
    
    # === MULTICALL OPTIMIZATION ===
    # Batch multiple calls into a single RPC request for efficiency
    multicall = Multicall[Arbitrum]()
    (name, symbol, decimals, total_supply) = await multicall.execute(
        usdt.name(),
        usdt.symbol(),
        usdt.decimals(),
        usdt.total_supply(),
    )
    print(f"Total {symbol} supply: {total_supply / 10**decimals:,.0f}")
    
    # === ENS RESOLUTION ===
    # Resolve ENS name to address
    vitalik_addr = await lookup_addr('vitalik.eth')
    print(f"Vitalik's address: {vitalik_addr}")
    
    # Get balance at specific block (historical data)
    balance = await usdt.balance_of(vitalik_addr).get(block_number=246_802_382)
    print(f"Vitalik's USDT balance at block 246802382: {balance / 10**decimals:.2f}")
    
    # === EVENT STREAMING ===
    # Subscribe to real-time transfer events
    print("Listening for USDT transfers...")
    async for event in TransferEvent[Arbitrum].set_filter(
        addresses=[usdt.address]
    ).subscribe():
        data = event.event
        amount = data.amount / 10**decimals
        print(f"Transfer: {amount:.2f} {symbol} from {data.sender} to {data.recipient}")
        
        # Break after first event for demo purposes
        break

if __name__ == "__main__":
    asyncio.run(main())
```

### Common Patterns

#### 1. Multi-Network Operations
```python
from eth_rpc.networks import Ethereum, Arbitrum, Base

# Work with the same contract across different networks
networks = [Ethereum, Arbitrum, Base]
for network in networks:
    block = await Block[network].latest()
    print(f"{network.__name__} latest block: {block.number}")
```

#### 2. Historical Data Analysis
```python
# Analyze token transfers over a block range
async for event in TransferEvent[Ethereum].set_filter(
    addresses=[token_address]
).backfill(start_block=18000000, end_block=18001000):
    print(f"Transfer: {event.event.amount}")
```

#### 3. Transaction Execution
```python
from eth_rpc.wallet import PrivateKeyWallet

wallet = PrivateKeyWallet(private_key=os.environ["PRIVATE_KEY"])
tx_hash = await usdt.transfer(recipient_address, amount).execute(wallet)
print(f"Transaction sent: {tx_hash}")
```

## Advanced Features

### Type-Safe Contract Interfaces

The framework's strength lies in creating type-safe contract interfaces. Instead of working with raw ABIs, you can define strongly-typed contract classes:

```solidity
// Your deployed contract
contract MyContract {
    function foo(address[] users) external returns(bool success) {}
    function getUser(uint256 id) external view returns(address user, uint256 balance) {}
}
```

Create a typed Python interface:

```python
import os
from typing import Annotated
from eth_rpc.contract import ProtocolBase, ContractFunc
from eth_rpc.wallet import PrivateKeyWallet
from eth_rpc.types import HexStr, Name, primitives
from eth_rpc.networks import Ethereum

class MyContract(ProtocolBase):
    # Function with array input and named return value
    foo: ContractFunc[
        list[primitives.address],  # Input: list of addresses
        Annotated[bool, Name("success")]  # Output: boolean named "success"
    ]
    
    # Function with multiple return values
    get_user: ContractFunc[
        primitives.uint256,  # Input: user ID
        tuple[primitives.address, primitives.uint256]  # Output: address and balance
    ]

# Usage
contract = MyContract[Ethereum](address="0x1234...")
wallet = PrivateKeyWallet(private_key=os.environ["PRIVATE_KEY"])

# Read-only call (no gas cost)
user_data = await contract.get_user(123).get()
user_address, balance = user_data
print(f"User {user_address} has balance {balance}")

# State-changing transaction
addresses = ["0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045", "0x..."]
tx_hash = await contract.foo(addresses).execute(wallet)
print(f"Transaction hash: {tx_hash}")

# Wait for confirmation
tx = await Transaction[Ethereum].get_by_hash(tx_hash)
receipt = await tx.wait_for_receipt()
print(f"Transaction confirmed in block {receipt.block_number}")
```

### Code Generation from ABIs

Generate typed contract interfaces automatically:

```bash
# From ABI file
eth_rpc codegen load contract_abi.json -o my_contract.py -c MyContract

# From verified contract on Etherscan
eth_rpc codegen explorer --address 0x1234... --api-key YOUR_KEY -o my_contract.py -c MyContract
```

### Event Processing and Analytics

```python
from eth_typeshed.erc20 import TransferEvent, TransferEventType

# Real-time event monitoring
async def monitor_large_transfers():
    async for event in TransferEvent[Ethereum].subscribe():
        transfer = event.event
        if transfer.amount > 1000000 * 10**18:  # > 1M tokens
            print(f"Large transfer detected: {transfer.amount}")

# Historical analysis
async def analyze_token_activity(token_address, start_block, end_block):
    total_volume = 0
    unique_users = set()
    
    async for event in TransferEvent[Ethereum].set_filter(
        addresses=[token_address]
    ).backfill(start_block, end_block):
        transfer = event.event
        total_volume += transfer.amount
        unique_users.add(transfer.sender)
        unique_users.add(transfer.recipient)
    
    return {
        "total_volume": total_volume,
        "unique_users": len(unique_users),
        "transactions": len(events)
    }
```

## Troubleshooting

### Common Issues

**1. RPC Connection Errors**
```python
# Ensure you have a valid RPC endpoint
from eth_rpc import set_alchemy_key, set_rpc_url
from eth_rpc.networks import Ethereum

# Use Alchemy (recommended)
set_alchemy_key("your-alchemy-key")

# Or use custom RPC
set_rpc_url(Ethereum, "https://your-rpc-endpoint.com")
```

**2. Import Errors**
```bash
# Make sure all required packages are installed
pip install eth-rpc-py eth-typeshed-py

# For development
pip install -e packages/eth_rpc -e packages/eth_typeshed
```

**3. Type Checking Issues**
```python
# Ensure proper type annotations
from eth_rpc.types import primitives

# Correct
balance: primitives.uint256 = await token.balance_of(address).get()

# Incorrect - missing type specification
balance = await token.balance_of(address).get()
```

**4. Network Configuration**
```python
# Specify network explicitly when working with multiple chains
from eth_rpc.networks import Ethereum, Arbitrum

eth_token = ERC20[Ethereum](address="0x...")
arb_token = ERC20[Arbitrum](address="0x...")
```

### Performance Tips

- Use `multicall` for batching multiple contract calls
- Specify block numbers for historical queries to enable caching
- Use event filtering to reduce data transfer
- Consider using WebSocket connections for real-time event streaming

### Getting Help

- Documentation: https://eth-packages.empyrealsdk.com/
- GitHub Issues: https://github.com/empyrealapp/eth-packages/issues
- Examples: Check the `examples/` directory for practical use cases

## Contributing

We welcome pull requests, and would love to find contributors interested in bringing more type
safety to pythonic blockchain development.

## License

[MIT](https://choosealicense.com/licenses/mit/)
