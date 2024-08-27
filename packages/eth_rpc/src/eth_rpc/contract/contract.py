from collections.abc import Awaitable
from copy import deepcopy
from typing import (
    TYPE_CHECKING,
    Annotated,
    ClassVar,
    Literal,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from eth_hash.auto import keccak as keccak_256
from eth_rpc.types import (
    BLOCK_STRINGS,
    ContractMethod,
    GetCodeArgs,
    GetStorageArgs,
    HexInteger,
    MaybeAwaitable,
)
from eth_typing import HexAddress, HexStr, Primitives
from pydantic import BaseModel, Field

from .._request import Request
from ..utils import run, to_hex_str
from .function import ContractFunc
from .interface import ContractT

if TYPE_CHECKING:
    from .function import FuncSignature


T = TypeVar(
    "T",
    bound=tuple
    | BaseModel
    | Primitives
    | list[Primitives]
    | tuple[Primitives, ...]
    | HexAddress,
)
U = TypeVar("U")


class Contract(ContractT, Request):
    _func_sigs: ClassVar[dict[str, ContractMethod]]
    functions: list[ContractFunc] = Field(default_factory=list)

    @property
    def sync(self) -> "ContractSync":
        obj = deepcopy(self)
        obj.__class__ = ContractSync
        return obj  # type: ignore

    @classmethod
    def __get_parent_func_sigs(cls) -> dict[str, ContractMethod]:
        func_sigs: dict[str, ContractMethod] = {}
        for klass in cls.__mro__:
            if issubclass(klass, Contract):
                try:
                    func_sigs |= klass._func_sigs
                except AttributeError:
                    pass
        return func_sigs

    def __init_subclass__(cls, **kwargs) -> None:
        # TODO: I hate this slightly less
        del_keys = []

        cls_annotations = get_type_hints(cls, include_extras=True)
        annotations = {
            key: cls_annotations[key]
            for key in (cls_annotations.keys() - get_type_hints(Contract).keys())
        }
        cls._func_sigs = cls.__get_parent_func_sigs()

        for key, annotation in annotations.items():
            if key.startswith("_"):  # exclude protected/private attributes
                continue
            if get_origin(annotation) is Annotated:
                annotation_args = get_args(annotation)
                for annotation in annotation_args:
                    if (
                        annotation is ContractMethod
                        or get_origin(annotation) is ContractFunc
                    ):
                        cls._func_sigs[key] = cls_annotations[key]
                        del_keys.append(key)
                        break
            elif get_origin(annotation) is ContractFunc:
                cls._func_sigs[key] = cls_annotations[key]
                del_keys.append(key)
        for key in del_keys:
            del cls.__annotations__[key]

    def add_func(self, func: "FuncSignature"):
        if func not in self.functions:
            self.functions.append(ContractFunc(func=func, contract=self))

    async def _get_storage_at(
        self, slot: int | HexStr, block_number="latest", sync: bool = False
    ):
        if sync:
            return self.rpc().get_storage_at.sync(
                GetStorageArgs(
                    storage_address=self.address,
                    slot_position=to_hex_str(slot),
                    block_number=block_number,
                )
            )
        return await self.rpc().get_storage_at(
            GetStorageArgs(
                storage_address=self.address,
                slot_position=to_hex_str(slot),
                block_number=block_number,
            )
        )

    @overload
    def get_storage_at(
        self, *, sync: Literal[True], slot: int | HexStr, block_number="latest"
    ) -> HexStr: ...

    @overload
    def get_storage_at(
        self, *, slot: int | HexStr, block_number="latest"
    ) -> Awaitable[HexStr]: ...

    def get_storage_at(
        self, *, slot: int | HexStr, block_number="latest", sync: bool = False
    ) -> MaybeAwaitable[HexStr]:
        return run(
            self._get_storage_at,
            slot=slot,
            block_number=block_number,
            sync=sync,
        )

    async def _get_code(
        self,
        block_number: int | BLOCK_STRINGS | None = None,
        block_hash: HexStr | None = None,
        sync: bool = False,
    ) -> HexStr:
        if block_hash:
            if sync:
                return self.rpc().get_code.sync(
                    GetCodeArgs(
                        address=self.address,
                        block_hash=block_hash,
                    )
                )
            return await self.rpc().get_code(
                GetCodeArgs(
                    address=self.address,
                    block_hash=block_hash,
                )
            )

        if block_number is None:
            block_number = "latest"
        if sync:
            return self.rpc().get_code.sync(
                GetCodeArgs(
                    address=self.address,
                    block_number=(
                        HexInteger(block_number)
                        if isinstance(block_number, int)
                        else block_number
                    ),
                )
            )
        return await self.rpc().get_code(
            GetCodeArgs(
                address=self.address,
                block_number=(
                    HexInteger(block_number)
                    if isinstance(block_number, int)
                    else block_number
                ),
            )
        )

    @overload
    def get_code(
        self,
        *,
        sync: Literal[True],
        block_number: int | BLOCK_STRINGS | None = None,
        block_hash: HexStr | None = None,
    ) -> HexStr: ...

    @overload
    def get_code(
        self,
        *,
        block_number: int | BLOCK_STRINGS | None = None,
        block_hash: HexStr | None = None,
    ) -> Awaitable[HexStr]: ...

    def get_code(
        self,
        *,
        block_number: int | BLOCK_STRINGS | None = None,
        block_hash: HexStr | None = None,
        sync: bool = False,
    ) -> MaybeAwaitable[HexStr]:
        return run(
            self._get_code,
            block_number=block_number,
            block_hash=block_hash,
            sync=sync,
        )

    def create2(self, salt: bytes, keccak_init_code: bytes) -> HexAddress:
        """
        EIP-104
        https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1014.md
        """
        pre = "0xff"
        b_pre = bytes.fromhex(pre[2:])
        b_address = bytes.fromhex(self.address[2:])

        b_result = keccak_256(b_pre + b_address + salt + keccak_init_code)
        result_address = "0x" + b_result[12:].hex()

        return HexAddress(HexStr(result_address))


class ContractSync(Contract):
    SYNC: ClassVar[Literal[True]] = True

    def get_storage_at(  # type: ignore
        self,
        *,
        slot: int | HexStr,
        block_number="latest",
    ) -> HexStr:
        return super().get_storage_at(
            slot=slot,
            block_number=block_number,
            sync=self.SYNC,
        )

    def get_code(  # type: ignore
        self,
        *,
        block_number: int | BLOCK_STRINGS | None = None,
        block_hash: HexStr | None = None,
    ) -> HexStr:
        return super().get_code(
            block_number=block_number, block_hash=block_hash, sync=self.SYNC
        )
