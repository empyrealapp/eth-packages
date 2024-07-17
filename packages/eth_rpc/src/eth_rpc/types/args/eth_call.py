from typing import Any, Optional

from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from ..basic import BlockReference, HexInteger


class StateOverride(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    balance: Optional[HexInteger] = None
    nonce: Optional[int] = None
    code: Optional[HexStr] = None
    state: Optional[dict[HexStr, HexStr]] = None
    state_diff: Optional[dict[HexStr, HexStr]] = None

    def model_dump(self, exclude_none=True, by_alias=True, **kwargs) -> dict[str, Any]:
        return super().model_dump(
            exclude_none=exclude_none, by_alias=by_alias, **kwargs
        )


class EthCallParams(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    from_: Optional[HexAddress] = Field(default=None, serialization_alias="from")
    to: HexAddress
    gas: Optional[HexInteger] = None
    gas_price: Optional[HexInteger] = None
    value: Optional[HexInteger] = None
    data: Optional[HexStr] = None

    def model_dump(self, exclude_none=True, **kwargs) -> dict[str, Any]:
        return super().model_dump(exclude_none=exclude_none, **kwargs)


class EthCallArgs(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    params: EthCallParams
    block_number: BlockReference
    state_override_set: Optional[dict[HexAddress, StateOverride]] = None

    def model_dump(self, **kwargs) -> dict[str, Any]:
        params = self.params.model_dump(exclude_none=True, by_alias=True)
        block_number = (
            hex(self.block_number)
            if isinstance(self.block_number, int)
            else self.block_number
        )
        if self.state_override_set:
            state_override = {
                key: value.model_dump()
                for key, value in self.state_override_set.items()
            }
            return {
                "params": params,
                "blockNumber": block_number,
                "stateOverride": state_override,
            }
        return {"params": params, "blockNumber": block_number}


class CallWithBlockArgs(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    params: EthCallParams
    block_number: BlockReference | None

    def model_dump(self, exclude_none=True, by_alias=True, **kwargs) -> dict[str, Any]:
        return super().model_dump(
            exclude_none=exclude_none, by_alias=by_alias, **kwargs
        )
