from collections.abc import AsyncIterator
from typing import cast

from eth_rpc import Block, get_current_network
from eth_rpc.models import Block as BlockModel
from eth_rpc.types import BLOCK_STRINGS, Network
from eth_streams.types import Source, Topic
from eth_streams.utils import ExpiringDict, get_implicit
from pydantic import BaseModel, ConfigDict, Field


class ReorgError(BaseModel):
    block_number: int


class BlockSource(Source[ReorgError | BlockModel], BaseModel):
    __name__ = "block-source"

    model_config = ConfigDict(arbitrary_types_allowed=True)
    reorg_topic: Topic[ReorgError]

    network: Network = Field(default_factory=get_current_network)
    start_block: int | BLOCK_STRINGS = Field(
        default_factory=lambda: get_implicit("start_block", "earliest")
    )
    reorg_distance: int = Field(5)
    history: ExpiringDict[int, BlockModel] = Field(
        default_factory=lambda: ExpiringDict(100, 12 * 100)
    )
    restart_point: int | None = Field(None)

    @property
    def block_topic(self):
        return self.default_topic

    def __class_getitem__(self, network: Network):  # type: ignore
        self.network = network

    async def _run(self) -> AsyncIterator[tuple[Topic, ReorgError | BlockModel]]:
        if self.start_block == "latest":
            latest = await Block[self.network].get_number()
            prev_block = await Block[self.network].load_by_number(
                block_number=latest - 1
            )
        else:
            if self.start_block in BLOCK_STRINGS.__dict__["__args__"]:
                prev_block = await Block[self.network].load_by_number(
                    block_number=self.start_block
                )
            else:
                block_number = cast(int, self.start_block)
                prev_block = await Block[self.network].load_by_number(
                    block_number=block_number - 1
                )
        self.history[prev_block.number] = prev_block
        current_block: int = prev_block.number + 1

        while True:
            async for block in Block[self.network].subscribe_from(
                start_block=current_block
            ):
                self.history[block.number] = block
                if self.history[block.number - 1].hash != block.parent_hash:
                    # go back the reorg_distance to reindex those blocks
                    current_block = block.number - self.reorg_distance
                    yield (self.reorg_topic, ReorgError(block_number=current_block))
                    break
                yield (self.block_topic, block)
