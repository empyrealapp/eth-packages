# Contracts

## Contract Class

The [Contract class](/api/contract/){.internal-link} is a fundamental component in our system, representing a smart contract on the blockchain. It provides a typed, structured way to interact with and manage onchain contract interactions.

### Overview

A `Contract` instance encapsulates the following key elements:

- Contract address
- Contract Interface

### Key Features

1. **Method Invocation**: Call contract methods easily.
2. **Event Listening**: Subscribe to and handle contract events.
3. **State Reading**: Read the current state of the contract.
4. **Transaction Sending**: Send transactions to modify the contract state.

### Basic Usage

The real focus is on making it easier to interact with deployed smart contracts and having some greater type safety.  For example, say you want to interact with a contract you just deployed, ie:

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
from eth_rpc.types import METHOD, HexStr, Name, primitives


class MyContract(ProtocolBase):
    foo: ContractFunc[
        list[primitives.address],  # input type is a list of addresses
        Annotated[bool, Name("success")],  # response type is a boolean
    ] = METHOD # this is necessary for the type checker to recognize it as a contract method

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
