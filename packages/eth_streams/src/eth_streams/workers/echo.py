import itertools
from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from eth_streams.types import Envelope, StreamEvents, Topic, Vertex
from pydantic import Field

T = TypeVar("T")

count = itertools.count()


class Echo(Vertex[T, T], Generic[T]):
    __name__ = "ECHO"

    ignore_empty: bool = Field(default=True)
    index: int = Field(default_factory=lambda: next(count))

    @property
    def name(self):
        return f"ECHO-{self.index}"

    def extra(self, envelope: Envelope[T]) -> None:
        return None

    async def transform(
        self, envelope: Envelope[T]
    ) -> AsyncIterator[tuple[Topic[T], T]]:
        if isinstance(envelope.message, StreamEvents):
            return
        if envelope.message or not self.ignore_empty:
            print("MSG:", envelope.message)
        self.extra(envelope)
        yield (self.default_topic, envelope.message)
