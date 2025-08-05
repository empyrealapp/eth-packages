import os

import pytest
from eth_rpc import set_alchemy_key
from eth_rpc.networks import Ethereum
from eth_rpc.transaction import Transaction
from eth_rpc.utils.event_receipt import (
    EventReceiptUtility,
    get_events_from_receipt,
    get_events_from_tx_hash,
    get_single_event_from_receipt,
    get_single_event_from_tx_hash,
)
from eth_typeshed.erc20 import ApprovalEvent, TransferEvent
from eth_typing import HexStr

TRANSFER_TX_HASH = HexStr(
    "0xc1b74e10a88ad2bc610432a182ae6d8200bd684704c44dfd0b915b86d4554211"
)
APPROVAL_TX_HASH = HexStr(
    "0x353bbe9c19982849849227f8745a7fb633502bbabde3068f2aeb3295083bc78e"
)


@pytest.fixture(scope="session", autouse=True)
def setup_alchemy():
    """Set up Alchemy API key for all tests."""
    set_alchemy_key(os.environ["ALCHEMY_KEY"])


@pytest.fixture(scope="session")
async def transfer_receipt():
    """Get real transaction receipt with Transfer events."""
    return await Transaction[Ethereum].get_receipt_by_hash(TRANSFER_TX_HASH)


@pytest.fixture(scope="session")
async def approval_receipt():
    """Get real transaction receipt with Approval events."""
    return await Transaction[Ethereum].get_receipt_by_hash(APPROVAL_TX_HASH)


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_receipt_transfer_events(transfer_receipt):
    """Test extracting Transfer events from real transaction receipt."""
    events = [TransferEvent]
    result = await EventReceiptUtility.get_events_from_receipt(events, transfer_receipt)

    assert len(result) > 0
    assert all(event_data.name == "Transfer" for event_data in result)
    assert all(hasattr(event_data.event, "sender") for event_data in result)
    assert all(hasattr(event_data.event, "recipient") for event_data in result)
    assert all(hasattr(event_data.event, "amount") for event_data in result)


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_receipt_approval_events(approval_receipt):
    """Test extracting Approval events from real transaction receipt."""
    events = [ApprovalEvent]
    result = await EventReceiptUtility.get_events_from_receipt(events, approval_receipt)

    assert len(result) == 1
    assert result[0].name == "Approval"
    assert hasattr(result[0].event, "owner")
    assert hasattr(result[0].event, "spender")
    assert hasattr(result[0].event, "value")


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_receipt_no_matches(transfer_receipt):
    """Test extracting events with no matches."""
    events = [ApprovalEvent]
    result = await EventReceiptUtility.get_events_from_receipt(events, transfer_receipt)

    assert len(result) == 0


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_receipt_multiple_event_types(transfer_receipt):
    """Test extracting multiple event types from receipt."""
    events = [TransferEvent, ApprovalEvent]
    result = await EventReceiptUtility.get_events_from_receipt(events, transfer_receipt)

    assert len(result) > 0
    assert all(event_data.name == "Transfer" for event_data in result)


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_tx_hash():
    """Test extracting events from transaction hash."""
    events = [TransferEvent]
    result = await EventReceiptUtility.get_events_from_tx_hash(events, TRANSFER_TX_HASH)

    assert len(result) > 0
    assert all(event_data.name == "Transfer" for event_data in result)


@pytest.mark.asyncio(scope="session")
async def test_get_single_event_from_receipt(transfer_receipt):
    """Test extracting single event from receipt."""
    result = await EventReceiptUtility.get_single_event_from_receipt(
        TransferEvent, transfer_receipt
    )

    assert result is not None
    assert result.name == "Transfer"


@pytest.mark.asyncio(scope="session")
async def test_get_single_event_from_receipt_no_match(transfer_receipt):
    """Test extracting single event with no matches."""
    result = await EventReceiptUtility.get_single_event_from_receipt(
        ApprovalEvent, transfer_receipt
    )

    assert result is None


@pytest.mark.asyncio(scope="session")
async def test_get_single_event_from_tx_hash():
    """Test extracting single event from transaction hash."""
    result = await EventReceiptUtility.get_single_event_from_tx_hash(
        ApprovalEvent, APPROVAL_TX_HASH
    )

    assert result is not None
    assert result.name == "Approval"


@pytest.mark.asyncio(scope="session")
async def test_convenience_functions(transfer_receipt):
    """Test that convenience functions work correctly."""
    result1 = await get_events_from_receipt([TransferEvent], transfer_receipt)
    assert len(result1) > 0

    result2 = await get_single_event_from_receipt(TransferEvent, transfer_receipt)
    assert result2 is not None


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_tx_hash_invalid_hash():
    """Test handling of invalid transaction hash."""
    invalid_hash = HexStr("0x" + "0" * 64)
    events = [TransferEvent]

    result = await EventReceiptUtility.get_events_from_tx_hash(events, invalid_hash)
    assert len(result) == 0


@pytest.mark.asyncio(scope="session")
async def test_convenience_functions_from_tx_hash():
    """Test convenience functions with transaction hash."""
    result1 = await get_events_from_tx_hash([TransferEvent], TRANSFER_TX_HASH)
    assert len(result1) > 0

    result2 = await get_single_event_from_tx_hash(ApprovalEvent, APPROVAL_TX_HASH)
    assert result2 is not None
