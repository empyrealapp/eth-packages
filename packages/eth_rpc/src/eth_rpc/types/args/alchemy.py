from typing import Any, Optional

from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from ..basic import HexInteger


class AlchemyParams(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    block_number: Optional[HexInteger]
    block_hash: Optional[HexStr]


class AlchemyBlockReceipt(BaseModel):
    params: AlchemyParams

    def model_dump(self, exclude_none=True, by_alias=True, **kwargs) -> dict[str, Any]:
        return super().model_dump(
            exclude_none=exclude_none, by_alias=by_alias, **kwargs
        )


class AlchemyTokenBalance(BaseModel):
    contract_address: HexAddress = Field(alias="contractAddress")
    token_balance: HexStr | None = Field(alias="tokenBalance", default=None)
    error: str | None = Field(default=None)


class AlchemyTokenBalances(BaseModel):
    address: HexAddress
    token_balances: list[AlchemyTokenBalance] = Field(alias="tokenBalances")
