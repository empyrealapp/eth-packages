from collections.abc import Awaitable
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Generic, Literal, Optional, TypeVar, cast, overload

from eth_rpc.models import AccessListResponse
from eth_rpc.types import (
    BASIC_TYPES,
    BLOCK_STRINGS,
    CallWithBlockArgs,
    EthCallArgs,
    EthCallParams,
    HexInteger,
    MaybeAwaitable,
    Network,
    RPCResponseModel,
)
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel

from .._transport import _force_get_global_rpc
from ..block import Block
from ..constants import ADDRESS_ZERO
from ..rpc.core import RPC
from ..transaction import PreparedTransaction
from ..utils import run
from ..wallet import BaseWallet
from .eth_response import EthResponse
from .func_signature import FuncSignature
from .interface import ContractT

# from .contract import Contract

T = TypeVar(
    "T",
    bound=tuple
    | BaseModel
    | BASIC_TYPES
    | list[BASIC_TYPES]
    | tuple[BASIC_TYPES, ...]
    | HexAddress,
)
U = TypeVar("U")


@dataclass
class ContractFunc(Generic[T, U]):
    func: FuncSignature[T, U]
    contract: ContractT
    data: HexStr = HexStr("0x")

    _network: type[Network] | None = None

    def __post_init__(self):
        self._network = self.contract._network

    @property
    def sync(self) -> "ContractFuncSync[T, U]":
        obj = deepcopy(self)
        obj.__class__ = ContractFuncSync
        obj = cast(ContractFuncSync, obj)
        return obj

    @property
    def address(self):
        return self.contract.address

    @property
    def name(self):
        return self.func.name

    @property
    def alias(self):
        return self.func.alias or self.func.name

    def _rpc(self) -> "RPC":
        """
        This uses the default network, unless a network has been provided, then immediately unsets the network.
        This makes it safe for async code.
        """
        from .._transport import _force_get_global_rpc

        if self._network is None:
            return _force_get_global_rpc(None)
        response = _force_get_global_rpc(self._network)
        return response

    def __call__(
        self,
        *args: T,
    ):
        new_self = deepcopy(self)
        if len(args) == 0:
            new_self.data = self.func.encode_call(inputs=())  # type: ignore
        elif len(args) == 1:
            new_self.data = self.func.encode_call(inputs=args[0])
        else:
            # assumed you provided the args
            _args: T = cast(T, args)
            new_self.data = self.func.encode_call(inputs=_args)
        return new_self

    def encode(self):
        return bytes.fromhex(self.data[2:])

    def decode(self, result: bytes) -> U:
        return self.func.decode_result(HexStr(result.hex()))

    async def _estimate_gas(
        self,
        from_: Optional[HexAddress] = None,
        block_number: HexInteger | Literal["latest", "pending"] = "latest",
        sync: bool = False,
        buffer: float = 1.25,
    ) -> HexInteger:
        query: RPCResponseModel[CallWithBlockArgs, HexInteger] = RPCResponseModel(
            self._rpc().estimate_gas,
            CallWithBlockArgs(
                params=EthCallParams(
                    from_=from_,
                    to=self.address,
                    data=self.data,
                ),
                block_number=block_number,
            ),
        )
        if sync:
            return HexInteger(query.sync * buffer)
        return HexInteger((await query) * buffer)

    @overload
    def estimate_gas(
        self,
        *,
        sync: Literal[True],
        from_: Optional[HexAddress] = ...,
        block_number: HexInteger | Literal["latest", "pending"] = ...,
    ) -> HexInteger: ...

    @overload
    def estimate_gas(
        self,
        *,
        sync: Literal[False] = ...,
        from_: Optional[HexAddress] = ...,
        block_number: HexInteger | Literal["latest", "pending"] = ...,
    ) -> Awaitable[HexInteger]: ...

    def estimate_gas(
        self,
        *,
        from_: Optional[HexAddress] = None,
        block_number: HexInteger | Literal["latest", "pending"] = "latest",
        sync: bool = False,
    ) -> MaybeAwaitable[HexInteger]:
        return run(
            self._estimate_gas, from_=from_, block_number=block_number, sync=sync
        )

    async def _access_list(
        self,
        *,
        gas: int = 10000000,
        sender: HexAddress = ADDRESS_ZERO,
        block_number: int | None = None,
        sync: bool = False,
    ) -> AccessListResponse:
        if sync:
            return RPCResponseModel(
                self._rpc().create_access_list,
                CallWithBlockArgs(
                    params=EthCallParams(
                        from_=sender,
                        to=self.address,
                        data=self.data,
                        gas=HexInteger(gas),
                    ),
                    block_number=HexInteger(block_number) if block_number else None,
                ),
            ).sync
        return await RPCResponseModel(
            self._rpc().create_access_list,
            CallWithBlockArgs(
                params=EthCallParams(
                    from_=sender,
                    to=self.address,
                    data=self.data,
                    gas=HexInteger(gas),
                ),
                block_number=HexInteger(block_number) if block_number else None,
            ),
        )

    @overload
    def access_list(
        self,
        *,
        sync: Literal[True],
        gas: int = 10000000,
        sender: HexAddress = ADDRESS_ZERO,
        block_number: int | None = None,
    ) -> AccessListResponse: ...

    @overload
    def access_list(
        self,
        *,
        gas: int = 10000000,
        sender: HexAddress = ADDRESS_ZERO,
        block_number: int | None = None,
    ) -> Awaitable[AccessListResponse]: ...

    def access_list(
        self,
        *,
        gas: int = 10000000,
        sender: HexAddress = ADDRESS_ZERO,
        block_number: int | None = None,
        sync: bool = False,
    ) -> MaybeAwaitable[AccessListResponse]:
        return run(
            self._access_list,
            gas=gas,
            sender=sender,
            block_number=block_number,
            sync=sync,
        )

    async def _call(
        self,
        from_: Optional[HexAddress] = None,
        block_number: int | BLOCK_STRINGS = "latest",
        value: HexInteger | int = 0,
        state_diff: dict[HexAddress, Any] = {},
        sync: bool = True,
    ) -> EthResponse[T, U]:
        # TODO: as_dict feels useful to get back a dict with named fields, but it's odd
        #       to have a few different return types for the same function
        if self.contract.code_override:
            contract_state = state_diff.get(self.address, {})
            state_diff[self.address] = {
                "code": self.contract.code_override
            } | contract_state
        if sync:
            response = self._rpc().eth_call.sync(
                EthCallArgs(
                    params=EthCallParams(
                        from_=from_,
                        to=self.address,
                        value=HexInteger(value),
                        data=self.data,
                    ),
                    block_number=(
                        HexInteger(block_number)
                        if isinstance(block_number, int)
                        else block_number
                    ),
                    state_override_set=state_diff,
                )
            )
        else:
            response = await self._rpc().eth_call(
                EthCallArgs(
                    params=EthCallParams(
                        from_=from_,
                        to=self.address,
                        value=HexInteger(value),
                        data=self.data,
                    ),
                    block_number=(
                        HexInteger(block_number)
                        if isinstance(block_number, int)
                        else block_number
                    ),
                    state_override_set=state_diff,
                )
            )
        return EthResponse[T, U](
            result=response,
            func=self.func,
        )

    @overload
    def call(
        self,
        *,
        sync: Literal[True],
        from_: Optional[HexAddress] = ...,
        block_number: int | BLOCK_STRINGS = ...,
        value: HexInteger | int = ...,
        state_diff: dict[HexAddress, Any] = ...,
    ) -> EthResponse[T, U]: ...

    @overload
    def call(
        self,
        *,
        sync: Literal[False],
        from_: Optional[HexAddress] = ...,
        block_number: int | BLOCK_STRINGS = ...,
        value: HexInteger | int = ...,
        state_diff: dict[HexAddress, Any] = ...,
    ) -> Awaitable[EthResponse[T, U]]: ...

    @overload
    def call(
        self,
        *,
        from_: Optional[HexAddress] = ...,
        block_number: int | BLOCK_STRINGS = ...,
        value: HexInteger | int = ...,
        state_diff: dict[HexAddress, Any] = ...,
    ) -> Awaitable[EthResponse[T, U]]: ...

    @overload
    def call(
        self,
        *,
        sync: bool,
        from_: Optional[HexAddress] = ...,
        block_number: int | BLOCK_STRINGS = ...,
        value: HexInteger | int = ...,
        state_diff: dict[HexAddress, Any] = ...,
    ) -> MaybeAwaitable[EthResponse[T, U]]: ...

    def call(
        self,
        *,
        from_: Optional[HexAddress] = None,
        block_number: int | BLOCK_STRINGS = "latest",
        value: HexInteger | int = 0,
        state_diff: dict[HexAddress, Any] = {},
        sync: bool = False,
    ) -> MaybeAwaitable[EthResponse[T, U]]:
        return run(self._call, from_, block_number, value, state_diff, sync=sync)

    async def _get(
        self,
        from_: Optional[HexAddress] = None,
        block_number: int | BLOCK_STRINGS = "latest",
        value: HexInteger | int = 0,
        state_diff: dict[HexAddress, Any] = {},
        sync: bool = False,
    ) -> U:
        """shorthand for call().decode()"""
        return (
            await self._call(
                from_=from_,
                block_number=block_number,
                value=value,
                state_diff=state_diff,
                sync=sync,
            )
        ).decode()

    @overload
    def get(
        self,
        *,
        sync: Literal[True],
        from_: Optional[HexAddress] = ...,
        block_number: int | BLOCK_STRINGS = ...,
        value: HexInteger | int = ...,
        state_diff: dict[HexAddress, Any] = ...,
    ) -> U: ...

    @overload
    def get(
        self,
        *,
        sync: Literal[False] = ...,
        from_: Optional[HexAddress] = ...,
        block_number: int | BLOCK_STRINGS = ...,
        value: HexInteger | int = ...,
        state_diff: dict[HexAddress, Any] = ...,
    ) -> Awaitable[U]: ...

    def get(
        self,
        *,
        from_: Optional[HexAddress] = None,
        block_number: int | BLOCK_STRINGS = "latest",
        value: HexInteger | int = 0,
        state_diff: dict[HexAddress, Any] = {},
        sync: bool = False,
    ) -> MaybeAwaitable[U]:
        return run(
            self._get,
            from_=from_,
            block_number=block_number,
            value=value,
            state_diff=state_diff,
            sync=sync,
        )

    async def _prepare(
        self,
        wallet: "BaseWallet",
        *,
        nonce: Optional[int] = None,
        value: int = 0,
        gas_price: Optional[int] = None,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
        use_access_list: bool = False,
        sync: bool = False,
        buffer: float = 1.25,
    ) -> PreparedTransaction:
        gas = await self._estimate_gas(from_=wallet.address, sync=sync, buffer=buffer)
        if use_access_list:
            if sync:
                access_list_response = self.access_list(
                    sender=wallet.address, sync=True
                )
            else:
                access_list_response = await self.access_list(sender=wallet.address)
            access_list = access_list_response.access_list
        else:
            access_list = None
        rpc = _force_get_global_rpc()
        if sync:
            chain_id = rpc.chain_id.sync()
        else:
            chain_id = await rpc.chain_id()

        if not (max_fee_per_gas or gas_price):
            if sync:
                max_priority_fee_per_gas = (
                    max_priority_fee_per_gas or Block.priority_fee().sync
                )
                base_fee_per_gas = Block.pending().sync.base_fee_per_gas
            else:
                max_priority_fee_per_gas = (
                    max_priority_fee_per_gas or await Block.priority_fee()
                )

                # TODO: fix pending()
                block = await Block.pending()
                base_fee_per_gas = block.base_fee_per_gas

            assert base_fee_per_gas, "block is earlier than London Hard Fork"
            max_fee_per_gas = max_fee_per_gas or (
                2 * base_fee_per_gas + max_priority_fee_per_gas
            )

        if sync:
            return PreparedTransaction(
                data=self.data,
                to=self.address,
                gas=HexInteger(gas),
                gas_price=gas_price,
                max_fee_per_gas=max_fee_per_gas,
                max_priority_fee_per_gas=max_priority_fee_per_gas,
                nonce=nonce or wallet.get_nonce().sync,
                value=value,
                access_list=access_list,
                chain_id=chain_id,
            )
        return PreparedTransaction(
            data=self.data,
            to=self.address,
            gas=HexInteger(gas),
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            nonce=nonce or await wallet.get_nonce(),
            value=value,
            access_list=access_list,
            chain_id=chain_id,
        )

    @overload
    def prepare(
        self,
        wallet: "BaseWallet",
        *,
        sync: Literal[True],
        nonce: Optional[int] = ...,
        value: int = ...,
        gas_price: Optional[int] = ...,
        max_fee_per_gas: Optional[int] = ...,
        max_priority_fee_per_gas: Optional[int] = ...,
        use_access_list: bool = ...,
    ) -> PreparedTransaction: ...

    @overload
    def prepare(
        self,
        wallet: "BaseWallet",
        *,
        nonce: Optional[int] = ...,
        value: int = ...,
        gas_price: Optional[int] = ...,
        max_fee_per_gas: Optional[int] = ...,
        max_priority_fee_per_gas: Optional[int] = ...,
        use_access_list: bool = ...,
    ) -> Awaitable[PreparedTransaction]: ...

    def prepare(
        self,
        wallet: "BaseWallet",
        *,
        nonce: Optional[int] = None,
        value: int = 0,
        gas_price: Optional[int] = None,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
        use_access_list: bool = False,
        sync: bool = False,
    ) -> MaybeAwaitable[PreparedTransaction]:
        return run(
            self._prepare,
            wallet,
            nonce=nonce,
            value=value,
            gas_price=gas_price,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            use_access_list=use_access_list,
            sync=sync,
        )

    async def _execute(
        self,
        wallet: "BaseWallet",
        *,
        nonce: Optional[int] = None,
        value: int = 0,
        gas_price: Optional[int] = None,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
        use_access_list: bool = False,
        sync: bool = True,
    ) -> HexStr:
        if sync is True:
            prepared_tx = self.prepare(
                wallet,
                nonce=nonce,
                value=value,
                gas_price=gas_price,
                max_fee_per_gas=max_fee_per_gas,
                max_priority_fee_per_gas=max_priority_fee_per_gas,
                use_access_list=use_access_list,
                sync=True,
            )
        else:
            prepared_tx = await self.prepare(
                wallet,
                nonce=nonce,
                value=value,
                max_fee_per_gas=max_fee_per_gas,
                max_priority_fee_per_gas=max_priority_fee_per_gas,
                use_access_list=use_access_list,
            )
        signed_tx = wallet.sign_transaction(prepared_tx)
        if sync:
            return wallet.send_raw_transaction(
                HexStr("0x" + signed_tx.raw_transaction)
            ).sync
        return await wallet.send_raw_transaction(
            HexStr("0x" + signed_tx.raw_transaction)
        )

    @overload
    def execute(
        self,
        wallet: "BaseWallet",
        *,
        sync: Literal[True],
        nonce: Optional[int] = ...,
        value: int = ...,
        gas_price: Optional[int] = ...,
        max_fee_per_gas: Optional[int] = ...,
        max_priority_fee_per_gas: Optional[int] = ...,
        use_access_list: bool = ...,
    ) -> HexStr: ...

    @overload
    def execute(
        self,
        wallet: "BaseWallet",
        *,
        nonce: Optional[int] = ...,
        value: int = ...,
        gas_price: Optional[int] = ...,
        max_fee_per_gas: Optional[int] = ...,
        max_priority_fee_per_gas: Optional[int] = ...,
        use_access_list: bool = ...,
    ) -> Awaitable[HexStr]: ...

    def execute(
        self,
        wallet: "BaseWallet",
        *,
        nonce: Optional[int] = None,
        value: int = 0,
        gas_price: Optional[int] = None,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
        use_access_list: bool = False,
        sync: bool = False,
    ) -> MaybeAwaitable[HexStr]:
        return run(
            self._execute,
            wallet,
            nonce=nonce,
            value=value,
            gas_price=gas_price,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            use_access_list=use_access_list,
            sync=sync,
        )

    def _encode_block_number(
        self, block_number: int | Literal["latest", "pending"] = "pending"
    ):
        if isinstance(block_number, int):
            return hex(block_number)
        return block_number


