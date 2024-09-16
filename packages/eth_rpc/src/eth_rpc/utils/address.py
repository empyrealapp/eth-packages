from eth_hash.auto import keccak
from eth_typing import ChecksumAddress, HexAddress, HexStr


def address_to_topic(address: str) -> HexStr:
    return HexStr("0x{:064x}".format(int(address, 16)))


def to_checksum(address: str) -> ChecksumAddress:
    norm_address = address.lower()
    address_hash = "0x" + keccak(norm_address[2:].encode("utf-8")).hex()
    return ChecksumAddress(
        HexAddress(
            HexStr(
                "0x"
                + "".join(
                    (
                        norm_address[i].upper()
                        if int(address_hash[i], 16) > 7
                        else norm_address[i]
                    )
                    for i in range(2, 42)
                )
            )
        )
    )
