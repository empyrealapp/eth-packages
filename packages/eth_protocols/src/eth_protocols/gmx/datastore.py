from typing import Literal

from pydantic import BaseModel, Field, PrivateAttr

from eth_typeshed.gmx import GMXEnvironment, Datastore as DatastoreContract

PRECISION = 30


class Datastore(BaseModel):
    network: Literal["arbitrum", "avalanche"] = Field(default="arbitrum")
    _environment: GMXEnvironment = PrivateAttr()
    _contract: DatastoreContract = PrivateAttr()

    def model_post_init(self, __context):
        super().model_post_init(__context)

        self._environment = GMXEnvironment.get_environment(self.network)
        self._contract = DatastoreContract[self.network_type](address=self._environment.datastore)

    async def get_uint(self, key: str) -> int:
        return await self._contract.get_uint(key).get()
