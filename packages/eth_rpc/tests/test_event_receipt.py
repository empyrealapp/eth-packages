import pytest
from unittest.mock import MagicMock

from eth_typing import HexAddress, HexStr
from pydantic import BaseModel

from eth_rpc.event import Event
from eth_rpc.models import EventData, Log, TransactionReceipt
from eth_rpc.utils.event_receipt import (
    EventReceiptUtility,
    get_events_from_receipt,
    get_events_from_tx_hash,
    get_single_event_from_receipt,
    get_single_event_from_tx_hash,
)


class MockTransferEvent(BaseModel):
    from_: HexAddress
    to: HexAddress
    value: int


class MockApprovalEvent(BaseModel):
    owner: HexAddress
    spender: HexAddress
    value: int


@pytest.fixture
def mock_transfer_log():
    return Log(
        transaction_hash=HexStr("0x123"),
        address=HexAddress("0xA0b86a33E6441e8e421b7b0b4b8b8b8b8b8b8b8b"),
        block_hash=HexStr("0x456"),
        block_number=12345,
        data=HexStr("0x0000000000000000000000000000000000000000000000000de0b6b3a7640000"),
        log_index=0,
        removed=False,
        topics=[
            HexStr(
                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
            ),  # Transfer topic0
            HexStr(
                "0x000000000000000000000000a0b86a33e6441e8e421b7b0b4b8b8b8b8b8b8b8b"
            ),  # from
            HexStr(
                "0x000000000000000000000000b0b86a33e6441e8e421b7b0b4b8b8b8b8b8b8b8b"
            ),  # to
        ],
        transaction_index=1,
    )


@pytest.fixture
def mock_approval_log():
    return Log(
        transaction_hash=HexStr("0x123"),
        address=HexAddress("0xA0b86a33E6441e8e421b7b0b4b8b8b8b8b8b8b8b"),
        block_hash=HexStr("0x456"),
        block_number=12345,
        data=HexStr("0x0000000000000000000000000000000000000000000000000de0b6b3a7640000"),
        log_index=1,
        removed=False,
        topics=[
            HexStr(
                "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
            ),  # Approval topic0
            HexStr(
                "0x000000000000000000000000a0b86a33e6441e8e421b7b0b4b8b8b8b8b8b8b8b"
            ),  # owner
            HexStr(
                "0x000000000000000000000000c0b86a33e6441e8e421b7b0b4b8b8b8b8b8b8b8b"
            ),  # spender
        ],
        transaction_index=1,
    )


@pytest.fixture
def mock_receipt(mock_transfer_log, mock_approval_log):
    return TransactionReceipt(
        transaction_hash=HexStr("0x123"),
        block_hash=HexStr("0x456"),
        block_number=12345,
        logs=[mock_transfer_log, mock_approval_log],
        contract_address=None,
        effective_gas_price=20000000000,
        cumulative_gas_used=21000,
        from_=HexAddress("0xA0b86a33E6441e8e421b7b0b4b8b8b8b8b8b8b8b"),
        gas_used=21000,
        logs_bloom=0,
        status=1,
        to=HexAddress("0xB0b86a33E6441e8e421b7b0b4b8b8b8b8b8b8b8b"),
        transaction_index=1,
        type=2,
    )


@pytest.fixture
def mock_transfer_event():
    event = Event[MockTransferEvent](name="Transfer")
    event.match = MagicMock(return_value=True)
    event.process_log = MagicMock(
        return_value=EventData(
            name="Transfer",
            log=MagicMock(),
            event=MockTransferEvent(
                from_=HexAddress("0xA0b86a33E6441e8e421b7b0b4b8b8b8b8b8b8b8b"),
                to=HexAddress("0xB0b86a33E6441e8e421b7b0b4b8b8b8b8b8b8b8b"),
                value=1000000000000000000,
            ),
            network=MagicMock(),
        )
    )
    return event


@pytest.fixture
def mock_approval_event():
    event = Event[MockApprovalEvent](name="Approval")
    event.match = MagicMock(return_value=False)  # Won't match transfer logs
    return event


