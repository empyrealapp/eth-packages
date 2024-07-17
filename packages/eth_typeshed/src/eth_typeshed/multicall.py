from collections.abc import Awaitable
from typing import Annotated, Any, Generic, Literal, TypeVar, overload

from eth_abi.exceptions import InsufficientDataBytes
from eth_rpc import ContractFunc
from eth_rpc.types import BLOCK_STRINGS, METHOD, MaybeAwaitable, Name, primitives
from eth_rpc.utils import handle_maybe_awaitable, run
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, Field

from ._base import ProtocolBase

T = TypeVar("T", bound=tuple[Any])
U = TypeVar("U")

MULTICALL3_ADDRESS = HexAddress(HexStr("0xcA11bde05977b3631167028862bE2a173976CA11"))


class TryMulticallRequest(BaseModel):
    require_success: Annotated[bool, Name("requireSuccess")]
    calls: list[tuple[primitives.address, primitives.bytes]]


class MulticallRequest(BaseModel):
    calls: list[tuple[primitives.address, primitives.bytes]]


class TryMulticallResponse(BaseModel):
    block_number: Annotated[primitives.uint256, Name("blockNumber")] = Field(
        alias="blockNumber"
    )
    block_hash: Annotated[primitives.bytes32, Name("blockHash")] = Field(
        alias="blockHash"
    )
    return_data: Annotated[
        list[tuple[primitives.bool, primitives.bytes]], Name("returnData")
    ] = Field(alias="returnData")


class TryResult(BaseModel, Generic[T]):
    success: bool
    result: T | Any


class Multicall(ProtocolBase):
    block_and_aggregate: Annotated[
        ContractFunc[
            MulticallRequest,
            TryMulticallResponse,
        ],
        Name("blockAndAggregate"),
    ] = METHOD
    try_block_and_aggregate: Annotated[
        ContractFunc[
            TryMulticallRequest,
            TryMulticallResponse,
        ],
        Name("tryBlockAndAggregate"),
    ] = METHOD

    async def _execute(
        self,
        *calls: ContractFunc,
        sync: bool = False,
        block_number: int | BLOCK_STRINGS = "latest",
    ) -> list[Any]:
        results = await handle_maybe_awaitable(
            self.try_execute(
                *calls, require_success=True, block_number=block_number, sync=sync
            )
        )
        return [r.result for r in results]

    @overload
    def execute(
        self,
        *calls: ContractFunc,
        sync: Literal[False],
        block_number: int | BLOCK_STRINGS = ...,
    ) -> list[Any]: ...

    @overload
    def execute(
        self,
        *calls: ContractFunc,
        sync: Literal[True],
        block_number: int | BLOCK_STRINGS = ...,
    ) -> Awaitable[list[Any]]: ...

    @overload
    def execute(
        self,
        *calls: ContractFunc,
        block_number: int | BLOCK_STRINGS = ...,
    ) -> Awaitable[list[Any]]: ...

    def execute(
        self,
        *calls: ContractFunc,
        block_number: int | BLOCK_STRINGS = "latest",
        sync: bool = False,
    ) -> MaybeAwaitable[list[Any]]:
        return run(self._execute, *calls, block_number=block_number, sync=sync)

    async def _try_execute(
        self,
        *calls: ContractFunc,
        require_success: bool = False,
        sync: bool = False,
        block_number: int | BLOCK_STRINGS = "latest",
    ) -> list[TryResult]:

        call = await self.try_block_and_aggregate(
            TryMulticallRequest(
                require_success=require_success,
                calls=[(c.address, c.encode()) for c in calls],
            )
        ).call(sync=sync, block_number=block_number)

        if call.result != "0x":
            return_data = call.decode().return_data
        else:
            return_data = call.result

        response: list[TryResult] = []
        for (success, result), func in zip(return_data, calls):
            if success:
                try:
                    response.append(TryResult(success=True, result=func.decode(result)))
                except (OverflowError, InsufficientDataBytes):
                    response.append(TryResult(success=False, result=None))
            else:
                response.append(TryResult(success=False, result=None))
        return response

    @overload
    def try_execute(
        self,
        *calls: ContractFunc,
        sync: Literal[True],
        require_success: bool = ...,
        block_number: int | BLOCK_STRINGS = ...,
    ) -> list[TryResult]: ...

    @overload
    def try_execute(
        self,
        *calls: ContractFunc,
        require_success: bool = ...,
        block_number: int | BLOCK_STRINGS = ...,
    ) -> Awaitable[list[TryResult]]: ...

    @overload
    def try_execute(
        self,
        *calls: ContractFunc,
        require_success: bool = ...,
        sync: bool = ...,
        block_number: int | BLOCK_STRINGS = ...,
    ) -> MaybeAwaitable[list[TryResult]]: ...

    def try_execute(
        self,
        *calls: ContractFunc,
        require_success: bool = False,
        sync: bool = False,
        block_number: int | BLOCK_STRINGS = "latest",
    ) -> MaybeAwaitable[list[TryResult]]:
        return run(
            self._try_execute,
            *calls,
            require_success=require_success,
            sync=sync,
            block_number=block_number,
        )


multicall = Multicall(address=MULTICALL3_ADDRESS)
