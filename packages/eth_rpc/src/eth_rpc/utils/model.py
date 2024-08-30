from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, PrivateAttr
from pydantic.alias_generators import to_camel

from ..types import Network


class RPCModel(BaseModel):
    _metadata: dict[str, Any] = PrivateAttr(default_factory=dict)
    _network: Optional[type[Network]] = PrivateAttr(default=None)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    def set_network(self, network: type[Network] | None):
        object.__setattr__(self, "_network", network)
