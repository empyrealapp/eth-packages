import asyncio
from typing import ClassVar, Generic, Optional, TypeVar

from eth_rpc import EventData
from eth_streams.models import ContractEvent

from .db_loader import DBLoader

T = TypeVar("T", bound=EventData)


class ContractEventSink(DBLoader[T, ContractEvent], Generic[T]):
    __instance: ClassVar[Optional["ContractEventSink"]] = None

    lock: ClassVar[asyncio.Lock] = asyncio.Lock()
    model: type[ContractEvent] = ContractEvent

    def __new__(cls, **kwargs):
        # this allows us to create a singleton
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, **kwargs):
        if not self.__dict__:
            super().__init__(**kwargs)

    def _convert(self, event_data: EventData[T]) -> ContractEvent:
        return ContractEvent(
            chain=event_data.network.chain_id,
            address=event_data.log.address,
            block_number=event_data.log.block_number,
            block_hash=event_data.log.block_hash,
            transaction_index=event_data.log.transaction_index,
            transaction_hash=event_data.log.transaction_hash,
            log_index=event_data.log.log_index,
            name=event_data.name,
            topic0=event_data.log.topics[0] if len(event_data.log.topics) > 0 else "",
            event_type=event_data.log.__class__.__name__,
            event_data=event_data.event.model_dump(),
            confirmed=True,
        )
