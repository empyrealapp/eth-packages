# Getting Started

Welcome to eth-packages! This guide will help you get up and running with type-safe Ethereum development in Python.

## Installation

### Prerequisites

- Python 3.10 or higher
- An Ethereum RPC endpoint (Alchemy recommended)

### Basic Installation

Install the core packages using pip:

```sh
pip install eth-rpc-py
pip install eth-typeshed-py
```

### Development Installation

For development or to access all packages:

```sh
git clone https://github.com/empyrealapp/eth-packages.git
cd eth-packages

# Install in development mode
pip install -e packages/eth_rpc
pip install -e packages/eth_typeshed
pip install -e packages/eth_protocols
pip install -e packages/eth_streams
```

## RPC Configuration

### Option 1: Alchemy (Recommended)

[Alchemy](https://www.alchemy.com/) provides reliable RPC endpoints with generous free tiers and WebSocket support for real-time events.

```python
import os
from eth_rpc import set_alchemy_key

# Set your Alchemy key globally for all networks
set_alchemy_key(os.environ["ALCHEMY_KEY"])
```

### Option 2: Custom RPC Endpoints

You can configure custom RPC endpoints for specific networks:

```python
import os
from eth_rpc import set_rpc_url
from eth_rpc.networks import Ethereum, Arbitrum, Base

# Set custom RPC for Ethereum
set_rpc_url(Ethereum, os.environ["ETHEREUM_RPC_URL"])

# Set different RPCs for different networks
set_rpc_url(Arbitrum, "https://arb1.arbitrum.io/rpc")
set_rpc_url(Base, "https://mainnet.base.org")
```

### Option 3: Environment Variables

Configure RPC settings using environment variables:

```python
from eth_rpc import configure_rpc_from_env

# Automatically configure from environment variables:
# ALCHEMY_KEY, ETHEREUM_RPC_URL, ARBITRUM_RPC_URL, etc.
configure_rpc_from_env()
```

## First Steps

### 1. Basic Block Data

```python
import asyncio
from eth_rpc import Block
from eth_rpc.networks import Ethereum

async def get_latest_block():
    # Get the latest block
    block = await Block[Ethereum].latest()
    print(f"Latest block: {block.number}")
    print(f"Block hash: {block.hash}")
    print(f"Timestamp: {block.timestamp}")

asyncio.run(get_latest_block())
```

### 2. Contract Interactions

```python
from eth_typeshed.erc20 import ERC20
from eth_rpc.networks import Ethereum

async def check_token_info():
    # USDC on Ethereum
    usdc = ERC20[Ethereum](address="0xA0b86a33E6441b8e776f1c0b8e8e8e8e8e8e8e8e")
    
    # Get token information
    name = await usdc.name().get()
    symbol = await usdc.symbol().get()
    decimals = await usdc.decimals().get()
    
    print(f"Token: {name} ({symbol})")
    print(f"Decimals: {decimals}")

asyncio.run(check_token_info())
```

### 3. Event Monitoring

```python
from eth_typeshed.erc20 import TransferEvent
from eth_rpc.networks import Ethereum

async def monitor_transfers():
    # Monitor USDC transfers
    usdc_address = "0xA0b86a33E6441b8e776f1c0b8e8e8e8e8e8e8e8e"
    
    async for event in TransferEvent[Ethereum].set_filter(
        addresses=[usdc_address]
    ).subscribe():
        transfer = event.event
        amount = transfer.amount / 10**6  # USDC has 6 decimals
        print(f"Transfer: {amount:.2f} USDC from {transfer.sender} to {transfer.recipient}")

# Run this in a separate task or process
asyncio.run(monitor_transfers())
```

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Make sure packages are installed
pip install eth-rpc-py eth-typeshed-py

# Check Python version
python --version  # Should be 3.10+
```

**2. RPC Connection Issues**
```python
# Test your RPC connection
from eth_rpc import Block
from eth_rpc.networks import Ethereum

try:
    block = await Block[Ethereum].latest()
    print(f"Connection successful! Latest block: {block.number}")
except Exception as e:
    print(f"Connection failed: {e}")
```

**3. Rate Limiting**
```python
# Use Alchemy or other premium RPC providers
# Public RPCs often have strict rate limits
set_alchemy_key("your-alchemy-key")
```

**4. WebSocket Issues**
```python
# Ensure your RPC provider supports WebSockets for event streaming
# Alchemy and Infura support WebSockets
# Some public RPCs do not
```

### Performance Tips

- Use multicall for batch operations
- Specify block numbers for historical queries
- Use event filtering to reduce data transfer
- Consider caching frequently accessed data

## Next Steps

- [Contract Interactions](contracts/index.md) - Learn about type-safe contract interfaces
- [Event Processing](events/index.md) - Master blockchain event handling
- [Code Generation](contracts/codegen.md) - Generate contract interfaces from ABIs
- [API Reference](../../api/) - Detailed API documentation

## Getting Help

- **Documentation**: https://eth-packages.empyrealsdk.com/
- **GitHub Issues**: https://github.com/empyrealapp/eth-packages/issues
- **Examples**: Check the `examples/` directory in the repository
