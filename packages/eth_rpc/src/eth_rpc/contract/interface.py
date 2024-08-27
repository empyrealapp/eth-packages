from typing import ClassVar, Optional

from eth_rpc._request import Request
from eth_rpc.types import Network
from eth_typing import HexAddress, HexStr
from pydantic import Field, PrivateAttr


class ContractT(Request):
    _network: ClassVar[type[Network] | None] = PrivateAttr(default=None)

    address: HexAddress
    code_override: Optional[HexStr] = Field(default=None)
