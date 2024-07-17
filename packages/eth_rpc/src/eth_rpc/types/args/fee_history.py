from eth_rpc.types import BlockReference
from pydantic import BaseModel


class FeeHistoryArgs(BaseModel):
    block_count: int
    block_number: BlockReference
    percentiles: list[int]
