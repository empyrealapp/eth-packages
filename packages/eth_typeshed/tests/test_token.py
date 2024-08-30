import pytest
from eth_rpc.networks import Arbitrum
from eth_typeshed.erc20 import ERC20


@pytest.mark.asyncio(loop_scope="session")
async def test_token() -> None:
    usdt = ERC20[Arbitrum](address="0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9")
    total_supply = await usdt.total_supply().get()
    assert total_supply != 0
