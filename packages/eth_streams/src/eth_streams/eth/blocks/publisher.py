from typing import Generic, TypeVar

from eth_rpc.models import Block
from eth_streams.models import Block as BlockModel
from eth_streams.types import Envelope, Sink

T = TypeVar("T", bound=Block)


class BlockSink(Sink[list[Block]], Generic[T]):
    async def notify(self, envelope: Envelope[list[Block]]):
        """Converts a log to a contract event and writes it to the database"""
        events = envelope.message
        # TODO: add batching logic
        batch = []
        for block in events:
            contract_event = BlockModel(
                number=block.number,
                timestamp=block.timestamp,
                # TODO: is block._network always set?
                chain_id=block._network and block._network.chain_id or -1,
                hash=block.hash,
                parent_block_hash=block.parent_hash,
                hot_block=False,
            )
            batch.append(contract_event)
        if batch:
            await BlockModel.bulk_create(
                batch,
                ignore_conflicts=True,
            )
