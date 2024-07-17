from pydantic import BaseModel

from ..basic import BlockReference


class FeeHistoryArgs(BaseModel):
    block_count: int
    block_number: BlockReference
    percentiles: list[int]
