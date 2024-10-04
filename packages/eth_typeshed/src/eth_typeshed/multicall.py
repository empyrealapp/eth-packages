from collections.abc import Awaitable
from typing import Annotated, Any, Generic, Literal, TypeVar, overload

from eth_abi.exceptions import InsufficientDataBytes
from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import (
    BLOCK_STRINGS,
    METHOD,
    MaybeAwaitable,
    Name,
    Struct,
    primitives,
)
from eth_rpc.utils import handle_maybe_awaitable, run
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel, Field

T = TypeVar("T", bound=tuple[Any])
U = TypeVar("U")

MULTICALL3_ADDRESS = HexAddress(HexStr("0xcA11bde05977b3631167028862bE2a173976CA11"))


class Result(Struct):
    success: bool
    return_data: bytes


class TryMulticallRequest(BaseModel):
    require_success: Annotated[bool, Name("requireSuccess")]
    calls: list[tuple[primitives.address, primitives.bytes]]


class MulticallRequest(BaseModel):
    calls: list[tuple[primitives.address, primitives.bytes]]


class TryAggregateResponse(BaseModel):
    results: list[Result]


class TryMulticallResponse(BaseModel):
    block_number: Annotated[primitives.uint256, Name("blockNumber")]
    block_hash: Annotated[primitives.bytes32, Name("blockHash")]
    return_data: Annotated[
        list[tuple[primitives.bool, primitives.bytes]], Name("returnData")
    ]


class TryResult(BaseModel, Generic[T]):
    success: bool
    result: T | Any


class Multicall(ProtocolBase):
    address: HexAddress = Field(default=MULTICALL3_ADDRESS)
    block_and_aggregate: Annotated[
        ContractFunc[
            MulticallRequest,
            TryMulticallResponse,
        ],
        Name("blockAndAggregate"),
    ] = METHOD
    try_aggregate: Annotated[
        ContractFunc[
            TryMulticallRequest,
            TryAggregateResponse,
        ],
        Name("tryAggregate"),
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
        call = await self.try_aggregate(
            TryMulticallRequest(
                require_success=require_success,
                calls=[(c.address, c.encode()) for c in calls],
            )
        ).call(sync=sync, block_number=block_number)

        return_data = call.decode()

        response: list[TryResult] = []

        for result, func in zip(return_data.results, calls):
            if result.success:
                try:
                    response.append(
                        TryResult(success=True, result=func.decode(result.return_data))
                    )
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
