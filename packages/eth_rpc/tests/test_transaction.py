import pytest
from eth_rpc import Transaction
from eth_rpc.networks import Arbitrum, Ethereum
from eth_typing import HexStr


@pytest.mark.unit
def test_transaction_network() -> None:
    # Currently, block is a singleton
    tx: type[Transaction[Arbitrum]] = Transaction[Arbitrum]
    assert tx._network == Arbitrum
    assert Transaction[Ethereum]._network == Ethereum


@pytest.mark.asyncio(scope="session")
async def test_transaction_load() -> None:
    # Currently, block is a singleton
    tx = await Transaction[Ethereum].get_by_hash(
        HexStr("0x38cab69c76d8d7069f8b90e170a853740f6370f975de9f4d90f50ed6adc2e6ee")
    )
    assert tx
    assert tx.block_number == 20590874
    assert tx.gas_price == 2800000000

    tx2 = await Transaction[Arbitrum].get_by_hash(
        HexStr("0x71183e2c32180bceca2696496e98a6d2805b03676df2cf0ab5189f9169514b16")
    )
    assert tx2
    assert tx2
    assert tx2.block_number == 242473407
    assert tx2.gas_price == 13000000

    # make sure they keep their networks
    assert tx._network == Ethereum
    assert tx2._network == Arbitrum
