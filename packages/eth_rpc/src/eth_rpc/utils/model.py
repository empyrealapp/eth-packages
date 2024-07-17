from datetime import datetime
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, ConfigDict, PrivateAttr
from pydantic.alias_generators import to_camel

from .._transport import _force_get_default_network
from ..types import Network as NetworkType
from .datetime import convert_datetime_to_iso_8601


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class RPCModel(BaseModel):
    _metadata: dict[str, Any] = PrivateAttr(default_factory=dict)
    _network: ClassVar[NetworkType | None] = PrivateAttr(None)
    __network: Optional[NetworkType] = PrivateAttr(default=None)

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        json_encoders={
            datetime: lambda v: convert_datetime_to_iso_8601(v),
        },
    )

    @property
    def network(self) -> NetworkType:  # noqa: F811
        network = self.__network or self._network
        if not network:
            return _force_get_default_network()
        return network

    def __class_getitem__(cls, params):
        if isinstance(params, NetworkType):
            cls._network = params
        return cls

    def set_network(self, network: NetworkType | None):
        self.__network = network
