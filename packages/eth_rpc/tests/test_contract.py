import os
from typing import Annotated

import pytest
from eth_rpc import ContractFunc, FuncSignature, set_alchemy_key
from eth_rpc.contract.base import ProtocolBase
from eth_rpc.networks import Arbitrum, Ethereum
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from eth_typing import HexAddress, HexStr


class Token(ProtocolBase):
    name: ContractFunc[
        NoArgs,
        Annotated[primitives.string, Name("_name")],
    ] = METHOD


@pytest.mark.contract
@pytest.mark.unit
def test_encode_signature():
    func = FuncSignature[NoArgs, primitives.string](name="name")
    assert func.encode_call(inputs=()) == "0x06fdde03"


@pytest.mark.unit
def test_set_network():
    usdt = Token[Ethereum](
        address=HexAddress(HexStr("0xdAC17F958D2ee523a2206206994597C13D831ec7"))
    )
    assert usdt._network == Ethereum

    usdc = Token[Arbitrum](address="0xaf88d065e77c8cc2239327c5edb3a432268e5831")
    assert usdc._network == Arbitrum

    # test that this didn't affect the usdt network
    assert usdt._network == Ethereum


@pytest.mark.asyncio(scope="session")
@pytest.mark.contract
async def test_contract() -> None:
    set_alchemy_key(os.environ["ALCHEMY_KEY"])

    usdt = Token[Ethereum](
        address=HexAddress(HexStr("0xdAC17F958D2ee523a2206206994597C13D831ec7"))
    )
    usdc = Token[Arbitrum](address="0xaf88d065e77c8cc2239327c5edb3a432268e5831")

    assert await usdt.name().get() == "Tether USD"
    assert await usdc.name().get() == "USD Coin"
