from pydantic import BaseModel
from eth_typing import HexAddress

from eth_rpc.event import Event


class SetYieldAdminType(BaseModel):
    newFee: HexAddress


class SetYieldBurnType(BaseModel):
    newFee: HexAddress


SetYieldAdminEvent = Event[SetYieldAdminType](name="SetYieldAdmin")
SetYieldBurnEvent = Event[SetYieldBurnType](name="SetYieldBurn")
