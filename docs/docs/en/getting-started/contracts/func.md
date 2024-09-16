# Contract Function Types

When building a contract function, you can utilize a variety of pythonic concepts to define your signature to be as easy to manipulate as possible.  Firstly, if you need to define a solidity `struct` you can utilize the `eth_rpc.types.Struct` class, and define your model inheriting from this class.  For example, if you had a smart contract with a function like:

!!! note
    This is not a realistic function signature, but it showcases multiple features of the ContractFunc class

```solidity
contract ExampleContract {
    enum Status {
        SUCCESS,
        FAILURE
    }

    struct Account {
        uint256 accountId;
        uint256 balance;
        bool isActive;
    }

    struct Transaction {
        uint256 recipientId;
        uint256 amount;
    }

    struct DepositResult {
        int256 balanceUpdate;
        Status status;
    }

    function depositFunds(Account memory account, Transaction[] memory transactions, uint256 deadline, bytes[] memory additionalArgs) external returns(bool success, DepositResult memory) {
        ...
    }
}
```

So this method, `depositFunds`, has a few characteristics.  It takes multiple structs, one as a direct argument and the other as a list of structs.  It also returns multiple values, one with an Enum field.  Now we can translate this directly to python types.

## Basic Imports

```python
from enum import IntEnum  # Its best to use IntEnum, since your enum fields need to be indexed from 0
from typing import Annotated  # This is used to attach additional information to fields

# this is used to wrap the Input/Output class of the ContractFunc
from pydantic import BaseModel

# these are the main types used in building a Contract
from eth_rpc import ContractFunc, ProtocolBase, Struct
from eth_rpc.types import METHOD, primitives
```

## Struct Definitions

Then we can define the internal types.  The `Status` Enum and the `Account` and `Transaction` Structs.  You need to define your fields as primitives/Structs, with the exception of bool and bytes.  Likewise if there are no args or return type you can provide `None` to indicate this.  Make sure to use the `Struct` type when referring to an onchain `Struct` or `tuple`, this helps the encoder/decoder to understand the onchain structure of the function.

```python
class Status(IntEnum):
    SUCCESS = 0
    FAILURE = 1


class Account(Struct):
    account_id: Annotated[
        primitives.uint256,
        Name("accountId"),
    ]
    balance: primitives.uint256
    is_active: Annotated[
        bool,
        Name("isActive"),
    ]

class Transaction(Struct):
    recipient_id: Annotated[
        primitives.uint256,
        Name("recipientId"),
    ]
    amount: primitives.uint256


class DepositResult(Struct):
    balance_updated: Annotated[
        primitives.int256,
        Name("balanceUpdate"),
    ]
    status: Status
```

## Defining the Input and Output types

Then we can define the objects for the Request and Response types.  Notice these are not `Struct`s.  That is because the encoder for a contract will encode a `Struct` argument differently from a list of parameters.  This is by design, so ensure you are only using `Struct`s to abstract actual struct types.

For functions that take a single argument, you can provide the raw type.  For example, you could define a function `balance: ContractFunc[primitives.address, primitives.uint256]` for a function that takes an `address` as an argument and returns a `uint256`.

```python
class DepositRequest(BaseModel):
    account: Account
    txs: list[Transaction]
    deadline: primitives.uint256
    additional_args: Annotated[
        list[bytes],
        Name("additionalArgs"),
    ]


class DepositResponse(BaseModel):
    success: bool
    result: DepositResult
```

## Building the Contract

With our types defined, we can now define the function `depositFunds` as a python function with type hints.  The `METHOD` is important because it indicates to the type checker this function does not require initialization.  If you change from CamelCase to snake_case, make sure to annotate the function with its name onchain, as this is used to calculate the function selector.

```python
class ExampleContract(ProtocolBase):
    deposit_funds: Annotated[
        ContractFunc[
            DepositRequest,
            DepositResponse,
        ],
        Name("depositFunc"),
     ] = METHOD

contract = ExampleContract(address=contract_address)

# this response object is now parsed back into a DepositResponse
response: DepositResponse = await contract.deposit_funds(
    DepositRequest(
        account=Account(account_id=1, balance=100, is_active=True),
        deadline=primitives.uint256(12345),
        additional_args=[b'123', b'456'],
    )
).get()
```
