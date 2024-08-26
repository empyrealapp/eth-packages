from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, PrivateAttr
from pydantic.alias_generators import to_camel

from ..types import Network as NetworkType
from .datetime import convert_datetime_to_iso_8601


class RPCModel(BaseModel):
    _metadata: dict[str, Any] = PrivateAttr(default_factory=dict)
    _network: Optional[NetworkType] = PrivateAttr(default=None)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        json_encoders={
            datetime: lambda v: convert_datetime_to_iso_8601(v),
        },
    )

    def set_network(self, network: NetworkType | None):
        self._network = network
