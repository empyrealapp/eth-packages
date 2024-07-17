from collections.abc import Generator
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from eth_typing import HexAddress, HexStr, Primitives
from pydantic import BaseModel

from ..function import FuncSignature

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


@dataclass
class EthResponse(Generic[T, U]):
    func: FuncSignature[T, U]
    result: HexStr

    @property
    def raw(self):
        return self.result

    def decode(self) -> U:
        return self.func.decode_result(self.result)

    def as_dict(self, **kwargs) -> dict[str, Any]:
        decoded_result = self.func.decode_result(self.result)
        # NOTE: tuple is redundant here
        if isinstance(decoded_result, tuple):
            return dict(
                zip(
                    [
                        (output_name or str(idx))
                        for idx, output_name in enumerate(self.func.get_output_name())
                    ],
                    decoded_result,
                )
            )
        elif isinstance(decoded_result, BaseModel):
            return decoded_result.model_dump(**kwargs)
        return {self.func.get_output_name()[0]: decoded_result}

    def __await__(self) -> "Generator[Any, None, EthResponse[T, U]]":
        async def foo():
            return self

        return foo().__await__()
