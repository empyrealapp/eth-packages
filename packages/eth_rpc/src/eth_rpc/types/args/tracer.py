from typing import Any, Literal

from pydantic import BaseModel

from .eth_call import CallWithBlockArgs


class TracerConfig(BaseModel):
    tracer: Literal["callTracer", "prestateTracer"] = "prestateTracer"
    only_top_call: bool | None = None

    def model_dump(self, exclude_none=True, **kwargs) -> dict[str, Any]:
        return super().model_dump(exclude_none=exclude_none, **kwargs)


class TraceArgs(CallWithBlockArgs):
    tracer_config: TracerConfig | None = TracerConfig()
