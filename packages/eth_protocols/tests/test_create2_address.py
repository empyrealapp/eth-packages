from eth_protocols.uniswap_v2.pair import get_uniswap_v2_pair_addr
from eth_rpc.utils import to_checksum
from eth_typing import HexAddress, HexStr


def test_create2_pair_addr() -> None:
    ppeas = HexAddress(HexStr("0x027ce48b9b346728557e8d420fe936a72bf9b1c7"))
    pohm = HexAddress("0x88e08adb69f2618adf1a3ff6cc43c671612d1ca4")
    pair_address = get_uniswap_v2_pair_addr(ppeas, pohm)
    assert pair_address == to_checksum(
        HexAddress("0x80e9c48ec41af7a0ed6cf4f3ac979f3538021608")
    )
