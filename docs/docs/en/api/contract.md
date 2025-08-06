# Contract API Reference

The Contract class provides the foundation for interacting with smart contracts on Ethereum and EVM-compatible networks.

## Overview

The Contract class serves as the base for all contract interactions in eth-rpc. It provides:

- **Address Management**: Contract address handling and validation
- **Network Context**: Multi-network support with type safety
- **ABI Integration**: Automatic function signature generation
- **State Management**: Code overrides and simulation support

## Basic Usage

```python
from eth_rpc import Contract
from eth_rpc.networks import Ethereum

# Basic contract instance
contract = Contract[Ethereum](address="0x...")

# With custom network configuration
contract = Contract(
    address="0x...",
    network=Ethereum,
    code_override="0x..."  # For testing/simulation
)
```

## Class Reference

::: eth_rpc.Contract
    options:
      show_root_heading: true
      show_source: false
      heading_level: 3
