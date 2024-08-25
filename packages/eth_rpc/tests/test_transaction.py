import pytest
from eth_rpc import Transaction
from eth_rpc.networks import Arbitrum, Ethereum


@pytest.mark.unit
def test_transaction_network() -> None:
    # Currently, block is a singleton
    block = Transaction[Arbitrum]
    assert block == Transaction
    assert block._network == Arbitrum

    Transaction[Ethereum]
    assert Transaction._network == Ethereum
    assert block._network == Ethereum
