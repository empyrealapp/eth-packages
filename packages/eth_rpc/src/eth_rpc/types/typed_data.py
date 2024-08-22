from inspect import isclass
from types import GenericAlias
from typing import get_args

from eth_account.account import Account, LocalAccount, SignableMessage
from eth_account.datastructures import SignedMessage
from eth_account.messages import encode_typed_data
from eth_typing import ChecksumAddress, HexAddress, HexStr
from pydantic import BaseModel, Field

from . import primitives
from .struct import Struct

ALL_PRIMITIVES = [x for x in dir(primitives) if x[0].islower() and x[0] != "_"]


class Domain(BaseModel):
    name: str
    version: str
    chain_id: int = Field(serialization_alias="chainId")
    verifying_contract: HexStr = Field(serialization_alias="verifyingContract")

    def model_dump(self, by_alias=True, **kwargs):
        return super().model_dump(by_alias=by_alias, **kwargs)


class EIP712Model(Struct):
    @classmethod
    def name(cls) -> str:
        return cls.__name__

    @staticmethod
    def transform(type_):
        mapping = {
            str: "string",
            int: "uint256",  # defaults to uint
            HexAddress: "address",
            ChecksumAddress: "address",
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
    def get_submodels(cls):
        for _, field_data in cls.model_fields.items():
            type_ = field_data.annotation
            if isclass(type_) and issubclass(type_, EIP712Model):
                yield type_
                yield from type_.get_submodels()
            elif isinstance(type_, GenericAlias):
                (arg,) = get_args(type_)
                if isclass(arg) and issubclass(arg, EIP712Model):
                    yield arg
                    yield from arg.get_submodels()

    @classmethod
    def get_models(cls):
        models = [cls]
        for _, field_data in cls.model_fields.items():
            if issubclass(field_data.annotation, EIP712Model):
                models.append(field_data.annotation)

        return models

    @classmethod
    def build(cls):
        response = []
        for field_name, field_data in cls.model_fields.items():
            response.append(
                {
                    "name": field_data.alias or field_name,
                    "type": cls.transform(field_data.annotation),
                },
            )
        return response

    def model_dump(self, by_alias=True, **kwargs):
        return super().model_dump(by_alias=by_alias, **kwargs)


class DomainTypes(Struct):
    types: list[type[EIP712Model]]

    def build(self):
        response = {}
        for type in self.types:
            response[type.__name__] = type.build()
        return response


def encode_data(domain: Domain, message_data: EIP712Model) -> SignableMessage:
    class_set: set[EIP712Model] = set()
    for type_ in message_data.get_submodels():
        class_set.add(type_)
    signable_message = encode_typed_data(
        domain.model_dump(),
        {klass.name(): klass.build() for klass in class_set},
        message_data.model_dump(),
    )
    return signable_message


def sign(message: SignableMessage, acc: LocalAccount) -> SignedMessage:
    return Account.sign_message(message, acc.key)
