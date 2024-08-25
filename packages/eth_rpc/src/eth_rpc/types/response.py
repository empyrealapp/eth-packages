from typing import TYPE_CHECKING, Generator, Generic, NewType, Optional, TypeVar

if TYPE_CHECKING:
    from eth_rpc.rpc.method import RPCMethod

# used to indicate methods with no arguments
NoArgs = NewType("NoArgs", tuple[()])

ArgType = TypeVar("ArgType")
ReturnType = TypeVar("ReturnType")


class RPCResponseModel(Generic[ArgType, ReturnType]):
    __slots__ = ["func", "arg"]

    func: "RPCMethod"
    arg: ArgType | NoArgs

    def __init__(self, func: "RPCMethod", arg: Optional[ArgType] = None):
        self.func = func
        self.arg = arg if arg is not None else NoArgs(())

    @property
    def sync(self) -> ReturnType:
        if self.arg:
            return self.func.sync(self.arg)
        response = self.func.sync()
        return response

    def __await__(self) -> Generator[None, None, ReturnType]:
        if self.arg:
            return self.func(self.arg).__await__()
        return self.func().__await__()
