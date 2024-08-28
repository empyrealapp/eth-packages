from types import GenericAlias
from typing import Annotated, get_args, get_origin

from eth_typing import HexAddress, HexStr, ChecksumAddress
from eth_rpc.types import primitives

ALL_PRIMITIVES = [x for x in dir(primitives) if x[0].islower() and x[0] != "_"]


def is_annotation(type_):
    return get_origin(type_) is Annotated


def convert_to_primitive_type_string(type_) -> str:
    """
    Converts an annotation to its equivalent primitive type, ie.
        list[tuple[int, str]] => "(uint256,string)[]"
    """
    mapping = {
        str: "string",
        int: "uint256",  # defaults to uint
        HexAddress: "address",
        ChecksumAddress: "address",
        HexStr: "bytes",
    }
    if type_ in mapping:
        return mapping[type_]
    if type_.__name__ in ALL_PRIMITIVES:
        return type_.__name__
    # handle list type
    if isinstance(type_, GenericAlias):
        origin = get_origin(type_)
        if origin == list:
            (arg,) = get_args(type_)
            type_ = convert_to_primitive_type_string(arg)
            return f"{type_}[]"
        elif origin == tuple:
            xargs = get_args(type_)
            args = ','.join(
                convert_to_primitive_type_string(t) for t in xargs
            )
            return f"({args})"
        else:
            raise ValueError(f"Unexpected GenericType: {origin}")

    raise ValueError(f"unknown type: {type_}")
