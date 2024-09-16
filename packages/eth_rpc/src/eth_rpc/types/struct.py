from inspect import isclass
from typing import Any, get_args, get_origin

from eth_abi import decode, encode
from eth_typing import HexStr
from pydantic import BaseModel


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
