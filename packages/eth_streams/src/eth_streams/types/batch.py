from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Batch(BaseModel, Generic[T]):
    data: list[T] = Field(default_factory=list)

    def append(self, item: T):
        self.data.append(item)

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for item in self.data:
            yield item

    def __str__(self):
        return f"<Batch size={len(self.data)}>"

    __repr__ = __str__
