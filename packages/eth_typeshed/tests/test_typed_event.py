from eth_rpc.event import Event
from eth_rpc.types import primitives
from eth_typeshed.uniswap_v2 import V2SwapEventType
from eth_typing import HexStr


def test_process_event() -> None:
    swap = Event[V2SwapEventType](name="Swap")
    assert (
        swap.get_topic0
        == "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
    )

    response = swap.process(
        topics=[
            HexStr(
                "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
            ),
            HexStr(
                "0x0000000000000000000000003328f7f4a1d1c57c35df56bbf0c9dcafca309c49"
            ),
            HexStr(
                "0x0000000000000000000000003e33de444802886a8041717f57e0f42a89b118d2"
            ),
        ],
        data=HexStr(
            "0x0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000296d1d8eba5c2dd9000000000000000000000000000000000000000000000062877d7caf78e5e6c90000000000000000000000000000000000000000000000000000000000000000"  # noqa: E501
        ),
    )
    assert response == V2SwapEventType(
        sender=primitives.address("0x3328f7f4a1d1c57c35df56bbf0c9dcafca309c49"),
        amount0_in=primitives.uint256(0),
        amount1_in=primitives.uint256(2985074626865671641),
        amount0_out=primitives.uint256(1817544015883834615497),
        amount1_out=primitives.uint256(0),
        to=primitives.address("0x3e33de444802886a8041717f57e0f42a89b118d2"),
    )
