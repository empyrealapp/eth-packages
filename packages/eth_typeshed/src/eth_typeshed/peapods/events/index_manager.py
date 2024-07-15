from typing import Annotated

from pydantic import BaseModel
from eth_typing import HexAddress

from eth_rpc.types import Indexed, Name, primitives
from eth_rpc.event import Event


class AddIndexType(BaseModel):
    index: Annotated[HexAddress, Indexed]
    verified: primitives.bool


class RemoveIndexType(BaseModel):
    index: Annotated[HexAddress, Indexed]


class SetVerifiedType(BaseModel):
    index: Annotated[HexAddress, Indexed]
    verified: primitives.bool


# from ownable
class OwnershipTransferredType(BaseModel):
    previous_owner: Annotated[HexAddress, Indexed, Name("previousOwner")]
    new_owner: Annotated[HexAddress, Indexed, Name("newOwner")]


AddIndexEvent = Event[AddIndexType](name="AddIndex")
RemoveIndexEvent = Event[RemoveIndexType](name="RemoveIndex")
SetVerifiedEvent = Event[SetVerifiedType](name="SetVerified")
OwnershipTransferredEvent = Event[OwnershipTransferredType](name="OwnershipTransferred")
