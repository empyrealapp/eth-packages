from collections.abc import AsyncIterator
from typing import TypeVar

from eth_streams.types import Envelope, Topic, Vertex
from pydantic import PrivateAttr

T = TypeVar("T")


class Skipper(Vertex[T, T]):
    n: int
    _count: int = PrivateAttr(default=0)

    async def transform(
        self, envelope: Envelope[T]
    ) -> AsyncIterator[tuple[Topic[T], T]]:
        """Allows for delivery 1 in every `n` items"""
        if self._count % self.n == 0:
            yield (self.default_topic, envelope.message)
        self._count += 1
