from inspect import isclass
from types import GenericAlias
from typing import NamedTuple, Optional, get_args, get_origin

from eth_abi import encode
from eth_rpc.types import primitives
from eth_typing import HexStr
from eth_utils import to_bytes, to_hex
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from ..types import Name, map_type_to_str
from .types import is_annotation


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


def convert_base_model(
    base: type[BaseModel], with_name: bool = False, as_tuple: bool = False
):
    lst = []
    for key, field_info in base.model_fields.items():
        lst.append(_convert_field_info(key, field_info, with_name=with_name))
    if as_tuple:
        return ",".join(lst)
    return lst


def _convert_field_info(alias: str, field: FieldInfo, with_name: bool = False):
    name = "" if not with_name else alias
    field_type = field.annotation

    for metadata in field.metadata:
        if isinstance(metadata, Name) and with_name:
            name = metadata.value

    type_origin = get_origin(field_type)
    if type_origin == list:
        list_type = get_args(field_type)[0]
        converted_list_type = convert(list_type)
        if isinstance(converted_list_type, list):
            converted_list_type = f"({','.join(converted_list_type)})"
        return f"{converted_list_type}[] {name}".strip()
    elif type_origin == tuple:
        tuple_args = f"({','.join([convert(t) for t in get_args(field_type)])}) {name}"
        return tuple_args
    return f"{map_type_to_str(field_type)} {name}".strip()


def convert(type, with_name: bool = False):
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
            converted_list_type = convert(list_type)
            # if the list type is a tuple:
            if isinstance(converted_list_type, list):
                converted_list_type = f"({','.join(converted_list_type)})"
            return f"{converted_list_type}[] {name}".strip()
        else:
            tuple_args = [convert(t, with_name=with_name) for t in get_args(type)]
            return tuple_args
    elif getattr(type, "__orig_bases__", [None])[0] == NamedTuple:
        return f"({','.join([convert(t) for t in type.__annotations__.values()])}) {name}".strip()
    elif isclass(type) and issubclass(type, BaseModel):
        return f"({convert_base_model(type, with_name=with_name, as_tuple=True)}) {name}".strip()
    return f"{map_type_to_str(type)} {name}".strip()
