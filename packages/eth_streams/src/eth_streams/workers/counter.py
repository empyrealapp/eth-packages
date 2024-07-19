import time
from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from eth_streams.types import Envelope, StreamEvents, Topic, Vertex
from pydantic import Field

T = TypeVar("T")


class Counter(Vertex[T, int], Generic[T]):
    __name__ = "counter"

    start_time: float = Field(default_factory=time.time)
    count: int = Field(default=0)
    display_frequency: int = Field(default=20)

    async def transform(
        self, envelope: Envelope[T]
    ) -> AsyncIterator[tuple[Topic[int], int]]:
        if isinstance(envelope.message, StreamEvents):
            return
        self.count += 1
        if self.count % self.display_frequency == 0:
            yield (self.default_topic, self.count)

    async def on_close(self):
        self.default_topic.publish(self.make_envelope(self.count))
