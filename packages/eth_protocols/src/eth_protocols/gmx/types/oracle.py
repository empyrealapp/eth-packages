from eth_typing import HexAddress
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class OraclePrice(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel
    )

    id: int
    min_block_number: int | None
    min_block_hash: str | None
    oracle_decimals: int | None
    token_symbol: str
    token_address: HexAddress
    min_price: str | None
    max_price: str | None
    signer: str | None
    signature: str | None = None
    signature_without_block_hash: str | None
    created_at: str
    min_block_timestamp: int
    oracle_keeper_key: str
    max_block_timestamp: int
    max_block_number: int | None
    max_block_hash: str | None
    max_price_full: str
    min_price_full: str
    oracle_keeper_record_id: str | None
    oracle_keeper_fetch_type: str
    oracle_type: str
    blob: str


class OraclePriceResponse(BaseModel):
    signed_prices: list[OraclePrice] = Field(alias="signedPrices")
