from types import GenericAlias
from typing import get_args

from eth_abi import encode
from eth_rpc.utils import convert_base_model
from eth_typing import ChecksumAddress, HexAddress, HexStr
from pydantic import BaseModel

from . import primitives

ALL_PRIMITIVES = [x for x in dir(primitives) if x[0].islower() and x[0] != "_"]


class Struct(BaseModel):
    """
    This is a type used to denote a solidity struct.  It is necessary
    to set this so the encoder knows to treat it as a single struct,
    and not a list of fields.

    For example, (uint8,bytes32) will encode differently from ((uint8,bytes32))

    One is a field with two arguments, the other is a field with a single argument,
        that is a struct with two fields
    """

    @staticmethod
    def transform(type_):
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
            return f"{arg.__name__}[]"
        return type_.__name__

    def to_bytes(self):
        # TODO: this should be able to handle recursive types, it will fail if the depth is more than 2
        types = ",".join(convert_base_model(self.__class__))
        values = []
        for _, value in self:
            # this generally works, but should be revisited
            if (
                isinstance(value, list)
                and len(value) > 0
                and isinstance(value[0], Struct)
            ):
                value = [tuple(v.model_dump().values()) for v in value]
            elif isinstance(value, Struct):
                value = tuple(value.model_dump().values())
            values.append(value)
        return encode([f"({types})"], [tuple(values)])
