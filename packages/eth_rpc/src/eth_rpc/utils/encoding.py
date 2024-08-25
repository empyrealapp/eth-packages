from typing import Optional

from eth_abi import encode
from eth_rpc.types import primitives
from eth_typing import HexStr
from eth_utils import to_bytes, to_hex


def encode_to_string(word):
    return encode(("string",), (word,))


def encode_to_bytes(word: str, type: primitives.BYTES_TYPES = primitives.bytes32):
    return encode((type.__name__,), (word.encode("utf-8"),))


def hex_to_int(v: None | int | str) -> Optional[int]:
    if v is None:
        return None
    return int(v, 16) if isinstance(v, str) else v


def to_32byte_hex(val):
    return to_hex(to_bytes(val).rjust(32, b"\0"))


def to_hex_str(number: int | str) -> HexStr:
    if isinstance(number, int):
        return HexStr(hex(number))
    return HexStr(number)
