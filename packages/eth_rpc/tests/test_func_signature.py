from typing import Annotated

import pytest
from eth_rpc import FuncSignature
from eth_rpc.types import Name, map_type_to_str, primitives
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


@pytest.mark.unit
def test_map_to_str():
    assert map_type_to_str(primitives.address) == "address"
    assert map_type_to_str(str) == "string"
    assert map_type_to_str(list[str]) == "string[]"
    assert map_type_to_str(list[primitives.bytes32]) == "bytes32[]"
