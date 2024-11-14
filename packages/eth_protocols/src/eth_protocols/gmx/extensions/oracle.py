from typing import Literal

import httpx
from eth_rpc.networks import get_network_by_name
from eth_typing import HexAddress
from pydantic import BaseModel, PrivateAttr

from ..types import OraclePrice, OraclePriceResponse


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

    async def get_recent_prices(self) -> dict[HexAddress, OraclePrice]:
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
