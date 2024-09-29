from typing import Annotated

import pytest
from eth_rpc import (
    ContractFunc,
    PrivateKeyWallet,
    ProtocolBase,
    add_middleware,
    get_selected_wallet,
    set_default_network,
    set_selected_wallet,
)
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

    wallet = PrivateKeyWallet.create_new()
    set_selected_wallet(wallet)
    assert get_selected_wallet() == wallet

    c = Contract(address="0x29FD7D921997647a1DccA5D8700E3b580C7A8531")
    assert await c.double(100).get() == 200

    who_am_i = WhoAmI(address="0xE1687514796F2be43AAa00b2b1abcf3fa5752D07")
    assert (
        await who_am_i.who_am_i().get() == "0x0000000000000000000000000000000000000000"
    )

    add_middleware(sapphire_middleware)

    assert c.double(100).sync.get() == 200
    assert await c.double(100).get() == 200

    # simple demo application that returns two bytes array for signing
    signing_demo = SigningDemo(address="0xa1109c5d56c3Cc76e72eCf3291090a8ad96Ccd49")
    response = await signing_demo.demo().get()
    assert isinstance(response, SigningResponse)
    assert len(response.public_key.hex()) == 66
    assert len(response.private_key.hex()) == 64

    # simple endpoint that returns the sender's address
    who_am_i = WhoAmI(address="0xE1687514796F2be43AAa00b2b1abcf3fa5752D07")
    assert await who_am_i.who_am_i().get(from_=wallet.address) == wallet.address.lower()
