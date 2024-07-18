import asyncio
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from eth_streams.coordinator import Coordinator
from pydantic import BaseModel, Field

from .transformer import Transformer

Trn = TypeVar("Trn", bound=Transformer)


class Stage(ABC, BaseModel, Generic[Trn]):
    poll_frequency: int = Field(default=1)

    @property
    def name(self):
        return self.__class__.__name__

    async def setup(self, transformer: Trn): ...

    @abstractmethod
    async def actions(
        self,
        transformer: Trn,
    ): ...

    async def teardown(self, transformer: Trn): ...

    async def run(self, transformer: Trn):
        await self.setup(transformer)
        with Coordinator() as coordinator:
            await self.actions(transformer)
        await coordinator.run()

        while not coordinator.completed:
            await asyncio.sleep(self.poll_frequency)
        await self.teardown(transformer)
