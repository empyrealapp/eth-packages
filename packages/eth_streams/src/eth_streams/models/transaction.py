from tortoise import fields
from tortoise.models import Model


class Transaction(Model):
    # hash is the id
    id = fields.CharField(
        pk=True,
        max_length=66,
        index=True,
    )

    block_number = fields.IntField()
    block_hash = fields.CharField(max_length=66, null=True)
    from_ = fields.CharField(max_length=42, index=True)
    to = fields.CharField(max_length=42, null=True)
    index = fields.IntField()
    gas = fields.DecimalField(max_digits=18, decimal_places=0)
    gas_price = fields.DecimalField(max_digits=18, decimal_places=0)
    max_fee_per_gas = fields.DecimalField(max_digits=18, decimal_places=0, null=True)
    max_priority_fee_per_gas = fields.DecimalField(
        max_digits=18, decimal_places=0, null=True
    )
    type = fields.IntField(null=True)
    receipt_gas_used = fields.DecimalField(max_digits=18, decimal_places=0)
    receipt_effective_gas_price = fields.DecimalField(max_digits=18, decimal_places=0)
    status = fields.IntField()

    class Meta:
        table = "transactions"
