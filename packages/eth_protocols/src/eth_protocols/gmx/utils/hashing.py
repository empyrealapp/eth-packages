from eth_abi import encode
from eth_hash.auto import keccak


def create_hash(types: list[str], values: list[str]):
    return keccak(encode(types, values))


def create_hash_string(string: str):
    """
    Value to hash

    Parameters
    ----------
    string : str
        string to hash.

    Returns
    -------
    bytes
        hashed string.
    """
    return keccak(encode(["string"], [string]))
