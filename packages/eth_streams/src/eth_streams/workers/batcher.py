from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from eth_streams.types import Envelope, StreamEvents, Topic, Vertex
from pydantic import BaseModel, Field, PrivateAttr

T = TypeVar("T")


class Batch(BaseModel, Generic[T]):
    data: list[T] = Field(default_factory=list)

    def __str__(self):
        return f"<Batch size={len(self.data)}>"

    def append(self, item: T):
        self.data.append(item)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for item in self.data:
            yield item

    __repr__ = __str__


class Batcher(Vertex[T, Batch[T]]):
    # TODO: 100 events or 10 seconds, whichever comes first
    batch: list[T] = Field(default_factory=list)
    batch_size: int
    # max_wait_time: float
    count: int = 0
    _name: str = PrivateAttr(f"batcher-{count}")

    def model_post_init(self, __context):
        self.count += 1

    async def transform(
        self, envelope: Envelope[T]
    ) -> AsyncIterator[tuple[Topic[Batch[T]], Batch[T]]]:
        if not isinstance(envelope.message, StreamEvents):
            self.batch.append(envelope.message)

        if (
            len(self.batch) >= self.batch_size
            or envelope.message == StreamEvents.stopped
        ):
            response = (self.default_topic, Batch[T](data=self.batch))
            self.batch = []
            yield response
