from typing import Generic, TypeVar

from eth_rpc.types import HexInteger, Network
from eth_rpc.utils import RPCModel
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar("T", bound=BaseModel)


class Log(RPCModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    transaction_hash: HexStr
    address: HexAddress
    block_hash: HexStr
    block_number: HexInteger
    data: HexStr
    log_index: HexInteger
    removed: bool
    topics: list[HexStr]
    transaction_index: HexInteger

    def __repr__(self):
        return f"<Log block={self.block_number} index={self.log_index}>"

    __str__ = __repr__


class EventData(BaseModel, Generic[T]):
    """
    This joins a log with it's transformed format (T).
    It needs to be in models because Models rely on Types.
    """

    name: str
    log: Log
    event: T
    network: type[Network]

    @property
    def tx(self):
        # temporary while I remove event_data.tx
        return self.log

    def __hash__(self):
        # TODO: this could be more efficient
        return hash(
            f"{self.tx.transaction_hash}|{self.tx.block_number}|{self.tx.transaction_index}|{self.tx.log_index}"
        )

    def __repr__(self):
        return f"<name={self.name} log={self.log} {{{self.event}}}>>"

    __str__ = __repr__
