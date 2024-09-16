from abc import ABC, abstractmethod
from decimal import Decimal
from functools import cached_property
from typing import Annotated, Any, ClassVar, Generic, Optional, cast

from eth_protocols.tokens import ERC20
from eth_rpc import ProtocolBase, get_current_network
from eth_rpc.types import BLOCK_STRINGS, MaybeAwaitable, Network
from eth_rpc.utils import to_checksum
from eth_typing import ChecksumAddress, HexAddress
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    PrivateAttr,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    computed_field,
)
from pydantic.functional_validators import WrapValidator
from typing_extensions import Self, TypeVar

NetworkType = TypeVar("NetworkType", bound=Network | None, default=None)


def load_token(
    v: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
) -> ERC20:
    if isinstance(v, ERC20):
        return v
    return ERC20.load(address=v)


class DexPair(ABC, BaseModel, Generic[NetworkType]):
    model_config = ConfigDict(frozen=True)
    _network: ClassVar[Network | None] = None
    pairs: ClassVar[dict[tuple[Network, ChecksumAddress], "DexPair"]] = {}

    pair_address: Annotated[
        ChecksumAddress, WrapValidator(lambda addr, y, z: to_checksum(addr))
    ]
    token0: Annotated[ERC20, WrapValidator(load_token)]
    token1: Annotated[ERC20, WrapValidator(load_token)]
    network: Network = Field(default_factory=get_current_network)

    _contract: ProtocolBase
    _reserve0: Optional[int] = PrivateAttr(None)
    _reserve1: Optional[int] = PrivateAttr(None)

    def __class_getitem__(cls, network: Network):
        cls._network = network
        return cls

    @classmethod
    def load(cls, pair: HexAddress | Self, **kwargs):
        if isinstance(pair, DexPair):
            return pair
        pair = cast(HexAddress, pair)
        checksum_address = to_checksum(pair)
        network = cls._network or get_current_network()
        key = (network, checksum_address)
        if key not in cls.pairs:
            cls.pairs[key] = cls[network].load_pair(pair_address=checksum_address)  # type: ignore
        # unset the network on the class instance
        cls._network = None
        return cls.pairs[key]

    @classmethod
    def load_pair(
        cls,
        pair_address: HexAddress,
    ): ...

    @property
    def address(self) -> ChecksumAddress:
        return self.pair_address

    async def reserves(self):
        return Decimal(self._reserve0 / 10**self.decimals0), Decimal(
            self._reserve1 / 10**self.decimals1
        )

    def get_reserve(self, token: HexAddress) -> Decimal:
        token = to_checksum(token)
        if self._reserve0 is None and self._reserve1 is None:
            raise ValueError("Must set reserves first")
        if token == self.token0.address:
            return Decimal(self._reserve0 / 10**self.decimals0)
        if token == self.token1.address:
            return Decimal(self._reserve1 / 10**self.decimals1)
        return Decimal(0)

    def set_reserves(self, reserve0: int, reserve1: int):
        self._reserve0 = reserve0
        self._reserve1 = reserve1

    @abstractmethod
    async def get_price(
        self, token: HexAddress, block_number: Optional[int | BLOCK_STRINGS] = None
    ) -> Decimal: ...

    @abstractmethod
    def get_reserves(
        self, block_number: int | BLOCK_STRINGS = "latest", sync: bool = False
    ) -> MaybeAwaitable[tuple[int, int]]: ...

    @computed_field  # type: ignore[misc]
    @property
    def flipped(self) -> bool:
        return self.token0.address < self.token1.address

    @cached_property
    def decimals0(self):
        return self.token0.sync.decimals()

    @cached_property
    def decimals1(self):
        return self.token1.sync.decimals()

    async def load_decimals(self):
        await self.token0.decimals()
        await self.token1.decimals()
