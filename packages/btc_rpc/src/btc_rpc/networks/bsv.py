from eth_typing import HexStr

from btc_rpc.types import Network


class BitcoinSV(Network):
    id: HexStr = HexStr("0xD9B4BEF9")
    name: str = "Bitcoin Satoshi Vision"
    symbol: str = "BSV"
    http: str
