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
from ..delegation import sponsor_delegation
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
        value: int = 0,
    ) -> HexInteger:
        query: RPCResponseModel[CallWithBlockArgs, HexInteger] = RPCResponseModel(
            self._rpc().estimate_gas,
            CallWithBlockArgs(
                params=EthCallParams(
                    from_=from_,
                    to=self.address,
                    data=self.data,
                    value=value,
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
        """
        Execute a contract call and return the decoded result directly.

        This is a convenience method that combines call() and decode() into
        a single operation, making it easier to get typed return values from
        contract functions.

        Equivalent to: (await contract.method().call()).decode()

        Args:
            from_: Address to simulate the call from (affects msg.sender)
            block_number: Block number or tag to execute the call at
            value: ETH value to send with the call (in wei)
            state_diff: State overrides for simulation (advanced usage)
            sync: Whether to execute synchronously

        Returns:
            Decoded return value with proper typing

        Example:
            ```python
            balance: int = await token.balance_of(user_address).get()

            reserves: tuple[int, int] = await pair.get_reserves().get()
            reserve0, reserve1 = reserves

            old_balance = await token.balance_of(user).get(block_number=17000000)
            ```
        """
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
        rpc = self._rpc()
        if sync:
            chain_id = rpc.chain_id.sync()
        else:
            chain_id = await rpc.chain_id()

        if not (max_fee_per_gas or gas_price):
            if sync:
                max_priority_fee_per_gas = (
                    max_priority_fee_per_gas or rpc.max_priority_fee_per_gas.sync()
                )
                # TODO: get block with default network if not set in contract
                base_fee_per_gas = Block[rpc.network].pending().sync.base_fee_per_gas  # type: ignore[name-defined]
            else:
                max_priority_fee_per_gas = (
                    max_priority_fee_per_gas or await rpc.max_priority_fee_per_gas()
                )

                # TODO: fix pending()
                block = await Block[rpc.network].pending()  # type: ignore[name-defined]
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
                nonce=nonce or wallet[rpc.network].get_nonce().sync,
                value=value,
                access_list=access_list,
                chain_id=chain_id,
                type=1 if bool(gas_price) else 2,
            )
        return PreparedTransaction(
            data=self.data,
            to=self.address,
            gas=HexInteger(gas),
            gas_price=gas_price,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            nonce=nonce or await wallet[rpc.network].get_nonce(),
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
        delegate_wallet: Optional["BaseWallet"] = None,
        chain_id: Optional[int] = None,
        gas: Optional[int] = None,
        sync: bool = True,
    ) -> HexStr:
        """
        Execute a contract function as a blockchain transaction.

        This method handles the complete transaction lifecycle:
        1. **Gas Estimation**: Automatically estimates gas requirements
        2. **Fee Calculation**: Determines optimal gas fees (EIP-1559 or legacy)
        3. **Transaction Preparation**: Creates a properly formatted transaction
        4. **Signing**: Signs the transaction with the provided wallet
        5. **Broadcasting**: Submits the transaction to the network

        Args:
            wallet: Wallet to sign and send the transaction
            nonce: Transaction nonce (auto-determined if not provided)
            value: ETH value to send with transaction (in wei)
            gas_price: Legacy gas price (for pre-EIP-1559 transactions)
            max_fee_per_gas: Maximum total fee per gas (EIP-1559)
            max_priority_fee_per_gas: Maximum priority fee per gas (EIP-1559)
            use_access_list: Whether to include an access list for gas optimization
            delegate_wallet: Optional delegate wallet for sponsored transactions
            chain_id: Chain ID override (usually auto-detected)
            gas: Gas limit override (usually auto-estimated)
            sync: Whether to execute synchronously

        Returns:
            Transaction hash of the submitted transaction

        Example:
            ```python
            from eth_rpc.wallet import PrivateKeyWallet

            wallet = PrivateKeyWallet(private_key=os.environ["PRIVATE_KEY"])

            tx_hash = await token.transfer(recipient, amount).execute(wallet)

            tx_hash = await token.approve(spender, amount).execute(
                wallet,
                max_fee_per_gas=50_000_000_000,  # 50 gwei
                max_priority_fee_per_gas=2_000_000_000,  # 2 gwei
            )

            tx = await Transaction[Ethereum].get_by_hash(tx_hash)
            receipt = await tx.wait_for_receipt()
            print(f"Transaction confirmed in block {receipt.block_number}")
            ```

        Note:
            - Gas estimation includes a 25% buffer by default
            - EIP-1559 transactions are used by default on supported networks
            - Access lists can reduce gas costs for complex transactions
            - Sponsored transactions allow gasless execution for end users
        """
        # If delegate_wallet is provided, use sponsored delegation
        if delegate_wallet is not None:
            return await self._execute_sponsored(
                sponsor_wallet=wallet,
                delegate_wallet=delegate_wallet,
                chain_id=chain_id,
                nonce=nonce,
                value=value,
                gas=gas or 100000,
                sync=sync,
            )

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
            return (
                wallet[self._network]
                .send_raw_transaction(HexStr("0x" + signed_tx.raw_transaction))
                .sync
            )
        return await wallet[self._network].send_raw_transaction(
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
        delegate_wallet: Optional["BaseWallet"] = ...,
        chain_id: Optional[int] = ...,
        gas: Optional[int] = ...,
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
        delegate_wallet: Optional["BaseWallet"] = ...,
        chain_id: Optional[int] = ...,
        gas: Optional[int] = ...,
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
        delegate_wallet: Optional["BaseWallet"] = None,
        chain_id: Optional[int] = None,
        gas: Optional[int] = None,
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
            delegate_wallet=delegate_wallet,
            chain_id=chain_id,
            gas=gas,
            sync=sync,
        )

    async def _execute_sponsored(
        self,
        sponsor_wallet: "BaseWallet",
        delegate_wallet: "BaseWallet",
        *,
        chain_id: Optional[int] = None,
        nonce: Optional[int] = None,
        value: int = 0,
        gas: int = 100000,
        sync: bool = False,
    ) -> HexStr:
        sponsored_tx = await sponsor_delegation(
            sponsor_wallet=sponsor_wallet,
            delegate_wallet=delegate_wallet,
            contract_address=self.address,
            chain_id=chain_id,
            nonce=nonce,
            value=value,
            data=self.data,
            gas=gas,
        )
        signed_tx = sponsor_wallet.sign_transaction(sponsored_tx)
        if sync:
            return (
                sponsor_wallet[self._network]
                .send_raw_transaction(HexStr("0x" + signed_tx.raw_transaction))
                .sync
            )
        return await sponsor_wallet[self._network].send_raw_transaction(
            HexStr("0x" + signed_tx.raw_transaction)
        )

    @overload
    def execute_sponsored(
        self,
        sponsor_wallet: "BaseWallet",
        delegate_wallet: "BaseWallet",
        *,
        sync: Literal[True],
        chain_id: Optional[int] = ...,
        nonce: Optional[int] = ...,
        value: int = ...,
        gas: int = ...,
    ) -> HexStr: ...

    @overload
    def execute_sponsored(
        self,
        sponsor_wallet: "BaseWallet",
        delegate_wallet: "BaseWallet",
        *,
        chain_id: Optional[int] = ...,
        nonce: Optional[int] = ...,
        value: int = ...,
        gas: int = ...,
    ) -> Awaitable[HexStr]: ...

    def execute_sponsored(
        self,
        sponsor_wallet: "BaseWallet",
        delegate_wallet: "BaseWallet",
        *,
        chain_id: Optional[int] = None,
        nonce: Optional[int] = None,
        value: int = 0,
        gas: int = 100000,
        sync: bool = False,
    ) -> MaybeAwaitable[HexStr]:
        return run(
            self._execute_sponsored,
            sponsor_wallet,
            delegate_wallet,
            chain_id=chain_id,
            nonce=nonce,
            value=value,
            gas=gas,
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
        delegate_wallet: Optional[BaseWallet] = None,
        chain_id: Optional[int] = None,
        gas: Optional[int] = None,
    ) -> HexStr:
        return super().execute(
            wallet,
            nonce=nonce,
            value=value,
            max_fee_per_gas=max_fee_per_gas,
            max_priority_fee_per_gas=max_priority_fee_per_gas,
            use_access_list=use_access_list,
            delegate_wallet=delegate_wallet,
            chain_id=chain_id,
            gas=gas,
            sync=self.SYNC,
        )

    def execute_sponsored(  # type: ignore
        self,
        sponsor_wallet: BaseWallet,
        delegate_wallet: BaseWallet,
        *,
        chain_id: Optional[int] = None,
        nonce: Optional[int] = None,
        value: int = 0,
        gas: int = 100000,
    ) -> HexStr:
        return super().execute_sponsored(
            sponsor_wallet,
            delegate_wallet,
            chain_id=chain_id,
            nonce=nonce,
            value=value,
            gas=gas,
            sync=self.SYNC,
        )
