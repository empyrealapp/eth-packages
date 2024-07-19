from eth_streams.utils import EventModel
from tortoise import Model, fields


class PairCreated(Model):
    # `{chain_id}-{pair_address}`
    id = fields.CharField(max_length=50, pk=True)

    chain_id = fields.IntField()
    pair_address = fields.CharField(max_length=42)
    factory_address = fields.CharField(max_length=42)
    token0_address = fields.CharField(max_length=42)
    token1_address = fields.CharField(max_length=42)
    created_block_number = fields.IntField()

    # only for uniswapV3
    fee = fields.IntField(null=True)

    class Meta:
        table = "pairs"
        unique_together = (
            "chain_id",
            "pair_address",
        )


class SyncEvent(EventModel):
    id = fields.IntField(pk=True)

    pair_address = fields.CharField(max_length=42)
    amount0 = fields.IntField()
    amount1 = fields.IntField()


class SwapEvent(EventModel):
    pair_address = fields.CharField(max_length=42)

    amount0_in = fields.IntField()
    amount0_out = fields.IntField()
    amount1_in = fields.IntField()
    amount1_out = fields.IntField()
    sender = fields.CharField(max_length=42)
    recipient = fields.CharField(max_length=42)
