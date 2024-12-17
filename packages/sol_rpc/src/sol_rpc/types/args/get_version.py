from pydantic import BaseModel, Field


class GetVersionResponse(BaseModel):
    solana_core: str = Field(validation_alias="solana-core")
    feature_set: int = Field(validation_alias="feature-set")
