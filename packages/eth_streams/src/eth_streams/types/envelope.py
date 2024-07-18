from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    sender: str
    message: T

    def __str__(self):
        return f"<Envelope sender={self.sender} message={self.message}>"

    __repr__ = __str__
