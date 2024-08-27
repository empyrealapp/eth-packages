import pytest
from eth_rpc import Account
from eth_rpc.networks import Arbitrum, Ethereum


@pytest.mark.unit
def test_account_network() -> None:
    # Currently, block is a singleton
    assert Account[Arbitrum]._network == Arbitrum
    assert Account[Ethereum]._network == Ethereum

    acct: type[Account[Arbitrum]] = Account[Arbitrum]
    assert acct._network == Arbitrum
