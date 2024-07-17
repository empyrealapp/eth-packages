from collections.abc import AsyncIterator

from eth_rpc.models import EventData
from eth_rpc.utils import acombine
from pydantic import BaseModel

from ..event import Event


class EventCombinator(BaseModel):
    events: list[Event]

    async def subscribe(self) -> AsyncIterator[EventData]:
        async for event in acombine(*[event.subscribe() for event in self.events]):
            yield event

    async def backfill(
        self, start_block: int, end_block: int, step_size: int | None = None
    ) -> AsyncIterator[EventData]:
        for event in acombine(
            *[
                event.backfill(
                    start_block=start_block,
                    end_block=end_block,
                    step_size=step_size,
                )
                for event in self.events
            ]
        ):
            yield event
