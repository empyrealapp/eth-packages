from typing import Annotated

import pytest
from eth_rpc import ContractFunc, ProtocolBase, add_middleware, set_default_network
from eth_rpc._transport import _force_get_global_rpc
from eth_rpc.networks import SapphireTestnet
from eth_rpc.types import METHOD, Name, NoArgs, primitives
from pydantic import BaseModel
from sapphire import sapphire_middleware

SAPPHIRE_TESTNET_RPC_URL = "https://testnet.sapphire.oasis.io"


class Contract(ProtocolBase):
    double: ContractFunc[primitives.uint256, primitives.uint256] = METHOD


class SigningResponse(BaseModel):
    public_key: bytes
    private_key: bytes


class SigningDemo(ProtocolBase):
    demo: ContractFunc[NoArgs, SigningResponse]


class WhoAmI(ProtocolBase):
    who_am_i: Annotated[
        ContractFunc[
            NoArgs,
            primitives.address,
        ],
        Name("whoAmI"),
    ]


@pytest.mark.asyncio(loop_scope="session")
async def test_contract():
    set_default_network(SapphireTestnet)
    rpc = _force_get_global_rpc()
    await rpc.oasis_calldata_public_key()
    rpc.oasis_calldata_public_key.sync()

    c = Contract(address="0x29FD7D921997647a1DccA5D8700E3b580C7A8531")
    assert await c.double(100).get() == 200

    add_middleware(sapphire_middleware)

    assert c.double(100).sync.get() == 200
    assert await c.double(100).get() == 200

    signing_demo = SigningDemo(address="0xa1109c5d56c3Cc76e72eCf3291090a8ad96Ccd49")
    response = await signing_demo.demo().get()
    assert isinstance(response, SigningResponse)
    # print(response.public_key.hex())
    # print(response.private_key.hex())

    who_am_i = WhoAmI(address="0xE1687514796F2be43AAa00b2b1abcf3fa5752D07")
    assert (
        await who_am_i.who_am_i().get(
            from_="0x7051DF3cD51115e75ab61d0e5eB0607623A75b56"
        )
        == "0x7051df3cd51115e75ab61d0e5eb0607623a75b56"
    )
