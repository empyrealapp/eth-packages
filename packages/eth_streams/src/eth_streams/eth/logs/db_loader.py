import asyncio
import sqlite3
from abc import abstractmethod
from typing import ClassVar, Generic, TypeVar

from eth_rpc import EventData, get_current_network
from eth_rpc.types import Network
from eth_streams.logger import logger
from eth_streams.types import Envelope, Sink
from eth_streams.workers import Batch
from pydantic import Field
from tortoise import Model

T = TypeVar("T", bound=EventData)
U = TypeVar("U", bound=Model)


class DBLoader(Sink[EventData[T] | list[EventData[T]]], Generic[T, U]):
    network: Network = Field(default_factory=get_current_network)
    lock: ClassVar[asyncio.Lock] = asyncio.Lock()
    model: type[U]

    @abstractmethod
    def _convert(self, event_data: EventData[T]) -> U:
        """Convert the input type to the model"""

    async def _notify(self, envelope: Envelope[EventData[T] | list[EventData[T]]]):
        """Converts a log to a contract event and writes it to the database"""
        events = envelope.message
        # TODO: add batching logic
        batch = []
        if isinstance(events, Batch):
            for event_data in events:
                batch.append(self._convert(event_data))
        elif isinstance(events, EventData):
            batch.append(self._convert(events))
        if batch:
            logger.debug(f"WRITING BATCH: {len(batch)}")
            try:
                await self.model.bulk_create(
                    batch,
                    ignore_conflicts=True,
                )
            except (ValueError, sqlite3.ProgrammingError) as exc:
                raise exc
