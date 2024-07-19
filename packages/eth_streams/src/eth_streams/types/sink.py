from abc import abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from pydantic import Field, computed_field

from ..types import StreamEvents
from .base import Base
from .envelope import Envelope

if TYPE_CHECKING:
    from .source import Source

T = TypeVar("T")


class Sink(Base, Generic[T]):
    source_count: int = Field(default=0)
    stopped: bool = Field(default=False)

    def model_post_init(self, __context):
        if self.coordinator:
            self.coordinator.add_sink(self)

    @computed_field  # type: ignore
    @property
    def name(self) -> str:
        return self.__class__.__name__

    async def notify(self, envelope: Envelope[T]):
        if isinstance(envelope.message, StreamEvents):
            if envelope.message == StreamEvents.stopped:
                self.source_count -= 1
        await self._notify(envelope)
        if self.source_count == 0:
            self.stopped = True

    @abstractmethod
    async def _notify(self, envelope: Envelope[T]): ...

    def __rrshift__(self, other: "Source[T] | list[Source[T]]"):
        from .source import Source

        if isinstance(other, list):
            for source in other:
                if not isinstance(source, Source):
                    raise ValueError(f"Not a source: {source.name}")
                source >> self
        else:
            if not isinstance(other, Source):
                raise ValueError(f"Not a source: {other.name}")
            other >> self
        return self
