import pytest
from eth_rpc import Event
from eth_rpc.networks import Arbitrum, Ethereum
from eth_rpc.types import primitives
from pydantic import BaseModel


class SampleArg(BaseModel):
    x: primitives.uint256
    y: primitives.string


SwapEvent = Event[SampleArg](name="Swap")


@pytest.mark.unit
def test_log_network():
    assert SwapEvent[Ethereum]._network == Ethereum
    assert SwapEvent[Arbitrum]._network == Arbitrum
