from typing import Any

from eth_typing import HexAddress, HexStr
from pydantic import BaseModel

from ..basic import BlockReference


class GetStorageArgs(BaseModel):
    storage_address: HexAddress
    slot_position: HexStr
    block_number: BlockReference


class GetCodeArgs(BaseModel):
    address: HexAddress
    block_number: BlockReference | None = None
    block_hash: HexStr | None = None

    def model_dump(self, exclude_none=True, **kwargs) -> dict[str, Any]:
        return super().model_dump(exclude_none=exclude_none, **kwargs)
