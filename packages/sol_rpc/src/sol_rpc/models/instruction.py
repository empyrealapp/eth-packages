from typing import Generic, TypeVar, Union

from pydantic import BaseModel

from sol_rpc.types.primitives import PrimitiveArgType


class Struct(BaseModel):
    pass


StructArgType = Union[
    Struct,
    PrimitiveArgType,
    "Vector[StructArgType]",
    "Array[StructArgType]",
]

T = TypeVar("T", bound=StructArgType)


class Array(BaseModel, Generic[T]):
    values: list[T]
    length: int

    def __init__(self, values: list[T], **kwargs):
        super().__init__(values=values, length=len(values), **kwargs)


class Vector(BaseModel, Generic[T]):
    values: list[T]

    def __init__(self, values: list[T], **kwargs):
        super().__init__(values=values, **kwargs)
