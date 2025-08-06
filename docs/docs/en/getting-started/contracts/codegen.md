# Code Generation: From ABI to Type-Safe Interfaces

The eth-rpc framework provides powerful code generation tools that transform contract ABIs into fully type-safe Python interfaces. This eliminates the need for manual ABI handling while providing comprehensive IDE support and runtime validation.

## Why Use Code Generation?

### Traditional Approach Problems
```python
# Traditional web3.py approach - no type safety
contract = web3.eth.contract(address=address, abi=large_abi_json)
result = contract.functions.someFunction(param1, param2).call()
# What type is result? What parameters does someFunction expect?
```

### eth-rpc Generated Approach
```python
# Generated type-safe interface
class MyContract(ProtocolBase):
    some_function: ContractFunc[
        tuple[primitives.uint256, primitives.address],  # Clear input types
        Annotated[bool, Name("success")]                # Clear output type
    ]

# Usage with full type safety
contract = MyContract[Ethereum](address="0x...")
result: bool = await contract.some_function(amount, recipient).get()
```

## Benefits of Generated Interfaces

### 1. Enhanced Type Safety
- **Compile-time Checking**: Catch type errors before runtime
- **IDE Support**: Full autocomplete and error highlighting
- **Parameter Validation**: Automatic input/output validation

### 2. Improved Developer Experience
- **Self-Documenting**: Types serve as documentation
- **Refactoring Safety**: IDE can safely rename and refactor
- **Error Prevention**: Impossible to call functions with wrong parameters

### 3. AI-Friendly Code
- **Structured Format**: Easy for LLMs to understand and generate
- **Consistent Patterns**: Predictable code structure
- **Clear Semantics**: Explicit type information aids code generation

### 4. Performance Benefits
- **No JSON Parsing**: Types are compiled, not parsed at runtime
- **Efficient Encoding**: Direct ABI encoding without intermediate steps
- **Smaller Bundles**: No need to include large ABI JSON files

## Code Generation Methods

### Method 1: From Local ABI File

Generate interfaces from ABI files on your local system:

```bash
# Basic usage
eth_rpc codegen load contract_abi.json -o my_contract.py -c MyContract

# With custom output location
eth_rpc codegen load ./abis/uniswap_v3_pool.json \
    --output ./contracts/uniswap_pool.py \
    --contract-name UniswapV3Pool
```

**Input formats supported:**
- Direct ABI array: `[{"type": "function", ...}, ...]`
- Truffle/Hardhat format: `{"abi": [...], "bytecode": "0x...", ...}`

### Method 2: From Block Explorers

Generate interfaces directly from verified contracts:

```bash
# Ethereum mainnet (Etherscan)
eth_rpc codegen explorer \
    --address 0xA0b86a33E6441b8e776f1c0b8e8e8e8e8e8e8e8e \
    --api-key YOUR_ETHERSCAN_KEY \
    --contract-name USDC \
    --output usdc.py

# Arbitrum (Arbiscan)
eth_rpc codegen explorer \
    --network arbitrum \
    --address 0x... \
    --api-key YOUR_ARBISCAN_KEY \
    --contract-name ArbitrumToken

# Base (Basescan)
eth_rpc codegen explorer \
    --network base \
    --address 0x... \
    --api-key YOUR_BASESCAN_KEY \
    --contract-name BaseToken
```

**Supported Networks:**
- `ethereum` - Ethereum mainnet (Etherscan)
- `arbitrum` - Arbitrum One (Arbiscan)
- `base` - Base mainnet (Basescan)

## Generated Code Structure

### Simple Function Example

**Input ABI:**
```json
{
    "name": "balanceOf",
    "type": "function",
    "inputs": [{"name": "owner", "type": "address"}],
    "outputs": [{"name": "", "type": "uint256"}],
    "stateMutability": "view"
}
```

**Generated Code:**
```python
from typing import Annotated
from eth_rpc import ProtocolBase, ContractFunc
from eth_rpc.types import primitives, Name, NoArgs, Struct

class MyToken(ProtocolBase):
    balance_of: ContractFunc[
        primitives.address,      # Input: single address
        primitives.uint256       # Output: token balance
    ]
```

### Complex Function with Structs

**Input ABI:**
```json
{
    "name": "getReserves",
    "type": "function",
    "inputs": [],
    "outputs": [
        {"name": "reserve0", "type": "uint112"},
        {"name": "reserve1", "type": "uint112"},
        {"name": "blockTimestampLast", "type": "uint32"}
    ],
    "stateMutability": "view"
}
```

**Generated Code:**
```python
class UniswapPair(ProtocolBase):
    get_reserves: ContractFunc[
        NoArgs,                                           # No inputs
        tuple[primitives.uint112, primitives.uint112, primitives.uint32]  # Multiple outputs
    ]
```

### Function Name Mapping

The generator automatically converts function names to Python conventions:

