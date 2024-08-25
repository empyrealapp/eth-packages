import os

import pytest
from eth_rpc import Block, set_alchemy_key
from eth_rpc.networks import Arbitrum, Ethereum


@pytest.mark.unit
def test_block_network() -> None:
    # Currently, block is a singleton
    block = Block[Arbitrum]
    assert block._network == Arbitrum

    block2 = Block[Ethereum]
    assert Block._network is None
    assert block._network == Arbitrum
    assert block2._network == Ethereum


@pytest.mark.asyncio(scope="session")
async def test_block_methods() -> None:
    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    assert Block[Arbitrum]._network == Arbitrum
    assert Block[Ethereum]._network == Ethereum

    ten_million_eth = await Block[Ethereum].load_by_number(10_000_000)
    assert ten_million_eth.number == 10_000_000
    assert len(ten_million_eth.transactions) == 103
    TEN_MILLION_BLOCK_HASH_ETH = (
        "0xaa20f7bde5be60603f11a45fc4923aab7552be775403fc00c2e6b805e6297dbe"
    )
    assert ten_million_eth.hash == TEN_MILLION_BLOCK_HASH_ETH

    ten_million_arb = await Block[Arbitrum].load_by_number(10_000_000)
    TEN_MILLION_BLOCK_HASH_ARB = (
        "0xed03835298dc4bfbb5da9c6d26aa8c8bf96bb58bcd71ea868f3b356de51ac35a"
    )
    assert ten_million_arb.hash == TEN_MILLION_BLOCK_HASH_ARB

    assert (await Block[Ethereum].load_by_hash(ten_million_eth.hash)) == ten_million_eth
    assert (await Block[Arbitrum].load_by_hash(ten_million_arb.hash)) == ten_million_arb

    fee_history = await Block[Ethereum].fee_history()
    assert fee_history
