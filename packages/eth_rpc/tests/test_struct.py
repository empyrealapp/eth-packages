from eth_rpc.types import Struct


class A(Struct):
    a: bool
    b: int


class B(Struct):
    a: list[A]
    b: A
    c: list[list[A]]


def test_struct_hash():
    assert A.to_tuple_type() == "(bool,uint256)"
    assert A.to_type_list() == ["bool", "uint256"]
    assert B.to_tuple_type() == "((bool,uint256)[],(bool,uint256),(bool,uint256)[][])"

    assert A(a=True, b=255).to_bytes().hex() == (
        "0000000000000000000000000000000000000000000000000000000000000001"
        "00000000000000000000000000000000000000000000000000000000000000ff"
    )
