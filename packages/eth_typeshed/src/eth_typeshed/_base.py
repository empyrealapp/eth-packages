from typing import Optional, get_args

from eth_rpc import Contract, ContractFunc, FuncSignature
from eth_rpc.types import Name
from eth_rpc.utils import is_annotation
from eth_typing import HexAddress, HexStr


class ProtocolBase(Contract):
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
