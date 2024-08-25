import pytest
from eth_rpc import Account
from eth_rpc.networks import Arbitrum, Ethereum


@pytest.mark.unit
def test_account_network() -> None:
    # Currently, block is a singleton
    block = Account[Arbitrum]
    assert block == Account
    assert block._network == Arbitrum

    Account[Ethereum]
    assert Account._network == Ethereum
    assert block._network == Ethereum
