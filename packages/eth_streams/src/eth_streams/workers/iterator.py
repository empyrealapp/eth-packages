from collections.abc import AsyncIterator
from typing import TypeVar

from eth_streams.types import Envelope, Topic, Vertex

T = TypeVar("T")


class Iterator(Vertex[list[T], T]):
    async def transform(
        self, envelope: Envelope[list[T]]
    ) -> AsyncIterator[tuple[Topic[T], T]]:
        """Transform an envelope, yielding iterables"""
        for item in envelope.message:
            yield (self.default_topic, item)
