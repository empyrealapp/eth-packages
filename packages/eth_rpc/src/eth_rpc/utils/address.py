def address_to_topic(address):
    return "0x{:064x}".format(int(address, 16))
