import pytest
from eth_rpc import ContractFunc, ProtocolBase, add_middleware, set_default_network
from eth_rpc._transport import _force_get_global_rpc
from eth_rpc.networks import SapphireTestnet
from eth_rpc.types import METHOD, primitives
from sapphire import sapphire_middleware

SAPPHIRE_TESTNET_RPC_URL = "https://testnet.sapphire.oasis.io"


class Contract(ProtocolBase):
    double: ContractFunc[primitives.uint256, primitives.uint256] = METHOD


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
