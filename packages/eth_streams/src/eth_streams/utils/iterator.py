from collections.abc import AsyncIterator

from eth_rpc import Event
from eth_rpc.models import EventData, Log
from eth_rpc.networks import Networks
from eth_streams.models import ContractEvent


class EventIterator:
    _events: list[Event]

    @property
    def event_map(self) -> dict[str, Event]:
        return {event.get_topic0: event for event in self._events}

    async def ordered_events(
        self,
        from_block: int | None = None,
        pagination_size: int = 100,
        stage_id: str | None = None,
    ) -> AsyncIterator[EventData]:
        """
        It is possible for events to be pulled out of order if you are
        adding new events from the same time period while this is
        running.
        """
        pagination_full = True
        offset = 0
        while pagination_full:
            query = ContractEvent.all().order_by(
                "block_number", "transaction_index", "log_index"
            )

            if from_block:
                query = query.filter(block_number__gte=from_block)

            if stage_id:
                query = query.filter(stage_id=stage_id)

            ordered_events = await query.limit(pagination_size).offset(offset)

            pagination_full = len(ordered_events) == pagination_size
            for event in ordered_events:
                EventType: Event = self.event_map[event.topic0]
                yield EventData(
                    name=event.name,
                    log=Log(
                        transaction_hash=event.transaction_hash,
                        address=event.address,
                        block_hash=event.block_hash,
                        block_number=event.block_number,
                        data="",
                        log_index=event.log_index,
                        removed=False,
                        topics=[],
                        transaction_index=event.transaction_index,
                    ),
                    event=EventType.from_dict(event.event_data),
                    network=Networks.get(event.chain),
                )
            offset += pagination_size
