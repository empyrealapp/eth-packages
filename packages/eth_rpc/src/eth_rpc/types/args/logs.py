from typing import Any

from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from ..basic import BlockReference


class LogsParams(BaseModel):
    address: HexAddress | list[HexAddress] | None = None
    from_block: BlockReference
    to_block: BlockReference
    topics: list[list[HexStr] | HexStr | None] | None = None

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )


class LogsArgs(BaseModel):
    params: LogsParams

    def model_dump(self, exclude_none=True, by_alias=True, **kwargs) -> dict[str, Any]:
        return super().model_dump(
            exclude_none=exclude_none, by_alias=by_alias, **kwargs
        )
