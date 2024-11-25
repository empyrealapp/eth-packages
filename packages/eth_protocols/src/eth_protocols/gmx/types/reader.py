from pydantic import BaseModel

from .base import ChecksumAddress
from .tokens import TokenInfo


class ExecutionPriceResult(BaseModel):
    execution_price: float
    price_impact_usd: float


class MarketInfo(BaseModel):
    gmx_market_address: ChecksumAddress
    market_symbol: str
    index_token_address: ChecksumAddress
    market_metadata: TokenInfo
    long_token_metadata: TokenInfo
    long_token_address: ChecksumAddress
    short_token_metadata: TokenInfo
    short_token_address: ChecksumAddress
