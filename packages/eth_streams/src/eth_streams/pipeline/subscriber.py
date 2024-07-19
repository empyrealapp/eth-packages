from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from eth_streams.coordinator import Coordinator
from pydantic import BaseModel

from ..context import Context
from .transformer import Transformer

Ctx = TypeVar("Ctx", bound=Context)


class Subscriber(ABC, BaseModel, Generic[Ctx]):
    @property
    def name(self):
        return self.__class__.__name__

    async def setup(self, context: Ctx):
        pass

    @abstractmethod
    async def actions(
        self,
        transformer: Transformer[Ctx],
    ): ...

    async def teardown(self): ...

    async def run(self, transformer: Transformer):
        """This should run forever"""
        await self.setup(transformer.context)
        with Coordinator() as coordinator:
            await self.actions(transformer)
        await coordinator.run()
