from inspect import isclass
from types import GenericAlias
from typing import get_args

from eth_abi import encode
from eth_hash.auto import keccak
from eth_typing import HexAddress
from pydantic import Field

from .primitives import bytes32
from .struct import Struct


class EIP712Model(Struct):
    @classmethod
    def struct_name(cls) -> str:
        """Override this if you want the struct name to be different from the class name"""
        return cls.__name__

    @classmethod
    def type_string(cls):
        type_string = ""
        for name, field_data in cls.model_fields.items():
            name = field_data.serialization_alias or name
            type_ = field_data.annotation
            if isinstance(type_, GenericAlias):
                (arg,) = get_args(type_)
                type_str = f"{cls.transform(arg)}[]"
            else:
                type_str = cls.transform(type_)
            type_string += f"{type_str} {name},"
        encoded_typestr = f'{cls.struct_name()}({type_string.rstrip(",")})'.encode(
            "utf-8"
        )
        return encoded_typestr

    @classmethod
    def typehash(cls):
        return keccak(cls.type_string())

    def hash(self) -> bytes32:
        types = ["bytes32"]
        values = [self.__class__.typehash()]

        for name, field_data in self.model_fields.items():
            type_ = field_data.annotation
            value = getattr(self, name)

            # handle a list of structs or primitive
            if isinstance(type_, GenericAlias):
                types.append("bytes32")

                (arg,) = get_args(type_)
                arg_name = self.transform(arg)

                if isclass(arg) and issubclass(arg, EIP712Model):
                    hashed_arr = []
                    for row in value:
                        hashed_arr.append(row.hash())
                    encoding = keccak(
                        hash_packed_array(
                            "bytes32",
                            hashed_arr,
                        )
                    )
                    values.append(encoding)
                else:
                    values.append(keccak(hash_packed_array(arg_name, value)))
            elif isclass(type_) and issubclass(type_, EIP712Model):
                types.append("bytes32")
                values.append(value.hash())
            else:
                type_name = self.transform(type_)
                if type_name == "string":
                    types.append("bytes32")
                    values.append(keccak(value.encode("utf-8")))
                elif type_name == "bytes":
                    types.append("bytes32")
                    values.append(keccak(value))
                else:
                    types.append(type_name)
                    values.append(value)
        return bytes32(keccak(encode(types, values)))

    def model_dump(self, by_alias=True, **kwargs):
        return super().model_dump(by_alias=by_alias, **kwargs)


class Domain(EIP712Model):
    name: str
    version: str
    chain_id: int = Field(serialization_alias="chainId")
    verifying_contract: HexAddress = Field(serialization_alias="verifyingContract")

    @classmethod
    def struct_name(cls) -> str:
        return "EIP712Domain"


def hash_eip712_bytes(domain: Domain, struct: EIP712Model) -> bytes32:
    joined = b"\x19\x01" + domain.hash() + struct.hash()
    return bytes32(keccak(joined))


def hash_packed_array(type_, values) -> bytes:
    match type_:
        case "string":
            return encode(
                ["bytes32"] * len(values),
                [keccak(value.encode("utf-8")) for value in values],
            )
        case "bytes":
            return encode(
                ["bytes32"] * len(values),
                [keccak(value) for value in values],
            )
        case _:
            return encode(
                [type_] * len(values),
                values,
            )
