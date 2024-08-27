from pydantic._internal._model_construction import ModelMetaclass
from typing_extensions import TypeVar

T = TypeVar("T")


class IndexableKlass(ModelMetaclass):
    def __getitem__(self: type[T], item) -> type[T]:
        return self
