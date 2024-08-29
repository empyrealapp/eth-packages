from typing import Optional

from eth_abi import encode
from eth_rpc.types import primitives
from eth_typing import HexStr
from eth_utils import to_bytes, to_hex
from pydantic import BaseModel

from .types import transform_primitive


def encode_to_string(word):
    return encode(("string",), (word,))


def encode_to_bytes(word: str, type: primitives.BYTES_TYPES = primitives.bytes32):
    return encode((type.__name__,), (word.encode("utf-8"),))


def hex_to_int(v: None | int | str) -> Optional[int]:
    if v is None:
        return None
    return int(v, 16) if isinstance(v, str) else v


def to_32byte_hex(val):
    return to_hex(to_bytes(val).rjust(32, b"\0"))


def to_hex_str(number: int | str) -> HexStr:
    if isinstance(number, int):
        return HexStr(hex(number))
    return HexStr(number)


# TODO: this can be combines with .types to simplify the type handling
def convert_base_model(
    base: type[BaseModel], with_name: bool = False, as_tuple: bool = False
):
    """Converts a BaseModel to an argument string"""
    lst = []
    for key, field_info in base.model_fields.items():
        field_type = field_info.annotation
        lst.append(
            transform_primitive(
                field_type,
                with_name=with_name,
                name=key,
            )
        )
    if as_tuple:
        return ",".join(lst)
    return lst
