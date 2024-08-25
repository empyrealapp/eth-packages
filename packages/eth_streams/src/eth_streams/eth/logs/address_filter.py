from collections.abc import AsyncIterator
from typing import cast

from eth_rpc.models import Log
from eth_streams.types import Address, Batch, Envelope, Topic, Vertex
from eth_typing import HexAddress, HexStr
from pydantic import Field


class AddressFilterVertex(Vertex[Log | Batch[Log] | Address, Log | Batch[Log]]):
    addresses: set[HexAddress] = Field(default_factory=set)

    async def transform(
        self, envelope: Envelope[Log | Batch[Log] | Address]
    ) -> AsyncIterator[tuple[Topic[Log | Batch[Log]], Log | Batch[Log]]]:
        if isinstance(envelope.message, Address):
            self.addresses.add(HexAddress(HexStr(envelope.message)))
        elif isinstance(envelope.message, Log):
            if envelope.message.address in self.addresses:
                yield (self.default_topic, envelope.message)
        elif isinstance(envelope.message, Batch):
            batch = Batch[Log]()
            for item in envelope.message:
                item = cast(Log, item)
                if item.address in self.addresses:
                    batch.append(item)
            if len(batch) > 0:
                yield (self.default_topic, batch)
