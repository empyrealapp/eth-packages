from typing import Annotated, Optional

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from eth_rpc.utils import to_bytes32
from eth_typing import HexAddress, HexStr
from pydantic import PrivateAttr

from .constants import ADMIN_SLOT, EIP1967_IMPLEMENTATION_SLOT, OZ_IMPLEMENTATION_SLOT
from .types import (
    ApproveRequest,
    OwnerSpenderRequest,
    TransferFromRequest,
    TransferRequest,
)


class ERC20Metadata(ProtocolBase):
    _decimals: int | None = PrivateAttr(None)
    _name: str | None = PrivateAttr(None)
    _symbol: str | None = PrivateAttr(None)

    name: ContractFunc[
        NoArgs,
        Annotated[primitives.string, Name("_name")],
    ] = METHOD
    symbol: ContractFunc[
        NoArgs,
        Annotated[primitives.string, Name("_symbol")],
    ] = METHOD
    decimals: ContractFunc[
        NoArgs,
        Annotated[primitives.uint256, Name("_decimals")],
    ] = METHOD

    def get_decimals(self):
        if not self._decimals:
            self._decimals = self.decimals().get()
        return self._decimals

    def get_name(self):
        if not self._name:
            self._name = self.name().get()
        return self._name

    def get_symbol(self):
        if not self._symbol:
            self._symbol = self.symbol().get()
        return self._symbol

    async def load_async(self):
        from eth_typeshed.multicall import multicall

        if not (self._name and self._symbol and self._decimals):
            self._name, self._symbol, self._decimals = await multicall.execute(
                self.name(),
                self.symbol(),
                self.decimals(),
            )


class ERC20(ERC20Metadata):
    balance_of: Annotated[
        ContractFunc[
            Annotated[primitives.address, Name("owner")],
            Annotated[primitives.uint256, Name("amount")],
        ],
        Name("balanceOf"),
    ] = METHOD
    total_supply: Annotated[
        ContractFunc[
            NoArgs,
            Annotated[primitives.uint256, Name("_supply")],
        ],
        Name("totalSupply"),
    ] = METHOD
    transfer: ContractFunc[
        TransferRequest,
        Annotated[bool, Name("success")],
    ] = METHOD
    transfer_from: Annotated[
        ContractFunc[
            TransferFromRequest,
            Annotated[bool, Name("success")],
        ],
        Name("transferFrom"),
    ] = METHOD
    approve: ContractFunc[
        ApproveRequest,
        Annotated[primitives.bool, Name("success")],
    ] = METHOD
    allowance: ContractFunc[
        OwnerSpenderRequest,
        Annotated[primitives.bool, Name("success")],
    ] = METHOD

    def get_allowance_slot(self, owner: str, spender: str):
        """
        Gets the allowance slot given token/owner/spender combination
        """
        response = self._get_debug_tracecall(
            self.address,
            data=f"0xdd62ed3e000000000000000000000000{owner.replace('0x', '')}000000000000000000000000{spender.replace('0x', '')}",
        )
        if not response:
            return None
        try:
            storage = response[self.address.lower()]["storage"]
        except KeyError:
            return None

        for key in [
            OZ_IMPLEMENTATION_SLOT,
            ADMIN_SLOT,
            EIP1967_IMPLEMENTATION_SLOT,
        ]:
            if hex(key) in storage:
                del storage[hex(key)]
        if len(storage) != 1:
            # TOOD: this isn't really a ValueError, but we need to allow the client to handle this differently
            raise ValueError(list(storage.keys()))
        return list(storage.keys())[0]

    def get_balance_slot(self, owner: primitives.address) -> Optional[HexStr]:
        """
        Attempts to find the balance slot for an address.
        This will not work on tokens with irregular balance calculation.
        """
        balance = self.balance_of(owner).sync.call().raw
        result = self._get_debug_tracecall(
            self.address,
            data=f"0x70a08231000000000000000000000000{owner.replace('0x', '')}",
        )
        storage = result[self.address.lower()]["storage"]
        for slot in storage:
            if balance in storage[slot]:
                return slot

        # Unknown slot return None
        return None

    def balance_state_diff(
        self, owner: primitives.address, balance: int
    ) -> Optional[dict]:
        slot = self.get_balance_slot(owner)
        if slot:
            return {
                self.address: {
                    "stateDiff": {
                        slot: to_bytes32(balance),
                    },
                },
            }
        return {}

    def allowance_state_diff(
        self, owner: HexAddress, spender: HexAddress, amount: int
    ) -> Optional[dict]:
        slot = self.get_allowance_slot(owner, spender)
        if slot:
            return {
                self.address: {
                    "stateDiff": {
                        slot: to_bytes32(amount),
                    }
                },
            }
        return {}

    def __repr__(self):
        return f"<ERC20 address={self.address}>"


class ERC20BytesMetadata(ProtocolBase):
    name: ContractFunc[
        NoArgs,
        Annotated[primitives.bytes32, Name("_name")],
    ] = METHOD
    symbol: ContractFunc[
        NoArgs,
        Annotated[primitives.bytes32, Name("_symbol")],
    ] = METHOD
