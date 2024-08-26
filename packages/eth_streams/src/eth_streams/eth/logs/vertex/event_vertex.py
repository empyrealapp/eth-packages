from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from eth_rpc import Event, EventData, get_current_network
from eth_rpc.models import Log
from eth_rpc.types import Network
from eth_streams.types import Envelope, Topic, Vertex
from eth_streams.workers import Batch
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, Field

from ..signals import AddAddress, RemoveAddress

U = TypeVar("U", bound=BaseModel)


class LogEventVertex(Vertex[Batch[Log] | Log | str, list[EventData[U]]], Generic[U]):
    network: Network = Field(default_factory=get_current_network)
    event: Event[U]

    def match_log(self, log: Log) -> bool:
        """
        Checks a log to see if it matches the desired filter
        """
        return self.event.match(log)

    def handle_log(self, log: Log) -> EventData[U] | None:
        """Converts a log event to the desired downstream type"""
        if self.match_log(log):
            return self.event.process_log(log)
        return None

    def handle_logs(self, envelope: Envelope[Batch[Log]]) -> list[EventData[U]]:
        """Converts a log event to the desired downstream type"""
        results = []
        for log in envelope.message.data:
            if parsed_log := self.handle_log(log):
                results.append(parsed_log)
        return results

    async def cleanup_backfill(self):
        """Any cleanup needed at the end of the backfill"""

    async def transform(
        self,
        envelope: Envelope[Batch[Log] | Log | str],
    ) -> AsyncIterator[tuple[Topic[list[EventData[U]]], list[EventData[U]]]]:
        """Transform an envelope, or return None to skip"""
        results = []
        if isinstance(envelope.message, Batch):
            results = self.handle_logs(envelope)  # type: ignore
        elif isinstance(envelope.message, AddAddress):
            self.event.add_address(HexAddress(HexStr(envelope.message)))
        elif isinstance(envelope.message, RemoveAddress):
            self.event.add_address(HexAddress(HexStr(envelope.message)))
        elif isinstance(envelope.message, Log):
            if result := self.handle_log(envelope.message):
                results.append(result)
        if results:
            yield (self.default_topic, results)
