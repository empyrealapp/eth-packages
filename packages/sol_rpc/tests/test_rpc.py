import pytest

from sol_rpc.networks.solana import Solana
from sol_rpc.rpc.core import RPC
from sol_rpc.types.args.block import BlockArgs, BlockConfiguration


@pytest.mark.asyncio(scope="session")
async def test_get_block():
    rpc = RPC(network=Solana)
    block = await rpc.get_block(
        BlockArgs(
            number=1,
            configuration=BlockConfiguration(rewards=True, transaction_details="full"),
        ),
    )
    assert block is not None


@pytest.mark.asyncio(scope="session")
async def test_get_tx_count():
    rpc = RPC(network=Solana)
    count = await rpc.get_transaction_count()
    assert count is not None
    assert count > 300_000_000_000


@pytest.mark.asyncio(scope="session")
async def test_get_version():
    rpc = RPC(network=Solana)
    version = await rpc.get_version()
    assert version is not None
