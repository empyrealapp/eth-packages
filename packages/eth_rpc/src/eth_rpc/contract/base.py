from typing import TYPE_CHECKING, Optional, get_args

from eth_rpc import Contract, ContractFunc, FuncSignature
from eth_rpc.types import Name
from eth_rpc.utils import is_annotation
from eth_typing import HexAddress, HexStr
from pydantic import ConfigDict


class _ProtocolBase(Contract):
    model_config = ConfigDict(extra="allow")

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

            setattr(
                self,
                alias,
                ContractFunc[T, U](  # type: ignore
                    func=FuncSignature[T, U](name=name, alias=alias),  # type: ignore
                    contract=self,
                ),
            )


if TYPE_CHECKING:
    # This is because type checkers don't like when you use __class_getitem__ outside of a generic
    # By adding a metaclass with a getitem, it plays much nicer with mypy.
    from pydantic._internal._model_construction import ModelMetaclass

    class IndexedKlass(ModelMetaclass):
        def __getitem__(self, item):
            return self

    class ProtocolBase(_ProtocolBase, metaclass=IndexedKlass):
        pass

else:
    ProtocolBase = _ProtocolBase
