import os
from typing import Annotated

import pytest
from eth_rpc import ContractFunc, FuncSignature, set_alchemy_key
from eth_rpc.contract.base import ProtocolBase
from eth_rpc.networks import Arbitrum, Ethereum
from eth_rpc.types import Name, NoArgs, primitives
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel


class AllowanceRequest(BaseModel):
    owner: primitives.address
    spender: primitives.address


class Token(ProtocolBase):
    name: ContractFunc[
        NoArgs,
        Annotated[primitives.string, Name("_name")],
    ]
    balance_of: Annotated[
        ContractFunc[
            primitives.address,
            Annotated[primitives.uint256, Name("_name")],
        ],
        Name("balanceOf"),
    ]
    allowance: ContractFunc[
        tuple[primitives.address, primitives.address],
        primitives.uint256,
    ]
    allowance2: Annotated[
        ContractFunc[
            AllowanceRequest,
            primitives.uint256,
        ],
        Name("allowance"),
    ]


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

    binance_balance = await usdt.balance_of(
        "0xF977814e90dA44bFA03b6295A0616a897441aceC"
    ).get()
    binance_balance = await usdt.balance_of(
        "0xF977814e90dA44bFA03b6295A0616a897441aceC"
    ).get(block_number=20_604_386)
    assert binance_balance == 6600822508869000

    # check function with two args
    allowance = await usdt.allowance(
        "0x71AC0c3E825f095E56b81fBA11020f01893d4433",
        "0x38C5412464A03EfDc3820d227b24316C11729E0a",
    ).get(block_number=20604634)
    assert allowance == 126967536
    # check function using BaseModel for args
    allowance = await usdt.allowance2(
        "0x71AC0c3E825f095E56b81fBA11020f01893d4433",
        "0x38C5412464A03EfDc3820d227b24316C11729E0a",
    ).get(block_number=20604640)
    assert allowance == 0
