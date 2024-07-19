from typing import Generic, Type, TypeVar

from eth_streams.types import Sink
from eth_streams.types.envelope import Envelope
from pydantic import ConfigDict
from tortoise import Model

T = TypeVar("T", bound=Model)


class DBPublisher(Sink[list[T]], Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    model: Type[Model]

    async def notify(self, envelope: Envelope[list]):
        await self.model.bulk_create(
            envelope.message,
            ignore_conflicts=True,
        )
