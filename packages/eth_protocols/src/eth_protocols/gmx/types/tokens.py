from pydantic import BaseModel

from .base import ChecksumAddress


class TokenInfo(BaseModel):
    symbol: str
    address: ChecksumAddress
    decimals: int


class TokensInfo(BaseModel):
    tokens: list[TokenInfo]
