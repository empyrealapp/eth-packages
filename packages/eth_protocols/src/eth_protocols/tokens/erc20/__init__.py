from copy import deepcopy
from typing import Annotated, ClassVar, Generic, cast

from eth_rpc import get_current_network
from eth_rpc.types import BLOCK_STRINGS, MaybeAwaitable, Network, primitives
from eth_rpc.utils import to_checksum
from eth_typeshed import ERC20 as ERC20Contract
from eth_typeshed.erc20 import OwnerRequest, OwnerSpenderRequest
from eth_typing import ChecksumAddress, HexAddress
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, WrapValidator
from typing_extensions import TypeVar

from .events import TransferEvents

NetworkType = TypeVar("NetworkType", bound=Network | None, default=None)


class ERC20(BaseModel, Generic[NetworkType]):
    model_config = ConfigDict(frozen=True)
    _network: ClassVar[Network | None] = None

    tokens: ClassVar[dict[tuple[Network, ChecksumAddress], "ERC20"]] = {}
    events: TransferEvents = Field(default_factory=TransferEvents)

    address: Annotated[
        ChecksumAddress, WrapValidator(lambda addr, y, z: to_checksum(addr))
    ]
    network: Network = Field(default_factory=get_current_network)

    _contract: ERC20Contract = PrivateAttr()
    _decimals: primitives.uint256 | None = PrivateAttr(None)
    _name: primitives.string | None = PrivateAttr(None)
    _symbol: primitives.string | None = PrivateAttr(None)

    def __class_getitem__(cls, network: Network):
        cls._network = network
        return cls

    @property
    def sync(self) -> "ERC20Sync":
        obj = deepcopy(self)
        obj.__class__ = ERC20Sync
        obj = cast(ERC20Sync, obj)
        return obj

    @property
    def raw(self) -> ERC20Contract:
        return self._contract

    @classmethod
    def get_network(cls, network: Network | None) -> Network:
        return network or cls._network or get_current_network()

    @classmethod
    def load(cls, address: HexAddress, network: Network | None = None):
        checksum_address = to_checksum(address)

        network = cls.get_network(network)
        key = (network, checksum_address)
        if key not in cls.tokens:
            cls.tokens[key] = cls(address=checksum_address, network=network)

        # unset the network on the class instance
        cls._network = None
        return cls.tokens[key]

    def model_post_init(self, __context):
        self._contract = ERC20Contract(address=self.address)
        self.events.set_address(self.address)

    def set_decimals(self, decimals: int):
        if not decimals:
            return
        self._decimals = decimals

    def set_symbol(self, symbol: int):
        if not symbol:
            return
        self._symbol = symbol

    async def decimals(self) -> primitives.uint256:
        if not self._decimals:
            self._decimals = await self._contract.decimals().get()
        assert self._decimals
        return self._decimals

    async def name(self) -> primitives.string:
        if not self._name:
            self._name = await self._contract.name().get()
        assert self._name
        return self._name

    async def symbol(self) -> primitives.string:
        if not self._symbol:
            self._symbol = await self._contract.symbol().get()
        assert self._symbol
        return self._symbol

    def total_supply(
        self,
        block_number: int | BLOCK_STRINGS = "latest",
        sync: bool = False,
    ) -> MaybeAwaitable[primitives.uint256]:
        return self._contract.total_supply().get(
            block_number=block_number,
            sync=sync,
        )

    def balance_of(
        self,
        owner: HexAddress,
        block_number: int | BLOCK_STRINGS = "latest",
        sync: bool = False,
    ) -> MaybeAwaitable[int]:
        return self._contract.balance_of(OwnerRequest(owner=owner)).get(
            block_number=block_number,
            sync=sync,
        )

    def allowance(
        self,
        owner: HexAddress,
        spender: HexAddress,
        block_number: int | BLOCK_STRINGS = "latest",
        sync: bool = False,
    ) -> MaybeAwaitable[int]:
        return self._contract.allowance(
            OwnerSpenderRequest(owner=owner, spender=spender)
        ).get(block_number=block_number, sync=sync)

    def __repr__(self):
        return f"<ERC20 address={self.address}>"

    def __lt__(self, other: "ERC20" | HexAddress) -> bool:
        if isinstance(other, ERC20):
            return self.address < other.address
        return self.address < other

    def __gt__(self, other: "ERC20" | HexAddress) -> bool:
        if isinstance(other, ERC20):
            return self.address > other.address
        return self.address > other


class ERC20Sync(ERC20):
    def decimals(self) -> int:  # type: ignore
        if not self._decimals:
            self._decimals = self._contract.decimals().get(sync=True)
        assert self._decimals
        return self._decimals

    def name(self) -> str:  # type: ignore
        if not self._name:
            self._name = self._contract.name().get(sync=True)
        assert self._name
        return self._name

    def symbol(self) -> str:  # type: ignore
        if not self._symbol:
            self._symbol = self._contract.symbol().get(sync=True)
        assert self._symbol
        return self._symbol

    def total_supply(self, block_number: int | BLOCK_STRINGS = "latest") -> int:  # type: ignore
        return self._contract.total_supply().get(block_number=block_number, sync=True)

    def balance_of(  # type: ignore
        self,
        owner: HexAddress,
        block_number: int | BLOCK_STRINGS = "latest",
    ) -> int:
        return self._contract.balance_of(OwnerRequest(owner=owner)).get(
            block_number=block_number,
            sync=True,
        )

    def allowance(  # type: ignore
        self,
        owner: HexAddress,
        spender: HexAddress,
        block_number: int | BLOCK_STRINGS = "latest",
    ) -> int:
        return self._contract.allowance(
            OwnerSpenderRequest(owner=owner, spender=spender)
        ).get(
            block_number=block_number,
            sync=True,
        )

    def __lt__(self, other: "ERC20" | HexAddress) -> bool:
        if isinstance(other, ERC20):
            return self.address < other.address
        return self.address < other

    def __gt__(self, other: "ERC20" | HexAddress) -> bool:
        if isinstance(other, ERC20):
            return self.address > other.address
        return self.address > other
