from typing import Any

from eth_typing import HexAddress
from tortoise import Model, fields
from tortoise.transactions import in_transaction


class ContractEvent(Model):
    """
    A default model for sourcing event data
    """

    id = fields.IntField(pk=True)
    chain = fields.IntField(index=True)
    address = fields.CharField(index=True, max_length=42)
    block_number = fields.IntField(index=True)
    block_hash = fields.CharField(index=True, max_length=66)
    transaction_index = fields.IntField()
    transaction_hash = fields.CharField(index=True, max_length=66)
    log_index = fields.IntField(index=True)
    name = fields.TextField()
    topic0 = fields.CharField(index=True, max_length=256)
    event_type = fields.CharField(index=True, max_length=256)
    event_data: dict[str, Any] = fields.JSONField()
    invalidated = fields.BooleanField(default=False)
    stage_id = fields.CharField(max_length=32, null=True)
    confirmed = fields.BooleanField(default=False)

    @classmethod
    async def clear_reorg_events(cls, block_number: int, chain_id: int):
        await cls.filter(
            block_number__gt=block_number,
            chain_id=chain_id,
        ).delete()

    def __str__(self):
        return f"Event(ID: {self.id}, {self.event_type}, Block: {self.block_number})"

    # Optionally, you can also define __repr__ for a more developer-focused representation
    def __repr__(self):
        return (
            f"<Events id={self.id} name={self.name} block_number={self.block_number}>"
        )

    @classmethod
    async def get_raw_sql(
        cls,
        event_type: str,
        chain: int,
        block_number: int,
        address: str,
        json_filters: dict[str, str],
        json_select_fields: dict[str, str],
        limit: int | None = None,
    ):
        query = """
            SELECT event_type, chain, block_number, transaction_index, log_index, address
        """

        for json_key, field_alias in json_select_fields.items():
            query += f", event_data->>'{json_key}' as {field_alias}"

        query += """
            FROM events
            WHERE event_type = ?
            AND chain = ?
            AND block_number > ?
        """

        params = [event_type, chain, block_number]

        if address:
            query += " AND address = ?"
            params.append(address)

        for field_path, value in json_filters.items():
            query += f" AND event_data->>'{field_path}' = ?"
            params.append(str(value))

        query += " ORDER BY block_number, transaction_index, log_index"
        if limit:
            query += f" LIMIT {limit}"
        async with in_transaction() as conn:
            result = await conn.execute_query_dict(query, params)
        return result

    @classmethod
    async def get_for_type(
        cls, chain_id: int, address: HexAddress, event_type: str
    ) -> list["ContractEvent"]:
        return await cls.filter(
            chain=chain_id,
            address=address,
            event_type=event_type,
        ).order_by("-block_number")

    class Meta:
        table = "events"
        unique_together = (
            "chain",
            "address",
            "block_number",
            "block_hash",
            "transaction_index",
            "log_index",
        )
