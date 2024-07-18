import asyncio
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel

from .envelope import Envelope

if TYPE_CHECKING:
    from ..coordinator import Coordinator


T = TypeVar("T")


class Callback(BaseModel, ABC):
    name: str
    coordinator: "Coordinator"
    timeout: int | None

    def __init__(self, *args, timeout: int | None = None, **kwargs):
        self.timeout = timeout

    async def notify(self, envelope: Envelope):
        raise ValueError("Callback does not allow notifications")

    @abstractmethod
    async def _on_epoch_end(self): ...

    @abstractmethod
    async def _on_epoch_start(self): ...

    async def shutdown(self, semaphore: asyncio.Semaphore):
        """Any logic for the end of each epoch"""

    async def on_epoch_start(self, semaphore: asyncio.Semaphore):
        async with semaphore:
            if self.timeout:
                await asyncio.wait_for(self._on_epoch_start(), timeout=self.timeout)
            await self._on_epoch_start()

    async def on_epoch_end(self, semaphore: asyncio.Semaphore):
        async with semaphore:
            await self._on_epoch_end()
