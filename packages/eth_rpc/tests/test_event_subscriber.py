import os
from typing import Annotated

import pytest
from eth_rpc import Event, EventData, EventSubscriber, set_alchemy_key
from eth_rpc.types import Indexed, primitives
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel
from typing_extensions import assert_type


class TransferEventType(BaseModel):
    sender: Annotated[primitives.address, Indexed]
    recipient: Annotated[primitives.address, Indexed]
    amount: primitives.uint256


class ApprovalEventType(BaseModel):
    owner: Annotated[primitives.address, Indexed]
    spender: Annotated[primitives.address, Indexed]
    value: primitives.uint256


TransferEvent = Event[TransferEventType](name="Transfer")
ApprovalEvent = Event[ApprovalEventType](name="Approval")


subscriber = EventSubscriber[TransferEventType | ApprovalEventType](
    step_size=1000,
    events=[TransferEvent, ApprovalEvent],
)


@pytest.mark.asyncio(scope="session")
@pytest.mark.contract
async def test_event_subscriber_types() -> None:
    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    async for event in subscriber(
        start_block=20_600_000,
        end_block=20_601_000,
        addresses=[HexAddress(HexStr("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"))],
    ):
        assert_type(event, EventData[TransferEventType | ApprovalEventType])
        match event.event:
            case TransferEventType():
                # print("Transfer", event.event)
                pass
            case ApprovalEventType():
                # print("Approval", event.event)
                pass
