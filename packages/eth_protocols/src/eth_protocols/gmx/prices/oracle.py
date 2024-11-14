from typing import Literal

import httpx
from eth_rpc.networks import get_network_by_name
from eth_typing import HexAddress
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
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


class PriceOracle(BaseModel):
    network: Literal["arbitrum", "avalanche"] = "arbitrum"
    _oracle_url: str = PrivateAttr()

    @property
    def network_type(self):
        return get_network_by_name(self.network)

    def model_post_init(self, __context):
        self._oracle_url = (
            "https://arbitrum-api.gmxinfra.io/signed_prices/latest"
            if self.network == "arbitrum"
            else "https://avalanche-api.gmxinfra.io/signed_prices/latest"
        )

    async def get_recent_prices(self):
        """
        Get raw output of the GMX rest v2 api for signed prices

        Returns
        -------
        dict
            dictionary containing raw output for each token as its keys.

        """
        raw_output = await self._make_query()
        return self._process_output(raw_output)

    async def _make_query(self) -> OraclePriceResponse:
        """
        Make request using oracle url

        Returns
        -------
        requests.models.Response
            raw request response.

        """
        async with httpx.AsyncClient() as client:
            response = await client.get(self._oracle_url)
        return OraclePriceResponse(**response.json())

    def _process_output(self, output: OraclePriceResponse) -> dict[HexAddress, OraclePrice]:
        processed: dict[str, OraclePriceResponse] = {}
        for i in output.signed_prices:
            processed[i.token_address] = i

        return processed
