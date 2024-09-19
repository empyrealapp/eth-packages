# Differences From web3.py


## RPC Methods

For most Python developers building blockchain apps, web3.py is the dominant library that provides services for interacting with the Ethereum rpc and calling contracts.  However, it has limitations in type safety due to it using raw ABIS for contract signatures. The result is a lack of type safety in contract invocations, where you are not able to get type safety via static analysis or runtime type checking. To address this, eth-packages introduces type safety via [pydantic](https://docs.pydantic.dev/latest/), which establishes runtime type safety and allows the type checker to catch many bugs before they happen.

For example, web3.py RPC endpoints return a dictionary, rather than a runtime safe struct, ie:

```bash
>>> w3.eth.get_block('latest')
{'difficulty': 1,
 'gasLimit': 6283185,
 'gasUsed': 0,
 'hash': HexBytes('0x53b983fe73e16f6ed8178f6c0e0b91f23dc9dad4cb30d0831f178291ffeb8750'),
 'logsBloom': HexBytes('0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
 'miner': '0x0000000000000000000000000000000000000000',
 'mixHash': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'),
 'nonce': HexBytes('0x0000000000000000'),
 'number': 0,
 'parentHash': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000'),
 'proofOfAuthorityData': HexBytes('0x0000000000000000000000000000000000000000000000000000000000000000dddc391ab2bf6701c74d0c8698c2e13355b2e4150000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'),
 'receiptsRoot': HexBytes('0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421'),
 'sha3Uncles': HexBytes('0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347'),
 'size': 622,
 'stateRoot': HexBytes('0x1f5e460eb84dc0606ab74189dbcfe617300549f8f4778c3c9081c119b5b5d1c1'),
 'timestamp': 0,
 'totalDifficulty': 1,
 'transactions': [],
 'transactionsRoot': HexBytes('0x56e81f171bcc55a6ff8345e692c0f86e5b48e01b996cadc001622fb5e363b421'),
 'uncles': []}
```

With eth_rpc, you get back a [Block](/api/block/){.internal-link},
```bash
>>> block = await Block.latest()
<Block number=20779350>
```

---

## Contracts

If you want to interact with a contract with web3.py, you do something like this:

```python
address = '0x1f9840a85d5aF5bf1D1762F925BDADdC4201F988'
abi = '[{"inputs":[{"internalType":"address","name":"account","type":"address"},{"internalType":"address","name":"minter_","type":"address"},...'
contract_instance = w3.eth.contract(address=address, abi=abi)

# read state:
contract_instance.functions.storedValue().call()
```

The contract invocation is not providing you with typed data, and as the call gets more complicated, the return type gets more difficult to deal with.


With `eth_rpc`, you do not need to import the abi, but set the types.  Likewise, the typed struct can be generated directly from the contract ABI, but you also get the benefit of type safe code.  By setting these arguments on the ContractFunc, the type signature is inferred in the class.  A contract is structured like:

```python
class MyContract(ProtocolBase):
    name: Annotated[
        ContractFunc[NoArgs, primitives.uint256],
        Name("storedValue")
    ] = METHOD

my_contract = MyContract(address=address)
response: int = await my_contract.stored_value().get()
```

By declaring your output types as pydantic structs, you also can enforce runtime type checking, ie.

```python
class RequestArgs(BaseModel):
    name: str
    age: primitives.uint8


class Response(BaseModel):
    title: str
    pupils: list[primitives.uint256]


# you define your Contract using type hints for each method with Generic Args for the Input and Output types
class MyContract(ProtocolBase):
    get_pupils: Annotated[
        ContractFunc[RequestArgs, Response],
        Name("get_pupils")
    ] = METHOD

my_contract = MyContract(address=address)
# you can build your request as a pydantic BaseModel
request = RequestArgs(name="fred", age=100)

# The response is now also a pydantic BaseModel
response: Response = await my_contract.get_pupils(request).get()
```
