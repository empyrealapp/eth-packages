from typing import ClassVar

from eth_rpc import get_current_network
from eth_rpc.types import Network
from eth_rpc.utils import to_checksum
from eth_typeshed.uniswap_v2 import GetPairRequest, UniswapV2Factory
from eth_typing import ChecksumAddress, HexAddress
from pydantic import BaseModel, Field, PrivateAttr

from .pair import V2Pair


class V2Factory(BaseModel):
    pairs: ClassVar[
        dict[tuple[Network, ChecksumAddress, ChecksumAddress], "ChecksumAddress"]
    ] = Field({})
    _network: ClassVar[Network | None] = None

    _contract: UniswapV2Factory = PrivateAttr()
    address: HexAddress

    def __class_getitem__(cls, network: Network):  # type: ignore
        cls._network = network
        return cls

    def model_post_init(self, __context):
        self._contract = UniswapV2Factory(address=self.address)

    @classmethod
    async def load_pair(cls, token0: HexAddress, token1: HexAddress) -> "V2Pair":
        network: Network = cls._network or get_current_network()
        token0 = to_checksum(token0)
        token1 = to_checksum(token1)
        key = (network, token0, token1)

        if key not in cls.pairs:
            pair_address: HexAddress = await cls._contract.get_pair(
                GetPairRequest(
                    token_a=token0,
                    token_b=token1,
                )
            )
            cls.pairs[key] = to_checksum(pair_address)

        return V2Pair.load(
            pair=cls.pairs[key],
        )
