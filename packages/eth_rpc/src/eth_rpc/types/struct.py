from eth_abi import encode
from eth_rpc.function import convert_base_model
from pydantic import BaseModel


class Struct(BaseModel):
    """
    This is a type used to denote a solidity struct.  It is necessary
    to set this so the encoder knows to treat it as a single struct,
    and not a list of fields.

    For example, (uint8,bytes32) will encode differently from ((uint8,bytes32))

    One is a field with two arguments, the other is a field with a single argument,
        that is a struct with two fields
    """
    def to_bytes(self):
        types = ','.join(convert_base_model(self.__class__))
        return encode(
            [f'({types})'], [tuple(self.model_dump().values())]
        )
