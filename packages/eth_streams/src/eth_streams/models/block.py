from tortoise import Model, fields


class Block(Model):
    id = fields.IntField(pk=True)

    number = fields.IntField()
    chain_id = fields.IntField()
    timestamp = fields.DatetimeField()
    block_hash = fields.CharField(max_length=66)
    parent_block_hash = fields.CharField(max_length=66)
    hot_block = fields.BooleanField(default=True)
