from eth_rpc.event import Event
from eth_typing import HexAddress
from pydantic import BaseModel


class SetYieldAdminType(BaseModel):
    newFee: HexAddress


class SetYieldBurnType(BaseModel):
    newFee: HexAddress


SetYieldAdminEvent = Event[SetYieldAdminType](name="SetYieldAdmin")
SetYieldBurnEvent = Event[SetYieldBurnType](name="SetYieldBurn")
