from eth_typing import HexStr

from btc_rpc.types import Network


class Bitcoin(Network):
    id: HexStr = HexStr("0xD9B4BEF9")
    name: str = "Bitcoin"
    symbol: str = "BTC"
    http: str
