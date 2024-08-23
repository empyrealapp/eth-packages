from inspect import isclass
from types import GenericAlias
from typing import get_args

from eth_abi import encode
from eth_account.account import Account, LocalAccount, SignableMessage
from eth_account.datastructures import SignedMessage
from eth_hash.auto import keccak
from eth_typing import HexAddress
from pydantic import BaseModel, Field

from .struct import Struct


def encode_packed_array(type_, values):
    if type_ == "string":
        return encode(
            [type_] * len(values),
            [keccak(value.encode("utf-8")) for value in values],
        )
    return encode(
        [type_] * len(values),
        values,
    )


class Domain(BaseModel):
    name: str
    version: str
    chain_id: int = Field(serialization_alias="chainId")
    verifying_contract: HexAddress = Field(serialization_alias="verifyingContract")

    def model_dump(self, by_alias=True, **kwargs):
        return super().model_dump(by_alias=by_alias, **kwargs)

    def hash(self):
        hash = keccak(
            b"EIP712Domain(string name,string version,uint256 chainId,address verifyingContract)"
        )
        return keccak(
            encode(
                ["bytes32", "bytes32", "bytes32", "uint256", "address"],
                [
                    hash,
                    keccak(self.name.encode("utf-8")),
                    keccak(self.version.encode("utf-8")),
                    self.chain_id,
                    self.verifying_contract,
                ],
            )
        )


class EIP712Model(Struct):
    @classmethod
    def name(cls) -> str:
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
        encoded_typestr = f'{cls.__name__}({type_string.rstrip(",")})'.encode("utf-8")
        return encoded_typestr

    @classmethod
    def typehash(cls):
        return keccak(cls.type_string())

    def hash(self):
        types = ["bytes32"]
        values = [self.__class__.typehash()]
        for name, field_data in self.model_fields.items():
            value = getattr(self, name)
            type_ = field_data.annotation
            if isinstance(type_, GenericAlias):
                (arg,) = get_args(type_)
                types.append("bytes32")
                if isclass(arg) and issubclass(arg, EIP712Model):
                    hashed_arr = []
                    for row in value:
                        hashed_arr.append(row.hash())
                    encoding = keccak(
                        encode_packed_array(
                            "bytes32",
                            hashed_arr,
                        )
                    )
                    values.append(encoding)
                else:
                    arg_name = self.transform(arg)
                    values.append(keccak(encode_packed_array(arg_name, value)))
            elif isclass(type_) and issubclass(type_, EIP712Model):
                types.append("bytes32")
                values.append(value.hash())
            else:
                type_name = self.transform(type_)
                if type_name == "string":
                    types.append("bytes32")
                    values.append(keccak(value.encode("utf-8")))
                else:
                    types.append(type_name)
                    values.append(value)
        return keccak(encode(types, values))

    def model_dump(self, by_alias=True, **kwargs):
        return super().model_dump(by_alias=by_alias, **kwargs)


class DomainTypes(Struct):
    types: list[type[EIP712Model]]

    def build(self):
        response = {}
        for type in self.types:
            response[type.__name__] = type.build()
        return response


def hash_eip712_bytes(domain: Domain, struct: EIP712Model):
    joined = b"\x19\x01" + domain.hash() + struct.hash()
    return keccak(joined)


def sign(message: SignableMessage, acc: LocalAccount) -> SignedMessage:
    return Account.sign_message(message, acc.key)
