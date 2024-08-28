from inspect import isclass
from types import GenericAlias
from typing import get_args, get_origin

from eth_typing import ChecksumAddress, HexAddress, HexStr
from eth_rpc.types import Struct, primitives
from eth_rpc.utils import is_annotation

ALL_PRIMITIVES = [x for x in dir(primitives) if x[0].islower() and x[0] != "_"]


def transform_primitive(type_):
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

    if is_annotation(type_):
        return transform_primitive(get_args(type_)[0])
    if isinstance(type_, GenericAlias):
        if get_origin(type_) == list:
            (arg,) = get_args(type_)
            return f"{transform_primitive(arg)}[]"
        elif get_origin(type_) == tuple:
            args = get_args(type_)
            tuple_args = ','.join(
                transform_primitive(a) for a in args
            )
            return f"({tuple_args})"
        else:
            raise ValueError(f"Unknown GenericAlias: {type_}")
    elif isclass(type_) and issubclass(type_, Struct):
        args = [arg.annotation for arg in type_.model_fields.values()]
        return transform_primitive(tuple[*args])  # type: ignore
    return transform_primitive(type_)
