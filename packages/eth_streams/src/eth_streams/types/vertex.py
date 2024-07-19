from abc import abstractmethod
from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from pydantic import ConfigDict

from ..types import StreamEvents
from .envelope import Envelope
from .sink import Sink
from .source import Source
from .topic import Topic

T = TypeVar("T")
U = TypeVar("U")


class Vertex(Sink[T], Source[U], Generic[T, U]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    async def _run(self) -> AsyncIterator[tuple[Topic[U], U | StreamEvents]]:
        """Vertex have no requirements by default"""
        # empty yield needed to ensure this is a generator
        if False:
            yield

    async def _notify(self, envelope: Envelope[T]):
        """transforms an envelope, and optionally publishes"""
        if isinstance(envelope.message, StreamEvents):
            if envelope.message == StreamEvents.stopped:
                if self.source_count == 0:
                    await self.on_close()
                    self.default_topic.publish(self.make_envelope(StreamEvents.stopped))
                    self.stopped = True
                    return
        else:
            async for response in self.transform(envelope):
                topic, transformed_message = response
                topic.publish(self.make_envelope(transformed_message))

    @abstractmethod
    def transform(self, envelope: Envelope[T]) -> AsyncIterator[tuple[Topic[U], U]]:
        """Transform an envelope, or return None to skip"""

    async def on_close(self):
        """Any actions to be taken when the stream is closed"""
