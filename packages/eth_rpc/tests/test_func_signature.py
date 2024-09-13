from typing import Annotated

import pytest
from eth_abi import encode
from eth_rpc import FuncSignature
from eth_rpc.types import Name, NoArgs, Struct, primitives
from eth_rpc.utils.types import transform_primitive
from eth_typing import HexStr
from pydantic import BaseModel


class Inputs(BaseModel):
    x: primitives.uint256
    y: primitives.uint256
    z: list[primitives.address]
    a: primitives.address
    b: primitives.uint256
    c: list[primitives.address]
    d: primitives.uint256


class Outputs(BaseModel):
    x: Annotated[
        list[primitives.bytes32],
        Name("XX"),
    ]
    y: str


class DisputeNested(Struct):
    a: list[primitives.address]
    b: list[primitives.uint256]
    c: primitives.uint256
    d: primitives.uint16


class DisputeInput(BaseModel):
    first: DisputeNested
    second: primitives.address
    third: primitives.address


@pytest.mark.unit
def test_func_signature():
    func = FuncSignature[Inputs, Annotated[Outputs, Name("OUTPUT")]](
        name="swapExactTokensForETHWithPortfolios", alias="test_func"
    )
    # https://www.4byte.directory/signatures/?bytes4_signature=0x8b41f64c
    assert func.get_identifier() == "0x8b41f64c"
    assert func.get_inputs() == [
        "uint256",
        "uint256",
        "address[]",
        "address",
        "uint256",
        "address[]",
        "uint256",
    ]
    assert func.get_output() == ["bytes32[]", "string"]
    assert func._get_name(Outputs.__annotations__["x"]) == "XX"

    func = FuncSignature[
        tuple[int, list[primitives.address], list[bytes]],
        bool,
    ](name="makeProxyArbitraryTransactions")
    assert func.get_inputs() == ("uint256", "address[]", "bytes[]")
    assert func.get_identifier() == "0xbe430874"

    func = FuncSignature[
        tuple[list[primitives.address], list[primitives.uint96], list[bool]],
        bool,
    ](name="onBridgeOperatorsAdded")
    assert func.get_identifier() == "0x8f851d8a"

    func3 = FuncSignature[
        DisputeInput,
        bool,
    ](name="distribute")
    assert func3.get_identifier() == "0x2d3f5537"


@pytest.mark.unit
def test_map_to_str():
    assert transform_primitive(primitives.address) == "address"
    assert transform_primitive(str) == "string"
    assert transform_primitive(list[str]) == "string[]"
    assert transform_primitive(list[primitives.bytes32]) == "bytes32[]"


@pytest.mark.unit
def test_func_signature_types():
    func = FuncSignature[
        tuple[list[int], bool],
        list[str],
    ](name="func")
    assert func.get_inputs() == ("uint256[]", "bool")
    assert func.get_output() == "string[]"


@pytest.mark.unit
def test_func_encode() -> None:
    class Data(Struct):
        name: str
        valid: bool

    func = FuncSignature[
        tuple[primitives.bytes32, list[Data]],
        None,
    ](name="func")
    assert func.get_inputs() == ("bytes32", "(string,bool)[]")
    func.encode_call(
        inputs=(
            primitives.bytes32(b"123"),
            [Data(name="test", valid=True), Data(name="test2", valid=False)],
        )
    )


@pytest.mark.unit
def test_func_decode_struct_list() -> None:
    class MyNestedStruct(Struct):
        a: primitives.uint256
        b: primitives.uint256

    class MyStruct(Struct):
        x: primitives.uint256
        y: bool
        z: list[MyNestedStruct]

    func = FuncSignature[
        NoArgs,
        list[MyStruct],
    ](name="func")

    my_struct = MyStruct(x=1, y=True, z=[MyNestedStruct(a=1, b=2)])
    encoded_bytes = encode(
        ["(uint256,bool,(uint256,uint256)[])[]"], [[(1, True, [(1, 2)])]]
    )

    result = func.decode_result(HexStr(encoded_bytes.hex()))
    assert result[0] == my_struct
