from eth_abi import encode
from pydantic import BaseModel

from eth_rpc.function import convert_base_model


class Struct(BaseModel):
    def to_bytes(self):
        return encode(
            convert_base_model(self.__class__), list(self.model_dump().values())
        )
