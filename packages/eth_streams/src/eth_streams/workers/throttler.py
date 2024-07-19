import asyncio
import itertools
from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from eth_streams.types import Envelope, StreamEvents, Topic, Vertex
from pydantic import ConfigDict, Field, PrivateAttr

from .batcher import Batch
from .timer import Timer

T = TypeVar("T")

count = itertools.count()


class Throttler(Timer[Batch[T]], Vertex[T, Batch[T]], Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    batch: Batch[T] = Field(default_factory=lambda: Batch())
    max_size: int | None = Field(None)
    lock: asyncio.Lock = Field(default_factory=asyncio.Lock)

    _count: int = PrivateAttr()

    @property
    def name(self):
        return f"throttler-{self._count}"

    def model_post_init(self, __context):
        self._count = next(count)
        super().model_post_init(__context)

    async def update_batch(self, item: T):
        async with self.lock:
            self.batch.append(item)

    async def reset_batch(self) -> Batch[T]:
        async with self.lock:
            batch = self.batch
            self.batch = Batch()
        return batch

    async def transform(
        self, envelope: Envelope[T]
    ) -> AsyncIterator[tuple[Topic[Batch[T]], Batch[T]]]:
        if not isinstance(envelope.message, StreamEvents):
            self.batch.append(envelope.message)

        if (self.max_size is not None) and (len(self.batch) >= self.max_size):
            batch = await self.reset_batch()
            yield (self.default_topic, batch)

    async def on_close(self):
        if len(self.batch) > 0:
            self.default_topic.publish(self.make_envelope(self.batch))
        self._stopped = True

    async def generate_timer_value(self) -> Batch[T]:
        return await self.reset_batch()
