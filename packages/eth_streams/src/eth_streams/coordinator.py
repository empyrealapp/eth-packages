import asyncio
from collections import deque
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr
from tortoise import Tortoise

if TYPE_CHECKING:
    from .types import Callback, Sink, Task


class Coordinator(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    callbacks: dict[str, "Callback"] = Field(default_factory=dict)
    tasks: dict[str, "Task"] = Field(default_factory=dict)
    sinks: dict[str, "Sink"] = Field(default_factory=dict)
    concurrency: int = Field(default=10)
    _semaphore: asyncio.Semaphore = PrivateAttr()

    def model_post_init(self, __context):
        self._semaphore = asyncio.Semaphore(self.concurrency)

    @property
    def semaphore(self):
        return self._semaphore

    def add_task(self, task: "Task"):
        if task.name in self.tasks:
            raise NameError("task already exists")
        self.tasks[task.name] = task

    def add_sink(self, sink: "Sink"):
        if sink.name in self.sinks:
            if self.sinks[sink.name] != sink:
                raise NameError(f"Sink already exists: {sink.name}")
        self.sinks[sink.name] = sink

    def load_callbacks(self):
        print("Loading all the strategies")

    def load_callback(self, callback: "Callback"):
        if callback.name in self.callbacks:
            raise NameError("Callback already exists")
        self.callbacks[callback.name] = callback

    def on_safe_shutdown(self):
        # TODO: callbacks are not used yet
        for callback in self.callbacks.values():
            asyncio.create_task(callback.shutdown(self.semaphore))

    @property
    def completed(self):
        return all([c.stopped for c in self.sinks.values()])

    async def run(self):
        tasks = []

        for task in self.tasks.values():
            tasks.append(asyncio.create_task(task.run()))
        await asyncio.gather(*tasks)

    async def close(self):
        await Tortoise.close_connections()

    def __enter__(self):
        CoordinatorContext.push_context_managed_coordinator(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        CoordinatorContext.push_context_managed_coordinator(self)


class CoordinatorContext:
    _context_managed_coordinators: deque[Coordinator] = deque()
    implicits: dict[str, Any] = {}

    @classmethod
    def set_implicits(cls, **kwargs):
        cls.implicits.update(kwargs)

    @classmethod
    def clear_implicits(cls):
        cls.implicits = {}

    @classmethod
    def push_context_managed_coordinator(cls, dag: Coordinator):
        cls._context_managed_coordinators.appendleft(dag)

    @classmethod
    def pop_context_managed_coordinator(cls) -> Coordinator | None:
        dag = cls._context_managed_coordinators.popleft()
        return dag

    @classmethod
    def get_current_coordinator(cls) -> Coordinator | None:
        try:
            return cls._context_managed_coordinators[0]
        except IndexError:
            return None
