from inspect import isclass
from types import GenericAlias
from typing import Annotated, get_args, get_origin

from eth_abi import encode
from eth_account import Account
from eth_hash.auto import keccak
from eth_typing import ChecksumAddress, HexAddress, HexStr
from pydantic import Field

from .basic import ALL_PRIMITIVES
from .primitives import bytes32
from .struct import Struct


class EIP712Model(Struct):
    """
    The EIP712Model adds additional methods to the Struct class, allowing for
    a struct to be easily hashed for signing.  This is utilized for EIP-712, which
    creates a standarized approach to serializing data.
    """

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
        elif isclass(type_) and issubclass(type_, EIP712Model):
            return [type_.type_string()] + list(type_.get_nested_types())
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
            type_string += f"{type_str} {name},"
        encoded_typestr: bytes = (
            f'{cls.struct_name()}({type_string.rstrip(",")})'.encode("utf-8")
        )
        return encoded_typestr + b"".join(set(nested_types))

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

    @staticmethod
    def recover(
        message: bytes,
        vrs: tuple[int, HexStr, HexStr] | None = None,
        signature: bytes | None = None,
    ):
        if vrs:
            return Account._recover_hash(message, vrs=vrs)
        return Account._recover_hash(message, signature=signature)


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
