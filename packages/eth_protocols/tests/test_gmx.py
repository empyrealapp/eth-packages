import pytest

from eth_protocols.gmx.synthetics_reader import SyntheticsReader


@pytest.mark.asyncio(scope="session")
async def test_synthetics_reader() -> None:
    reader = SyntheticsReader(network="arbitrum")
    markets = await reader.get_available_markets()
    print(markets)