class ContractFuncSync(ContractFunc[T, U]):
    SYNC: Literal[True] = True

    def estimate_gas(  # type: ignore
        self,
        *,
        from_: Optional[HexAddress] = None,
        block_number: HexInteger | Literal["latest", "pending"] = "latest",
    ) -> HexInteger:
        return super().estimate_gas(
            from_=from_, block_number=block_number, sync=self.SYNC
        )

    def access_list(  # type: ignore
        self,
        *,
        gas: int = 10000000,
        sender: HexAddress = ADDRESS_ZERO,
        block_number: int | None = None,
    ) -> AccessListResponse:
        return super().access_list(
            gas=gas,
            sender=sender,
            block_number=block_number,
            sync=self.SYNC,
        )

    def call(  # type: ignore
        self,
        *,
        from_: Optional[HexAddress] = None,
        block_number: int | BLOCK_STRINGS = "latest",
        value: HexInteger | int = 0,
        state_diff: dict[HexAddress, Any] = {},
    ) -> EthResponse[T, U]:
        return super().call(
            from_=from_,
            block_number=block_number,
            value=value,
            state_diff=state_diff,
            sync=self.SYNC,
        )

    def get(  # type: ignore
        self,
        *,
        from_: Optional[HexAddress] = None,
        block_number: int | BLOCK_STRINGS = "latest",
        value: HexInteger | int = 0,
        state_diff: dict[HexAddress, Any] = {},
    ) -> U:
        return super().get(
            from_=from_,
            block_number=block_number,
            value=value,
            state_diff=state_diff,
            sync=self.SYNC,
        )

    def prepare(  # type: ignore
        self,
        wallet: "BaseWallet",
        *,
        nonce: Optional[int] = None,
        value: int = 0,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
        use_access_list: bool = False,
    ) -> PreparedTransaction:
        return super().prepare(
            wallet,
            nonce=nonce,
            value=value,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            use_access_list=use_access_list,
            sync=self.SYNC,
        )

    def execute(  # type: ignore
        self,
        wallet: BaseWallet,
        *,
        nonce: Optional[int] = None,
        value: int = 0,
        max_fee_per_gas: Optional[int] = None,
        max_priority_fee_per_gas: Optional[int] = None,
        use_access_list: bool = False,
    ) -> HexStr:
        return super().execute(
            wallet,
            nonce=nonce,
            value=value,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            use_access_list=use_access_list,
            sync=self.SYNC,
        )
