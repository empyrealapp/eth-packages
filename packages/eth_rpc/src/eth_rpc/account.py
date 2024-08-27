from typing import Generic

from eth_rpc.models import Account as AccountModel
from eth_rpc.types import BLOCK_STRINGS
from eth_rpc.types.args import GetAccountArgs
from eth_typing import HexAddress
from typing_extensions import TypeVar

from ._request import Request
from .types import HexInteger, RPCResponseModel

Network = TypeVar("Network", default=None)


class Account(Request, AccountModel, Generic[Network]):
    def get_balance(
        self, address: HexAddress, block_number: int | BLOCK_STRINGS = "latest"
    ) -> RPCResponseModel[GetAccountArgs, HexInteger]:
        return RPCResponseModel(
            self.rpc().get_balance,
            GetAccountArgs(
                address=address,
                block_number=(
                    HexInteger(block_number)
                    if isinstance(block_number, int)
                    else block_number
                ),
            ),
        )

    def get_account(
        self, address: HexAddress, block_number: int | BLOCK_STRINGS = "latest"
    ) -> RPCResponseModel[GetAccountArgs, AccountModel]:
        return RPCResponseModel(
            self.rpc().get_account,
            GetAccountArgs(
                address=address,
                block_number=(
                    HexInteger(block_number)
                    if isinstance(block_number, int)
                    else block_number
                ),
            ),
        )
