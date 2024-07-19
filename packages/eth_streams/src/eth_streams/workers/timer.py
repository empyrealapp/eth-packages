import asyncio
import time
from abc import abstractmethod
from collections.abc import AsyncIterator
from typing import Generic, TypeVar

from eth_streams.types import Source, StreamEvents, Topic
from pydantic import Field, PrivateAttr

T = TypeVar("T")


class Timer(Source[T], Generic[T]):
    start_time: float = Field(default_factory=time.time)
    frequency: float
    _stopped: bool = PrivateAttr(default=False)

    def stop(self):
        self._stopped = True

    @abstractmethod
    async def generate_timer_value(self) -> T | StreamEvents:
        """Override this for alternative logic to generate your yielded value"""

    async def _run(self) -> AsyncIterator[tuple[Topic[T], T | StreamEvents]]:
        while True:
            if self._stopped:
                break
            value = await self.generate_timer_value()
            if value:
                yield (self.default_topic, value)
            await asyncio.sleep(self.frequency)


class IntervalTimer(Timer[int]):
    iteration: int = Field(0)
    max_count: float = float("inf")

    async def generate_timer_value(self) -> int | StreamEvents:
        self.iteration += 1
        if self.iteration >= self.max_count:
            self.stop()
            return StreamEvents.stopped
        return self.iteration
