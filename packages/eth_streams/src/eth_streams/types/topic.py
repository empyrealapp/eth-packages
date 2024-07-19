import asyncio
from collections.abc import Callable
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from ..types import StreamEvents
from .envelope import Envelope
from .sink import Sink

T = TypeVar("T")


class Topic(BaseModel, Generic[T]):
    """
    A topic allows users to publish and subscribe
    """

    # this allows duplicates to be added
    subscribers: list[Sink] = Field(default_factory=list)
    name: str

    def publish(self, envelope: Envelope[T | StreamEvents]) -> list[asyncio.Task]:
        tasks: list[asyncio.Task] = []
        for subscriber in self.subscribers:
            tasks.append(asyncio.create_task(subscriber.notify(envelope)))
        return tasks

    def subscribe(self, sink: Sink):
        self.subscribers.append(sink)
        sink.source_count += 1

    def __rrshift__(self, envelope: Envelope[T | StreamEvents]) -> list[asyncio.Task]:
        return self.publish(envelope)

    def __rshift__(self, other: Sink | list[Sink]):
        if isinstance(other, list):
            for row in other:
                self.subscribers.append(row)
        else:
            self.subscribers.append(other)
        return other


class FilterTopic(Topic[T], Generic[T]):
    """
    A topic that allows filtering which users are sent each message based on an arbitrary function
    """

    sinks: dict[str, tuple[Sink, Callable[[Envelope[T | StreamEvents]], bool]]] = Field(
        default_factory=dict
    )
    name: str

    def publish(self, envelope: Envelope[T | StreamEvents]) -> list[asyncio.Task]:
        tasks: list[asyncio.Task] = []
        for _, (subscriber, filter) in self.sinks.items():
            if filter(envelope):
                tasks.append(asyncio.create_task(subscriber.notify(envelope)))
        return tasks

    def subscribe(self, sink: Sink):
        self.sinks[sink.name] = (sink, lambda x: True)

    def subscribe_with_filter(
        self, *, sink: Sink, filter: Callable[[Envelope[T | StreamEvents]], bool]
    ):
        self.sinks[sink.name] = (sink, filter)

    def __rrshift__(self, envelope: Envelope[T | StreamEvents]) -> list[asyncio.Task]:
        return self.publish(envelope)
