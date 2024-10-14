from inspect import isclass
from types import GenericAlias
from typing import Annotated, Any, get_args, get_origin

from eth_abi import decode, encode
from eth_typing import ChecksumAddress, HexAddress, HexStr
from pydantic import BaseModel

from .basic import ALL_PRIMITIVES


class Struct(BaseModel):
    """
    This is a type used to denote a solidity struct.  It is necessary
    to set this so the encoder knows to treat it as a single struct,
    and not a list of fields.

    For example, (uint8,bytes32) will encode differently from ((uint8,bytes32))

    One is a field with two arguments, the other is a field with a single argument,
        that is a struct with two fields
    """

    @classmethod
    def to_tuple_type(cls):
        lst = cls.to_type_list()
        return f"({','.join(lst)})"

    @classmethod
    def to_type_list(cls):
        from eth_rpc.utils.types import transform_primitive

        lst = []
        for _, field in cls.model_fields.items():
            type_ = field.annotation
            lst.append(transform_primitive(type_))
        return lst

    @classmethod
    def convert(cls, arg):
        if isinstance(arg, list):
            return [cls.convert(a) for a in arg]
        elif isinstance(arg, tuple):
            return tuple(cls.convert(a) for a in arg)
        elif isinstance(arg, Struct):
            return tuple(cls.convert(getattr(arg, a)) for a in arg.model_fields)
        return arg

    def to_bytes(self):
        types = self.to_tuple_type()
        values = []
        for _, value in self:
            values.append(self.convert(value))
        return encode([types], [tuple(values)])

    @classmethod
    def cast(cls, type_, args):
        if get_origin(type_) == list:
            (type_,) = get_args(type_)
            return [cls.cast(type_, arg) for arg in args]
        elif get_origin(type_) == tuple:
            tuple_types = get_args(type_)
            return tuple(cls.cast(type_, arg) for type_, arg in zip(tuple_types, args))
        elif isclass(type_) and issubclass(type_, Struct):
            return type_._build(args)
        return args

    @classmethod
    def from_bytes(cls, data_: bytes | HexStr):
        if isinstance(data_, str):
            bytes_ = bytes.fromhex(data_.removeprefix("0x"))
        else:
            bytes_ = data_
        types = cls.to_tuple_type()
        decoded = decode([types], bytes_)[0]
        return cls._build(decoded)

    @classmethod
    def from_tuple(cls, data: list[Any]):
        return cls._build(data)

    @classmethod
    def _build(cls, data):
        zipped = dict(zip(cls.model_fields.keys(), data))
        fields = [field.annotation for field in cls.model_fields.values()]
        response = {}
        for field, (name, value) in zip(fields, zipped.items()):
            response[name] = cls.cast(field, value)
        return cls(**response)

    @classmethod
    def struct_name(cls) -> str:
        """Override this if you want the struct name to be different from the class name"""
        return cls.__name__

    @staticmethod
    def transform(type_):
        mapping = {
            str: "string",
            int: "uint256",  # defaults to uint256
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
            return f"{arg.__name__}[]"
        return type_.__name__

    @classmethod
    def get_nested_types(cls):
        for _, field in cls.model_fields.items():
            for item in cls._get_nested_types(field.annotation):
                yield item

    @classmethod
    def _get_nested_types(cls, type_) -> list:
        if get_origin(type_) == list:
            return cls._get_nested_types(get_args(type_)[0])
        elif get_origin(type_) == tuple:
            args = get_args(type_)
            return [
                item
                for subl in [cls._get_nested_types(arg) for arg in args]
                for item in subl
            ]
        elif get_origin(type_) == Annotated:
            return cls._get_nested_types(get_args(type_)[0])
        return []

    @classmethod
    def type_string(cls) -> bytes:
        type_string: str = ""
        nested_types = list(cls.get_nested_types())
        for name, field_data in cls.model_fields.items():
            name = field_data.serialization_alias or name
            type_ = field_data.annotation

            if isinstance(type_, GenericAlias):
                if get_origin(type_) == list:
                    (arg,) = get_args(type_)
                    type_str = f"{cls.transform(arg)}[]"
                elif get_origin(type_) == tuple:
                    args = get_args(type_)
                    type_str = f"({','.join([cls.transform(arg) for arg in args])})"
            else:
                type_str = cls.transform(type_)
            type_string += f"{type_str},"
        encoded_typestr: bytes = (
            f'{cls.struct_name()}({type_string.rstrip(",")})'.encode("utf-8")
        )
        return encoded_typestr + b"".join(set(nested_types))
