from abc import abstractmethod
from typing import Generic, TypeVar

from .callback import Callback

T = TypeVar("T")


class Monitor(Callback, Generic[T]):
    @abstractmethod
    async def poll(self) -> T:
        """Pull in any data needed by the monitor"""

    @abstractmethod
    async def evaluate(self, value: T) -> bool:
        """Evaluate polled value to see if a condition is met"""

    @abstractmethod
    async def handle(self, value: T) -> None:
        """What to do if condition is met"""

    async def _on_epoch_start(self) -> None:
        value: T = await self.poll()
        is_alarm = await self.evaluate(value)
        if is_alarm:
            await self.handle(value)

    async def _on_epoch_end(self):
        """Any logic related to the execution can be handled here"""
