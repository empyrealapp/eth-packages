import logging
from typing import Literal

from pydantic import BaseModel, Field, PrivateAttr

from ..types.base import ChecksumAddress
from ..synthetics_reader import SyntheticsReader


class OpenPositions(BaseModel):
    network: Literal["arbitrum", "avalanche"] = Field(default="arbitrum")
    address: ChecksumAddress
    _synthetics_reader: SyntheticsReader = PrivateAttr()

    def model_post_init(self, __context):
        self._synthetics_reader = SyntheticsReader(network=self.network)

    async def get_positions(self):
        processed_positions = {}
        raw_positions = await self._synthetics_reader.get_account_positions(self.address)

        for raw_position in raw_positions:
            try:
                processed_position = self._get_data_processing(raw_position)

                # TODO - maybe a better way of building the key?
                if processed_position['is_long']:
                    direction = 'long'
                else:
                    direction = 'short'

                key = "{}_{}".format(
                    processed_position['market_symbol'][0],
                    direction
                )
                processed_positions[key] = processed_position
            except KeyError as e:
                logging.error(f"Incompatible market: {e}")
