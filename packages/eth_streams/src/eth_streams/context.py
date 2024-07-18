from abc import ABC
from typing import Any

from pydantic import BaseModel

# TODO: Maintain staged events before commiting them
#       This allows for reorgs to be handled gracefully


class Context(ABC, BaseModel):
    """
    This should store all state changes
    """

    @classmethod
    def load(cls, json_data: str) -> "Context":
        return cls.model_validate_json(json_data)

    def dump(self) -> dict[str, Any]:
        return self.model_dump()
