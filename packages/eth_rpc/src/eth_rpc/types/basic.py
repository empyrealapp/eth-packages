from types import GenericAlias
from typing import Annotated, Any, Literal, get_args

from eth_typing import ChecksumAddress, HexAddress, HexStr
from pydantic import (
    BaseModel,
    GetCoreSchemaHandler,
    SerializerFunctionWrapHandler,
    ValidationInfo,
)
from pydantic.functional_serializers import WrapSerializer
from pydantic_core import core_schema

from . import primitives

ALL_PRIMITIVES = [x for x in dir(primitives) if x[0].islower() and x[0] != "_"]
BLOCK_STRINGS = Literal["latest", "earliest", "pending", "safe", "finalized"]


class Empty(BaseModel): ...


class HexInt(int):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.with_info_after_validator_function(
            function=cls.validate,
            schema=handler(int | str),
            field_name=handler.field_name,
        )

    @classmethod
    def validate(cls, v, r: ValidationInfo):
        if isinstance(v, str):
            return int(v, 16)
        return int(v)


def hex_int_wrap(v: Any, nxt: SerializerFunctionWrapHandler) -> str:
    if v in get_args(BLOCK_STRINGS):
        return v
    return hex(v)


# A Custom Integer type that loads from hex string and serializes to hex string
# TODO: make this a BlockNumber type and support block strings too
HexInteger = Annotated[HexInt, WrapSerializer(hex_int_wrap)]
BlockReference = HexInteger | BLOCK_STRINGS


def map_type_to_str(type_: Any) -> str:
    """Convert a type to its solidity compatible format"""
    mapping = {
        str: "string",
        int: "uint256",  # defaults to uint
        HexAddress: "address",
        ChecksumAddress: "address",
        HexStr: "bytes",
    }
    if type_ in mapping:
        return mapping[type_]
    if str(type_) in ALL_PRIMITIVES:
        return str(type_)
    # handle list type
    if isinstance(type_, GenericAlias):
        (arg,) = get_args(type_)
        return f"{map_type_to_str(arg)}[]"
    return type_.__name__
