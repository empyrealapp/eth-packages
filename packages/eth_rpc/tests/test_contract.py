import os
from typing import Annotated

import pytest
from eth_abi import encode
from eth_rpc import ContractFunc, FuncSignature, set_alchemy_key
from eth_rpc.contract import EthResponse, ProtocolBase
from eth_rpc.networks import Arbitrum, Ethereum
from eth_rpc.types import METHOD, Name, NoArgs, Struct, primitives
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel


class AllowanceRequest(BaseModel):
    owner: primitives.address
    spender: primitives.address


class Token(ProtocolBase):
    name: ContractFunc[
        NoArgs,
        Annotated[primitives.string, Name("_name")],
    ] = METHOD
    balance_of: Annotated[
        ContractFunc[
            primitives.address,
            Annotated[primitives.uint256, Name("_name")],
        ],
        Name("balanceOf"),
    ] = METHOD
    allowance: ContractFunc[
        tuple[primitives.address, primitives.address],
        primitives.uint256,
    ] = METHOD
    allowance2: Annotated[
        ContractFunc[
            AllowanceRequest,
            primitives.uint256,
        ],
        Name("allowance"),
    ] = METHOD


@pytest.mark.contract
@pytest.mark.unit
def test_encode_signature():
    func = FuncSignature[NoArgs, primitives.string](name="name")
    assert func.encode_call(inputs=()) == "0x06fdde03"


@pytest.mark.unit
def test_set_network():
    usdt = Token[Ethereum](
        address=HexAddress(HexStr("0xdAC17F958D2ee523a2206206994597C13D831ec7"))
    )
    assert usdt._network == Ethereum

    usdc = Token[Arbitrum](address="0xaf88d065e77c8cc2239327c5edb3a432268e5831")
    assert usdc._network == Arbitrum

    # test that this didn't affect the usdt network
    assert usdt._network == Ethereum


@pytest.mark.asyncio(scope="session")
@pytest.mark.contract
async def test_contract() -> None:
    set_alchemy_key(os.environ["ALCHEMY_KEY"])

    usdt = Token[Ethereum](
        address=HexAddress(HexStr("0xdAC17F958D2ee523a2206206994597C13D831ec7"))
    )
    usdc = Token[Arbitrum](address="0xaf88d065e77c8cc2239327c5edb3a432268e5831")
    assert usdt._network == Ethereum
    assert usdc._network == Arbitrum

    assert await usdt.name().get() == "Tether USD"
    assert await usdc.name().get() == "USD Coin"

    binance_balance = await usdt.balance_of(
        "0xF977814e90dA44bFA03b6295A0616a897441aceC"
    ).get()
    binance_balance = await usdt.balance_of(
        "0xF977814e90dA44bFA03b6295A0616a897441aceC"
    ).get(block_number=20_604_386)
    assert binance_balance == 6600822508869000

    # check function with two args
    allowance = await usdt.allowance(
        "0x71AC0c3E825f095E56b81fBA11020f01893d4433",
        "0x38C5412464A03EfDc3820d227b24316C11729E0a",
    ).get(block_number=20604634)
    assert allowance == 126967536
    # check function using BaseModel for args
    allowance = await usdt.allowance2(
        "0x71AC0c3E825f095E56b81fBA11020f01893d4433",
        "0x38C5412464A03EfDc3820d227b24316C11729E0a",
    ).get(block_number=20604640)
    assert allowance == 0


@pytest.mark.unit
def test_multi_arg_func() -> None:
    response = EthResponse(
        func=FuncSignature[
            tuple[primitives.bytes32, primitives.bytes32, int],
            primitives.address,
        ](name="computeAddress"),
        result=HexStr(
            "0x0000000000000000000000008284ff4a6881edfa14435e1b140c9430e3a0ec5d"
        ),
    )

    assert response.decode() == "0x8284ff4a6881edfa14435e1b140c9430e3a0ec5d"


@pytest.mark.unit
def test_decode_struct() -> None:
    class SubStruct(Struct):
        x: bool
        y: list[primitives.uint256]

    class MyStruct(Struct):
        a: list[primitives.uint256]
        b: str
        c: list[SubStruct]

    my_struct = MyStruct(a=[1, 2, 3], b="test", c=[SubStruct(x=True, y=[1, 2, 3])])

    bytes_ = encode(
        ("(uint256[],string,(bool,uint256[])[])",),
        [([1, 2, 3], "test", [(True, [1, 2, 3])])],
    )
    assert my_struct.to_bytes().hex() == bytes_.hex()

    response = EthResponse(
        func=FuncSignature[
            NoArgs,
            MyStruct,
        ](name="computeAddress"),
        result=my_struct.to_bytes().hex(),
    )
    decoded = response.decode()

    assert isinstance(decoded, MyStruct)
    assert decoded.a == [1, 2, 3]
    assert decoded.b == "test"
    assert decoded.c[0].x
    assert decoded.c[0].y == [1, 2, 3]


@pytest.mark.unit
def test_decode_basemodel() -> None:
    class SubStruct(Struct):
        x: bool
        y: list[primitives.uint256]

    class MyStruct(BaseModel):
        a: list[primitives.uint256]
        b: str
        c: list[SubStruct]

    my_struct = MyStruct(a=[1, 2, 3], b="test", c=[SubStruct(x=True, y=[1, 2, 3])])
    bytes_ = encode(
        (
            "uint256[]",
            "string",
            "(bool,uint256[])[]",
        ),
        [[1, 2, 3], "test", [(True, [1, 2, 3])]],
    )

    response = EthResponse(
        func=FuncSignature[
            NoArgs,
            MyStruct,
        ](name="computeAddress"),
        result=HexStr(bytes_.hex()),
    )
    decoded = response.decode()
    assert decoded == my_struct
