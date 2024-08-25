from typing import TYPE_CHECKING, Optional, get_args

from eth_rpc import Contract, ContractFunc, FuncSignature
from eth_rpc.types import Name
from eth_rpc.utils import is_annotation
from eth_typing import HexAddress, HexStr
from typing_extensions import Self


class _ProtocolBase(Contract):
    def __init__(self, address: HexAddress, code_override: Optional[HexStr] = None):
        super().__init__(address=address, code_override=code_override)
        for alias, func in self._func_sigs.items():
            name = alias
            if is_annotation(func):
                annotation_args = get_args(func)
                args = annotation_args[0]
                for annotation in annotation_args:
                    if isinstance(annotation, Name):
                        name = annotation.value
            else:
                args = func
            T, U = get_args(args)

            self.functions.append(
                ContractFunc[T, U](  # type: ignore
                    func=FuncSignature[T, U](name=name, alias=alias),  # type: ignore
                    contract=self,
                )
            )


if TYPE_CHECKING:
    from pydantic._internal._model_construction import ModelMetaclass

    class Indexed(ModelMetaclass):
        def __getitem__(self, item):
            return self

    class ProtocolBase(Contract, metaclass=Indexed):
        def __class_getitem__(cls, params) -> type["Self"]:
            return cls

        def __getitem__(cls, params) -> "Self":
            return cls

else:
    ProtocolBase = _ProtocolBase
