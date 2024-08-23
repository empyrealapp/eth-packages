from eth_typing import ChecksumAddress, HexAddress, HexStr
from eth_utils import to_checksum_address


def address_to_topic(address):
    return "0x{:064x}".format(int(address, 16))


def address_to_bytes32(address: str):
    return bytes.fromhex(address.ljust(66, "0")[2:])


def to_checksum(address: str | HexAddress) -> ChecksumAddress:
    return ChecksumAddress(HexAddress(HexStr(to_checksum_address(address))))
