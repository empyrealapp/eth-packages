from pydantic import BaseModel

from eth_rpc.types import BlockReference


class FeeHistoryArgs(BaseModel):
    block_count: int
    block_number: BlockReference
    percentiles: list[int]
