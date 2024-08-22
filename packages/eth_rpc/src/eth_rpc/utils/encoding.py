from eth_abi import encode
from eth_rpc.types import primitives


def encode_to_string(word):
    return encode(("string",), (word,))


def encode_to_bytes(word: str, type: primitives.BYTES_TYPES = primitives.bytes32):
    return encode((type.__name__,), (word.encode("utf-8"),))