| Solidity Name | Python Name | Reason |
|---------------|-------------|---------|
| `balanceOf` | `balance_of` | snake_case convention |
| `WETH` | `WETH` | All caps preserved |
| `getReserves` | `get_reserves` | snake_case conversion |

When names differ, the generator uses `Annotated` types:

```python
# Original function name preserved in metadata
get_reserves: Annotated[
    ContractFunc[NoArgs, tuple[primitives.uint112, primitives.uint112, primitives.uint32]],
    Name("getReserves")
]
```

## Advanced Options

### Struct Name Handling

Control how struct names are generated:

```bash
# Full struct names (default)
eth_rpc codegen load abi.json -c MyContract --full-struct-names
# Generates: ContractNameStructName

# Short struct names
eth_rpc codegen load abi.json -c MyContract
# Generates: StructName
```

### Custom Output Formatting

The generated code follows these conventions:
- **Imports**: All necessary imports at the top
- **Structs**: Defined before the main contract class
- **Functions**: Ordered as they appear in the ABI
- **Type Annotations**: Full type information for all parameters

## Usage Examples

### Generated ERC20 Interface

```python
# Generated from ERC20 ABI
class ERC20Token(ProtocolBase):
    name: ContractFunc[NoArgs, str]
    symbol: ContractFunc[NoArgs, str]
    decimals: ContractFunc[NoArgs, primitives.uint8]
    total_supply: ContractFunc[NoArgs, primitives.uint256]
    balance_of: ContractFunc[primitives.address, primitives.uint256]
    transfer: ContractFunc[
        tuple[primitives.address, primitives.uint256],
        bool
    ]
    approve: ContractFunc[
        tuple[primitives.address, primitives.uint256],
        bool
    ]

# Usage
token = ERC20Token[Ethereum](address="0x...")
balance = await token.balance_of(user_address).get()
tx_hash = await token.transfer(recipient, amount).execute(wallet)
```

### Generated Uniswap V3 Pool Interface

```python
# Generated from Uniswap V3 Pool ABI
class UniswapV3Pool(ProtocolBase):
    token0: ContractFunc[NoArgs, primitives.address]
    token1: ContractFunc[NoArgs, primitives.address]
    fee: ContractFunc[NoArgs, primitives.uint24]
    
    swap: ContractFunc[
        tuple[
            primitives.address,    # recipient
            bool,                  # zeroForOne
            primitives.int256,     # amountSpecified
            primitives.uint160,    # sqrtPriceLimitX96
            bytes                  # data
        ],
        tuple[primitives.int256, primitives.int256]  # amount0, amount1
    ]

# Usage with full type safety
pool = UniswapV3Pool[Ethereum](address="0x...")
token0_addr = await pool.token0().get()
amounts = await pool.swap(recipient, True, amount, price_limit, b"").execute(wallet)
```

## Best Practices

### 1. Organize Generated Files
```
contracts/
├── tokens/
│   ├── erc20.py
│   ├── usdc.py
│   └── weth.py
├── dex/
│   ├── uniswap_v2_pair.py
│   ├── uniswap_v3_pool.py
│   └── sushiswap_pair.py
└── lending/
    ├── aave_pool.py
    └── compound_ctoken.py
```

### 2. Version Control
- **Include Generated Files**: Commit generated interfaces to version control
- **Regenerate on Updates**: Update interfaces when contracts are upgraded
- **Document Sources**: Include comments about ABI sources and generation dates

### 3. Testing Generated Interfaces
```python
import pytest
from contracts.tokens.usdc import USDC

@pytest.mark.asyncio
async def test_usdc_interface():
    usdc = USDC[Ethereum](address="0xA0b86a33E6441b8e776f1c0b8e8e8e8e8e8e8e8e")
    
    # Test type safety
    name: str = await usdc.name().get()
    assert isinstance(name, str)
    
    # Test parameter validation
    with pytest.raises(TypeError):
        await usdc.balance_of("invalid_address").get()
```

## Troubleshooting

### Common Issues

**1. ABI Format Errors**
```bash
# Error: Invalid ABI format
# Solution: Ensure ABI is valid JSON array or object with "abi" key
```

**2. Network Not Supported**
```bash
# Error: Network 'polygon' not supported
# Solution: Use supported networks (ethereum, arbitrum, base) or use local ABI
```

**3. Contract Not Verified**
```bash
# Error: Could not fetch ABI
# Solution: Ensure contract is verified on block explorer
```

**4. API Key Issues**
```bash
# Error: Invalid API key
# Solution: Get valid API key from respective block explorer
```

### Performance Considerations

- **Large ABIs**: Consider splitting large contracts into multiple interfaces
- **Struct Complexity**: Use `--full-struct-names` for complex contracts with many structs
- **Generation Time**: Large contracts may take time to process all functions

The code generation system provides a robust foundation for type-safe smart contract interactions, eliminating common errors while providing excellent developer experience and AI compatibility.
