from eth_rpc.types import HexInteger
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class FeeHistory(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    oldest_block: HexInteger
    base_fee_per_gas: list[HexInteger]
    base_fee_per_blob_gas: list[HexInteger] | None = None
    gas_used_ratio: list[float]
    reward: list[list[HexInteger]]

    def mean_fee(self, buffer=1):
        """gas_price"""
        return int(buffer * sum(self.base_fee_per_gas) / len(self.base_fee_per_gas))
