from pydantic import BaseModel

from eth_rpc.types import HexInteger, HexInt


def test_hex_int() -> None:
    class MyNum(BaseModel):
        x: HexInt

    assert MyNum(x="0x7") == MyNum(x=7)
    my_num = MyNum(x=30)
    assert my_num.model_dump() == {"x": 30}


def test_hex_integer() -> None:
    class MyNum(BaseModel):
        x: HexInteger

    assert MyNum(x="0x7") == MyNum(x=7)
    my_num = MyNum(x=30)
    assert my_num.model_dump() == {"x": "0x1e"}
