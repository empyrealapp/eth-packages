from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from eth_streams.types import Envelope, Topic, Vertex
from pydantic import BaseModel, computed_field

T = TypeVar("T")
U = TypeVar("U")


class Combinator(Vertex[T, U], Generic[T, U]):
    vertices: list[Vertex]

    @computed_field  # type: ignore
    @property
    def name(self) -> str:
        return "&".join(vertex.name for vertex in self.vertices)

    def __init__(self, *args):
        BaseModel.__init__(self, vertices=args)

    async def transform(
        self, envelope: Envelope[T]
    ) -> AsyncIterator[tuple[Topic[U], U]]:
        """Transform an envelope, or return None to skip"""
        for vertex in self.vertices:
            async for result in vertex.transform(envelope):
                _, msg = result
                yield (self.default_topic, msg)
