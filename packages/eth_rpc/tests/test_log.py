import os

import pytest
from eth_rpc import Log, set_alchemy_key
from eth_rpc.networks import Arbitrum, Ethereum


@pytest.mark.unit
def test_log_network():
    assert Log[Ethereum]._network == Ethereum
    assert Log[Arbitrum]._network == Arbitrum


@pytest.mark.asyncio(scope="session")
async def test_log():
    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    eth_logs = await Log[Ethereum].load_by_number(10_000_000, 10_000_000)
    arb_logs = await Log[Arbitrum].load_by_number(10_000_000, 10_000_000)

    assert len(eth_logs) == 135
    assert len(arb_logs) == 4
