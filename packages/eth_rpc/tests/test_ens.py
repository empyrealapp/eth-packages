import os

import pytest
from eth_rpc import set_alchemy_key
from eth_rpc.ens import lookup_addr


@pytest.mark.asyncio(scope="session")
@pytest.mark.contract
async def test_ens_lookup():
    set_alchemy_key(os.environ["ALCHEMY_KEY"])
    response = await lookup_addr("vitalik.eth", block_number=20_000_000)
    assert response == "0xd8da6bf26964af9d7eed9e03e53415d37aa96045"

    response = await lookup_addr("000.eth", block_number=15_000_000)
    assert response == "0x9394a7cf1b7ad5de4825c3a3d8033453e23a4ce1"

    response = await lookup_addr("000.eth", block_number=20_000_000)
    assert response == "0xb34d849c0551c6a4c0d491224bcc6114b906afc4"
