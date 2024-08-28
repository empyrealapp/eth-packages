from inspect import isclass
from types import GenericAlias
from typing import NamedTuple, Optional, get_args, get_origin

from eth_abi import encode
from eth_rpc.types import primitives
from eth_typing import HexStr
from eth_utils import to_bytes, to_hex
from pydantic import BaseModel

from ..types import Name
from .types import is_annotation, transform_primitive

ALL_PRIMITIVES = [x for x in dir(primitives) if x[0].islower() and x[0] != "_"]


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
    """Converts a basemodel to an argument string"""
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


def convert_with_name(type, with_name: bool = False):
    name = ""
    # unwrap annotations
    if is_annotation(type):
        type, *annotations = get_args(type)
        if with_name:
            for annotation in annotations:
                if isinstance(annotation, Name):
                    name = annotation.value
    # if it's a list or a tuple
    if isinstance(type, GenericAlias):
        if get_origin(type) in [list, "list"]:
            list_type = get_args(type)[0]
            converted_list_type = convert_with_name(list_type)
            # if the list type is a tuple:
            if isinstance(converted_list_type, list):
                converted_list_type = f"({','.join(converted_list_type)})"
            return f"{converted_list_type}[] {name}".strip()
        else:
            tuple_args = [convert_with_name(t, with_name=with_name) for t in get_args(type)]
            return tuple_args
    elif getattr(type, "__orig_bases__", [None])[0] == NamedTuple:
        return f"({','.join([convert_with_name(t) for t in type.__annotations__.values()])}) {name}".strip()
    elif isclass(type) and issubclass(type, BaseModel):
        return f"({convert_base_model(type, with_name=with_name, as_tuple=True)}) {name}".strip()
    return f"{transform_primitive(type)} {name}".strip()
