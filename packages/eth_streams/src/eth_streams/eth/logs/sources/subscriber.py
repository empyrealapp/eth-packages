from collections.abc import AsyncIterator

from eth_rpc import Block, get_current_network
from eth_rpc.models import Log
from eth_rpc.types import BLOCK_STRINGS, Network
from eth_streams.types import Envelope, Sink, Source, Topic
from eth_streams.utils import get_implicit
from eth_streams.workers import Batcher
from pydantic import BaseModel, Field

from ...blocks.source import ReorgError


class LogSubscriber(Source[Log], Sink[ReorgError], BaseModel):
    __name__ = "log-source"

    network: Network = Field(default_factory=get_current_network)
    start_block: int | BLOCK_STRINGS = Field(
        default_factory=lambda: get_implicit("start_block", "earliest")
    )
    reorg_triggered: bool = Field(False)
    reorg_block: int | None = Field(None)

    @classmethod
    def create(
        cls,
        *,
        with_batcher: bool = True,
        batch_size: int = 100,
        **kwargs,
    ):
        if with_batcher:
            batcher: Batcher[Log] = Batcher(batch_size=batch_size)
            log_source = cls(
                **kwargs,
            )
            return log_source >> batcher
        return cls(**kwargs)

    def __class_getitem__(cls, network: Network):  # type: ignore
        cls.network = network
        return cls

    async def _notify(self, envelope: Envelope[ReorgError]):
        block_number = envelope.message.block_number
        self.trigger_reorg(block_number)

    def trigger_reorg(self, reorg_block: int):
        self.reorg_triggered = True
        self.reorg_block = reorg_block

    async def _get_current_block(self) -> int:
        if self.start_block in BLOCK_STRINGS.__dict__["__args__"]:
            latest = (await Block[self.network].load_by_number(self.start_block)).number
        elif isinstance(self.start_block, int):
            latest = self.start_block
        else:
            latest = self.start_block
        return latest

    async def _run(self) -> AsyncIterator[tuple[Topic, Log]]:
        current_block: int = await self._get_current_block()

        while True:
            async for log in Log[self.network].subscribe_from(start_block=current_block):  # type: ignore[misc]
                if self.reorg_triggered:
                    assert self.reorg_block is not None
                    current_block = min(self.reorg_block, current_block)

                    self.reorg_triggered = False
                    self.reorg_block = None
                    break
                if log.block_number != current_block:
                    current_block = log.block_number
                yield (self._default_topic, log)
