from eth_typing import ChecksumAddress, HexAddress, HexStr
from eth_utils import to_checksum_address


def address_to_topic(address: str) -> HexStr:
    return HexStr("0x{:064x}".format(int(address, 16)))


def to_checksum(address: str | HexAddress | ChecksumAddress) -> ChecksumAddress:
    return ChecksumAddress(HexAddress(HexStr(to_checksum_address(address))))
