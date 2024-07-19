from abc import ABC
from typing import Optional

from pydantic import BaseModel, Field, computed_field

from ..coordinator import Coordinator, CoordinatorContext


class Base(ABC, BaseModel):
    coordinator: Optional[Coordinator] = Field(
        default_factory=CoordinatorContext.get_current_coordinator
    )

    @computed_field  # type: ignore
    @property
    def name(self) -> str:
        return self.__class__.__name__
