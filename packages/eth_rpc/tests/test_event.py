import os
from typing import Annotated

import pytest
from eth_rpc import Event, set_alchemy_key
from eth_rpc.networks import Arbitrum, Ethereum
from eth_rpc.types import Indexed, primitives
from pydantic import BaseModel


class TransferEventType(BaseModel):
    sender: Annotated[primitives.address, Indexed]
    recipient: Annotated[primitives.address, Indexed]
    amount: primitives.uint256


TransferEvent = Event[TransferEventType](name="Transfer")


@pytest.mark.unit
@pytest.mark.event
def test_event_network():
    assert TransferEvent[Ethereum]._network == Ethereum
    assert TransferEvent[Arbitrum]._network == Arbitrum
    swap_topic = TransferEvent.get_topic0
    assert (
        swap_topic
        == "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
    )

    eth_event = TransferEvent[Ethereum]
    assert eth_event._network == Ethereum
    arb_event = TransferEvent[Arbitrum]
    assert arb_event._network == Arbitrum

    # ensure previous instance isn't changed
    assert eth_event._network == Ethereum


@pytest.mark.asyncio(scope="session")
@pytest.mark.event
async def test_event_lookup():
    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    eth_ = TransferEvent[Ethereum]
    logs = await eth_._get_logs(10_000_000, 10_000_001)
    assert len(logs) == 121
