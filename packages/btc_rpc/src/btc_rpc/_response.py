from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class RPCResponse(BaseModel, Generic[T]):
    id: int
    result: T
    error: str | None
