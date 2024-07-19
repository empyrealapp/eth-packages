from collections.abc import AsyncIterator

from eth_rpc import EventData
from eth_rpc.constants import ADDRESS_ZERO
from eth_rpc.utils import address_to_topic
from eth_typeshed.erc20 import TransferEvent, TransferEventType
from eth_typing import HexAddress
from pydantic import BaseModel


class TransferEvents(BaseModel):
    address: HexAddress | None = None

    def set_address(self, address: HexAddress):
        self.address = address

    def mints(self) -> AsyncIterator[EventData[TransferEventType]]:
        return self.transfers(
            sender=ADDRESS_ZERO,
        )

    def burns(self) -> AsyncIterator[EventData[TransferEventType]]:
        return self.transfers(
            recipient=ADDRESS_ZERO,
        )

    def transfers(
        self,
        sender: HexAddress | None = None,
        recipient: HexAddress | None = None,
        step_size: int | None = None,
    ) -> AsyncIterator[EventData[TransferEventType]]:
        return TransferEvent.set_filter(
            addresses=[self.address],
            topic1=address_to_topic(sender) if sender else None,
            topic2=address_to_topic(recipient) if recipient else None,
        ).backfill(step_size=step_size)
