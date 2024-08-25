import pytest
from eth_rpc import Transaction
from eth_rpc.networks import Arbitrum, Ethereum


@pytest.mark.unit
def test_transaction_network() -> None:
    # Currently, block is a singleton
    tx = Transaction[Arbitrum]
    assert tx._network == Arbitrum

    tx2 = Transaction[Ethereum]
    assert tx2._network == Ethereum
    assert tx._network == Arbitrum
