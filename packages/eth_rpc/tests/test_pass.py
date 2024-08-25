import pytest
from eth_rpc.types.basic import HexInt, HexInteger
from pydantic import BaseModel


@pytest.mark.unit
def test_hex_int() -> None:
    class MyNum(BaseModel):
        x: HexInt

    assert MyNum(x="0x7") == MyNum(x=7)
    my_num = MyNum(x=30)
    assert my_num.model_dump() == {"x": 30}


@pytest.mark.unit
def test_hex_integer() -> None:
    class MyNum(BaseModel):
        x: HexInteger

    assert MyNum(x="0x7") == MyNum(x=7)
    my_num = MyNum(x=30)
    assert my_num.model_dump() == {"x": "0x1e"}
