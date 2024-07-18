from abc import abstractmethod
from typing import Any, Generic, TypeVar

from eth_streams.context import Context
from eth_streams.types import Envelope, Sink

Ctx = TypeVar("Ctx", bound=Context)


class Transformer(Sink[Any], Generic[Ctx]):
    """
    The transformer is used to Transform the events to a format the Context can interpret.
    It is a stateless component.
    """

    context: Ctx

    async def _notify(self, envelope: Envelope[Any]):
        await self.on_next(self.context, envelope)

    @abstractmethod
    async def on_next(self, context: Ctx, envelope: Envelope[Any]): ...
