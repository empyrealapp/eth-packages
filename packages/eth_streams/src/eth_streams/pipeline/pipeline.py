from typing import Generic, Optional, Type, TypeVar

from eth_rpc.block import Block
from eth_rpc.types import BLOCK_STRINGS
from eth_streams.context import Context
from eth_streams.coordinator import CoordinatorContext
from eth_streams.logger import logger
from eth_streams.models import Checkpoint
from eth_streams.utils import init_db
from pydantic import BaseModel, Field
from tortoise import Tortoise

from .stage import Stage
from .subscriber import Subscriber
from .transformer import Transformer

Ctx = TypeVar("Ctx", bound=Context)


class Pipeline(BaseModel, Generic[Ctx]):
    pipeline_id: int | str
    context: Ctx
    stages: list[Stage]
    subscriber: Type[Subscriber]
    transformer: Type[Transformer]  # Transformer[Ctx] errors
    # sqlite doesn't allow parallel access
    in_parallel: bool = Field(default=False)

    db_url: str = Field(default="sqlite://db.sqlite3")
    checkpoint_block: Optional[int] = None

    async def setup(self):
        await init_db(
            db_url=self.db_url,
            load_schema=True,
        )

    async def close(self):
        await Tortoise.close_connections()

    async def resume(
        self,
        blocks: int = 1_000_000,
    ):
        await self.setup()
        checkpoint = await Checkpoint.filter(pipeline_id=self.pipeline_id).first()
        if not checkpoint:
            raise ValueError("No checkpoint set")
        await self.backfill(
            start_block=checkpoint.block_number + 1,
            end_block=checkpoint.block_number + blocks,
        )

    async def subscribe(self, start_block: int | BLOCK_STRINGS):
        CoordinatorContext.set_implicits(
            start_block=start_block,
        )
        await self.setup()
        await self.subscriber().run(transformer=self.transformer(context=self.context))
        CoordinatorContext.clear_implicits()

    async def backfill(
        self,
        start_block: int | None = None,
        end_block: int | None = None,
        confirmations: int = 5,
    ) -> int:
        """
        Backfills using Extractor(s), then iterates all events in the extractor using the Transformer.
        This allows an extractor to require processing of events from the previous step.
        """
        await self.setup()
        # ensure all extractors have the same stop block
        start_: int = start_block or self.checkpoint_block or 1
        if not end_block:
            end_block = (await Block.latest()).number - confirmations

        logger.info("Backfilling from %i to %i", start_, end_block)

        CoordinatorContext.set_implicits(
            start_block=start_,
            end_block=end_block,
        )

        if len(self.stages) == 0:
            raise ValueError("No stages set")

        for stage in self.stages:
            logger.info(f"STARTING STAGE: {stage.name}")
            await stage.run(
                self.transformer(context=self.context),
            )
        assert end_block
        await self.checkpoint(end_block)
        CoordinatorContext.clear_implicits()
        return end_block

    async def checkpoint(self, stop_block: int):
        context_dict = self.context.dump()
        checkpoint = await Checkpoint.filter(pipeline_id=self.pipeline_id).first()
        if not checkpoint:
            logger.info("CREATING CHECKPOINT: %i", stop_block)
            await Checkpoint(
                pipeline_id=self.pipeline_id,
                block_number=stop_block,
                context=context_dict,
            ).save()
        else:
            logger.info("UPDATING CHECKPOINT: %i", stop_block)
            checkpoint.block_number = stop_block
            checkpoint.context = context_dict
            await checkpoint.save()
        self.checkpoint_block = stop_block

    async def load(self):
        latest_checkpoint = (
            await Checkpoint.filter(
                pipeline_id=self.pipeline_id,
            )
            .order_by("-block_number")
            .first()
        )
        if not latest_checkpoint:
            raise ValueError("Checkpoint not found")
        self.context = self.context.load(latest_checkpoint.context)
        self.checkpoint_block = latest_checkpoint.block_number
