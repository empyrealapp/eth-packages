import asyncio
from collections.abc import AsyncIterator

from eth_streams.types import Source, StreamEvents, Topic
from pydantic import Field


class Range(Source[int]):
    start_number: int = Field(default=0)
    end_number: int
    skip: int = Field(default=1)
    delay: float = Field(default=0, ge=0)

    async def _run(self) -> AsyncIterator[tuple[Topic, int | StreamEvents]]:
        for idx in range(self.start_number, self.end_number, self.skip):
            yield (self.default_topic, idx)
            await asyncio.sleep(self.delay)
