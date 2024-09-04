import math
from typing import Annotated, Any, Literal, get_args

from pydantic import (
    BeforeValidator,
    GetCoreSchemaHandler,
    SerializerFunctionWrapHandler,
    ValidationInfo,
)
from pydantic.functional_serializers import WrapSerializer
from pydantic_core import core_schema

from . import primitives

ALL_PRIMITIVES = [x for x in dir(primitives) if x[0].islower() and x[0] != "_"]
BLOCK_STRINGS = Literal["latest", "earliest", "pending", "safe", "finalized"]


class HexInt(int):
    """
    This enables an integer to load from a hex str to an int, or to be loaded as an int directly
    """

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


# wraps an int to a hex, or preserves the block_string
def hex_int_wrap(v: Any, nxt: SerializerFunctionWrapHandler) -> str:
    if v in get_args(BLOCK_STRINGS):
        return v
    return hex(v)


def number_to_bytes(number):
    nibble_count = int(math.log(number, 256)) + 1
    hex_string = "{:0{}x}".format(number, nibble_count * 2)
    return bytes.fromhex(hex_string)[:32]


def hex_str_to_bytes(v, info):
    if isinstance(v, bytes):
        return v
    elif v == "":
        return b""
    return number_to_bytes(int(v, 16))


# A Custom Integer type that loads from hex string and serializes to hex string
# TODO: make this a BlockNumber type and support block strings too
HexInteger = Annotated[HexInt, WrapSerializer(hex_int_wrap)]

# references to a block, either the rpc terms or a HexInteger
BlockReference = HexInteger | BLOCK_STRINGS

Bytes32Hex = Annotated[
    primitives.bytes32,
    BeforeValidator(hex_str_to_bytes),
    WrapSerializer(lambda x, y, z: x.hex()),
]
