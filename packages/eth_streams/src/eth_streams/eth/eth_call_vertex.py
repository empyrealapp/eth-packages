from abc import abstractmethod
from collections.abc import AsyncIterator
from typing import Any, Generic, TypeVar, final

from eth_rpc import ContractFunc
from eth_rpc.contract.function import T as ArgType
from eth_streams.types import Envelope, Topic, Vertex

ResponseType = TypeVar("ResponseType")
U = TypeVar("U")


class EthCallVertex(Vertex[Any, U], Generic[ArgType, ResponseType, U]):
    func: ContractFunc[ArgType, ResponseType]
    args: ArgType

    @final
    async def transform(
        self, envelope: Envelope[Any]
    ) -> AsyncIterator[tuple[Topic[U], U]]:
        result = await self.func(self.args)
        if await self.conditions(envelope, result):
            response = await self.modify(envelope, result)
            yield self.default_topic, response

    @abstractmethod
    async def conditions(self, envelope: Envelope[Any], result: ResponseType) -> bool:
        """Specify what condition needs to be met by the eth_call to alert the user"""

    @abstractmethod
    async def modify(self, envelope: Envelope[Any], result: ResponseType) -> U:
        """Specify what to return if the condition is met"""
