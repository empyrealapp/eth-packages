from typing import Generic, TypeVar

from eth_rpc import Event, EventData, EventSubscriber
from eth_rpc.types import BLOCK_STRINGS, Network
from eth_streams.types import Source
from eth_streams.utils import get_implicit
from eth_streams.workers import Throttler
from eth_typing import HexAddress
from pydantic import BaseModel, ConfigDict, Field, computed_field

from ..contract_event_vertex import ContractEventSink

T = TypeVar("T", bound=BaseModel)


class EventBackfillSource(Source[EventData[T]], Generic[T]):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    events: list[Event] = Field(default_factory=list)
    subscriber: EventSubscriber = Field(default_factory=EventSubscriber)
    addresses: list[HexAddress] = Field(default_factory=list)

    start_block: int | BLOCK_STRINGS = Field(
        default_factory=lambda: get_implicit("start_block", "earliest")
    )
    end_block: int | None = Field(default_factory=lambda: get_implicit("end_block"))

    @computed_field  # type: ignore
    @property
    def name(self) -> str:
        return ",".join(e.name for e in self.events)

    def model_post_init(self, __context):
        self.subscriber.add_receiver(self, self.events)
        return super().model_post_init(__context)

    @classmethod
    def create(
        cls,
        *,
        with_throttler: bool = True,
        with_db_sink: bool = True,
        batch_size: int = 10,
        network: type[Network] | None = None,
        **kwargs,
    ):
        log_source = cls(**kwargs)
        if with_throttler:
            throttler: Throttler[EventData[T]] = Throttler[EventData[T]](
                max_size=batch_size, frequency=3.0
            )
            log_source = log_source >> throttler
        if with_db_sink:
            sink: ContractEventSink
            if network:
                sink = ContractEventSink(network=network)
            else:
                sink = ContractEventSink()
            log_source >> sink  # type: ignore
        return log_source

    async def put(self, event: EventData[T]) -> None:
        self.default_topic.publish(self.make_envelope(event))

    async def _run(self):
        if self.end_block is None:
            # this will never terminate
            await self.subscriber.backfill_and_listen(
                self.start_block, addresses=self.addresses
            )

        async for event in self.subscriber(
            start_block=self.start_block,
            end_block=self.end_block,
            addresses=self.addresses,
        ):
            yield self.default_topic, event

        yield self.stop()
