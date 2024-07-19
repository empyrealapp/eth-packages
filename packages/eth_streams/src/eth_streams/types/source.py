import asyncio
from abc import abstractmethod
from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from pydantic import Field, PrivateAttr

from ..types import StreamEvents
from .envelope import Envelope
from .sink import Sink
from .task import Task
from .topic import Topic

T = TypeVar("T")


class Source(Task, Generic[T]):
    _default_topic: Topic[T | StreamEvents] = PrivateAttr(
        default_factory=lambda: Topic(name="default")
    )
    wait_for_downstreams: bool = Field(default=True)

    @property
    def default_topic(self):
        return self._default_topic

    def make_envelope(self, message: T | StreamEvents):
        return Envelope(
            sender=self.name,
            message=message,
        )

    async def run(self) -> None:
        async for topic, event in self._run():
            tasks = topic.publish(self.make_envelope(event))
            if self.wait_for_downstreams:
                await asyncio.gather(*tasks)
            if event == StreamEvents.stopped:
                return

    def __rshift__(self, other: Sink[T] | list[Sink[T]]):
        if isinstance(other, list):
            for sink in other:
                self._default_topic.subscribe(sink)
        else:
            self._default_topic.subscribe(other)
        return other

    @abstractmethod
    def _run(self) -> AsyncIterator[tuple[Topic, T | StreamEvents]]:
        """Create an iterator that yields the source values"""

    def stop(self):
        return (self.default_topic, StreamEvents.stopped)
