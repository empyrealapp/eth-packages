from tortoise import Model, fields


class EventModel(Model):
    id = fields.IntField(pk=True)

    chain_id = fields.IntField()
    transaction_hash = fields.CharField(max_length=66)
    log_index = fields.IntField()
    block_hash = fields.CharField(max_length=66)