@pytest.mark.asyncio
async def test_get_events_from_receipt_single_match(mock_receipt, mock_transfer_event):
    """Test extracting events from receipt with single matching event."""
    events = [mock_transfer_event]

    result = await EventReceiptUtility.get_events_from_receipt(events, mock_receipt)

    assert len(result) == 2  # Should match both logs since mock returns True
    assert all(isinstance(event_data, EventData) for event_data in result)
    assert mock_transfer_event.match.call_count == 2  # Called for each log


@pytest.mark.asyncio
async def test_get_events_from_receipt_no_matches(mock_receipt, mock_approval_event):
    """Test extracting events from receipt with no matching events."""
    events = [mock_approval_event]

    result = await EventReceiptUtility.get_events_from_receipt(events, mock_receipt)

    assert len(result) == 0
    assert mock_approval_event.match.call_count == 2  # Called for each log


@pytest.mark.asyncio
async def test_get_events_from_receipt_multiple_event_types(
    mock_receipt, mock_transfer_event, mock_approval_event
):
    """Test extracting events from receipt with multiple event types."""
    events = [mock_transfer_event, mock_approval_event]

    result = await EventReceiptUtility.get_events_from_receipt(events, mock_receipt)

    assert len(result) == 2  # Only transfer events match
    assert mock_transfer_event.match.call_count == 2
    assert mock_approval_event.match.call_count == 2


@pytest.mark.asyncio
async def test_get_events_from_tx_hash(mock_receipt, mock_transfer_event, monkeypatch):
    """Test extracting events from transaction hash."""
    async def mock_get_receipt(tx_hash):
        return mock_receipt

    monkeypatch.setattr(
        "eth_rpc.utils.event_receipt.Transaction.get_receipt_by_hash", mock_get_receipt
    )

    events = [mock_transfer_event]
    tx_hash = HexStr("0x123")

    result = await EventReceiptUtility.get_events_from_tx_hash(events, tx_hash)

    assert len(result) == 2
    assert all(isinstance(event_data, EventData) for event_data in result)


@pytest.mark.asyncio
async def test_get_events_from_tx_hash_no_receipt(mock_transfer_event, monkeypatch):
    """Test extracting events from transaction hash when receipt is None."""
    async def mock_get_receipt(tx_hash):
        return None

    monkeypatch.setattr(
        "eth_rpc.utils.event_receipt.Transaction.get_receipt_by_hash", mock_get_receipt
    )

    events = [mock_transfer_event]
    tx_hash = HexStr("0x123")

    result = await EventReceiptUtility.get_events_from_tx_hash(events, tx_hash)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_get_single_event_from_receipt(mock_receipt, mock_transfer_event):
    """Test extracting single event from receipt."""
    result = await EventReceiptUtility.get_single_event_from_receipt(
        mock_transfer_event, mock_receipt
    )

    assert result is not None
    assert isinstance(result, EventData)


@pytest.mark.asyncio
async def test_get_single_event_from_receipt_no_match(mock_receipt, mock_approval_event):
    """Test extracting single event from receipt with no matches."""
    result = await EventReceiptUtility.get_single_event_from_receipt(
        mock_approval_event, mock_receipt
    )

    assert result is None


@pytest.mark.asyncio
async def test_convenience_functions(mock_receipt, mock_transfer_event):
    """Test that convenience functions work correctly."""
    result1 = await get_events_from_receipt([mock_transfer_event], mock_receipt)
    assert len(result1) == 2

    result2 = await get_single_event_from_receipt(mock_transfer_event, mock_receipt)
    assert result2 is not None


@pytest.mark.asyncio
async def test_process_log_exception_handling(mock_receipt, mock_transfer_event):
    """Test that exceptions during process_log are handled gracefully."""
    mock_transfer_event.process_log.side_effect = Exception("Decode error")

    result = await EventReceiptUtility.get_events_from_receipt(
        [mock_transfer_event], mock_receipt
    )

    assert len(result) == 0
