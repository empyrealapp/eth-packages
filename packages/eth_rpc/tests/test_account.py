import pytest
from eth_rpc import Account
from eth_rpc.networks import Arbitrum, Ethereum


@pytest.mark.unit
def test_account_network() -> None:
    # Currently, block is a singleton
    acct = Account[Arbitrum]
    assert acct._network == Arbitrum

    acct2 = Account[Ethereum]
    assert acct._network == Arbitrum
    assert acct2._network == Ethereum
