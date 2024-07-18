from typing import Any

from eth_streams.coordinator import CoordinatorContext


def get_implicit(name: str, default: Any = None):
    return CoordinatorContext.implicits.get(name, default)
