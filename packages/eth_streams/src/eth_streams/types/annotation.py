from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class AnnotatedData(BaseModel, Generic[T]):
    message: T
    annotations: list = Field(default_factory=list)

    def annotate(self, value):
        self.annotations.append(value)
