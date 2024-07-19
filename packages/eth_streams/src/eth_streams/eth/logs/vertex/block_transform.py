from collections.abc import AsyncIterator

from eth_rpc import Block, Log, get_current_network
from eth_rpc.types import Network
from eth_streams.types import Envelope, Topic, Vertex
from eth_streams.workers import Batch
from pydantic import Field


class BlockNumberToLogsVertex(Vertex[int | Block, Batch[Log]]):
    """This is useful for lagging the current block"""

    network: Network = Field(default_factory=get_current_network)

    async def transform(
        self, envelope: Envelope[int | Block]
    ) -> AsyncIterator[tuple[Topic[Batch[Log]], Batch[Log]]]:
        """Transform a Block Number to the logs for that block"""
        message: int | Block = envelope.message
        if isinstance(message, Block):
            logs = await Log[self.network].load_by_number(message.number)
        elif isinstance(message, int):
            logs = await Log[self.network].load_by_number(message)
        yield (self.default_topic, Batch(data=logs))
