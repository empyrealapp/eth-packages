from typing import Self

from eth_abi import decode
from eth_hash.auto import keccak
from eth_typing import HexStr

from .struct import Struct


class EvmError(Struct):
    @classmethod
    def selector(cls):
        return f"0x{keccak(cls.type_string())[:4].hex()}"

    @classmethod
    def decode(cls, data: HexStr) -> Self:
        selector = cls.selector()
        if not data.startswith(selector):
            raise ValueError(f"Invalid selector for {cls.__name__}")
        data = HexStr(data.removeprefix(selector))
        tuple_type = cls.to_tuple_type()
        decoded = decode([tuple_type], bytes.fromhex(data))[0]
        return cls.from_tuple(decoded)
