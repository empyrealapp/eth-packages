def address_to_topic(address):
    return "0x{:064x}".format(int(address, 16))


def address_to_bytes32(address: str):
    return bytes.fromhex(address.ljust(66, "0")[2:])
