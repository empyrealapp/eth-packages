from abc import abstractmethod

from ..coordinator import Coordinator
from .base import Base


class Task(Base):
    def model_post_init(self, __context):
        if self.coordinator:
            self.coordinator.add_task(self)

    @abstractmethod
    async def run(self) -> None: ...

    def set_coordinator(self, coordinator: "Coordinator"):
        self.coordinator = coordinator

    async def on_close(self) -> None:
        """Optional cleanup method"""
        return None
