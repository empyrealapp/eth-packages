from typing import Annotated

from eth_rpc.types import Name, Struct
from pydantic import BaseModel


class A(Struct):
    x: int
    y: str
    z: list[bool]


class B(Struct):
    a: list[A]
    b: A
    c: Annotated[bool, Name("BOOL")]


class C(Struct):
    a: Annotated[tuple[A, B, list[B]], Name("tuples")]
    d: list[B]
    e: str


class D(BaseModel):
    a: Annotated[tuple[A, B, list[B]], Name("tuples")]
    d: list[B]
    e: str


def test_typing_nested_structs():
    A_str = "(uint256,string,bool[])"
    B_str = f"({A_str}[],{A_str},bool)"
    C_str = f"(({A_str},{B_str},{B_str}[]),{B_str}[],string)"

    assert C.to_tuple_type() == C_str


def test_load_struct():
    a1 = A(x=1, y="a", z=[True, False])
    a2 = A(x=2, y="b", z=[False, True])
    a3 = A(x=3, y="b", z=[False, True])
    a4 = A(x=4, y="b", z=[False, True])
    b1 = B(a=[a1, a2], b=a3, c=True)
    b2 = B(a=[a1, a2], b=a3, c=False)
    c = C(a=(a4, b1, [b2]), d=[b1.model_copy(), b2.model_copy()], e="final")

    assert A.from_bytes(a1.to_bytes()) == a1
    assert A.from_bytes(a2.to_bytes()) == a2
    assert A.from_bytes(a3.to_bytes()) == a3
    assert A.from_bytes(a4.to_bytes()) == a4

    assert B.from_bytes(b1.to_bytes()) == b1
    assert B.from_bytes(b2.to_bytes()) == b2

    assert C.from_bytes(c.to_bytes()) == c
