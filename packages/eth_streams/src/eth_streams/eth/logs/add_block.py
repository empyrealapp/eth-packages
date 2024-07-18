from abc import abstractmethod
from collections.abc import AsyncIterator
from typing import ClassVar, Generic, TypeVar

from pydantic import BaseModel, Field

from eth_rpc import Block, Log
from eth_rpc.types import Network
from eth_streams.types import Envelope, Topic, Vertex

T = TypeVar("T")


class BlockWrap(BaseModel, Generic[T]):
    data: T
    block: Block


class AddBlockVertex(Vertex[Log, BlockWrap[T]]):
    """
    A singleton class, depending on whether `with_tx_data` is set to True or False.
    This wraps the transaction into a BaseModel with the Block data.
    """

    __instances: ClassVar[dict[bool, "AddBlockVertex"]] = {}

    blocks: dict[tuple[int, Network], Block] = Field(default_factory=dict)
    with_tx_data: bool = Field(default=True)

    def __new__(cls, with_tx_data=True, **kwargs):
        if cls.__instances.get(with_tx_data) is None:
            cls.__instances[with_tx_data] = super().__new__(cls)
        return cls.__instances[with_tx_data]

    def __init__(self, **kwargs):
        if not self.__dict__:
            super().__init__(**kwargs)

    @abstractmethod
    def get_block_number(self, envelope: Envelope[T]) -> tuple[Block, Network]: ...

    async def transform(self, envelope: Envelope[T]) -> AsyncIterator[tuple[Topic[BlockWrap[T]], BlockWrap[T]]]:
        key = self.get_block_number(envelope)
        block_number, network = key

        if key not in self.blocks:
            self.blocks[key] = await Block[network].load_by_number(block_number)

        yield (
            self.default_topic,
            BlockWrap(
                data=envelope.message,
                block=self.blocks[key],
            ),
        )
