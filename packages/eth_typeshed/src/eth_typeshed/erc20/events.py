from eth_rpc import Event

from .types import ApprovalEventType, TransferEventType

TransferEvent = Event[TransferEventType](name="Transfer")
ApprovalEvent = Event[ApprovalEventType](name="Approval")
