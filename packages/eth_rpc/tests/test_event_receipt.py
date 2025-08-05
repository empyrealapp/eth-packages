from typing import Annotated

import pytest
from eth_rpc import Event
from eth_rpc.models import Log, TransactionReceipt
from eth_rpc.types import Indexed, primitives
from eth_rpc.utils.event_receipt import (
    EventReceiptUtility,
    get_events_from_receipt,
    get_events_from_tx_hash,
    get_single_event_from_receipt,
    get_single_event_from_tx_hash,
)
from pydantic import BaseModel


class TransferEventType(BaseModel):
    sender: Annotated[primitives.address, Indexed]
    recipient: Annotated[primitives.address, Indexed]
    amount: primitives.uint256


class ApprovalEventType(BaseModel):
    owner: Annotated[primitives.address, Indexed]
    spender: Annotated[primitives.address, Indexed]
    value: primitives.uint256


TransferEvent = Event[TransferEventType](name="Transfer")
ApprovalEvent = Event[ApprovalEventType](name="Approval")
from eth_typing import HexStr

TRANSFER_TX_HASH = HexStr(
    "0xc1b74e10a88ad2bc610432a182ae6d8200bd684704c44dfd0b915b86d4554211"
)
APPROVAL_TX_HASH = HexStr(
    "0x353bbe9c19982849849227f8745a7fb633502bbabde3068f2aeb3295083bc78e"
)


@pytest.fixture(scope="session")
def transfer_receipt():
    """Construct real transaction receipt with Transfer events from raw data."""
    logs_data = [
        {
            "transaction_hash": "0xc1b74e10a88ad2bc610432a182ae6d8200bd684704c44dfd0b915b86d4554211",
            "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "block_hash": "0xa5542fac95d9d23fa3481614579810c6314931cbb3082b4c241781d8eb7650a3",
            "block_number": "0x1601e91",
            "data": "0x0000000000000000000000000000000000000000000000000000000011898e69",
            "log_index": "0x148",
            "removed": False,
            "topics": [
                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "0x000000000000000000000000e0554a476a092703abdb3ef35c80e0d76d32939f",
                "0x0000000000000000000000001111111254eeb25477b68fb85ed929f73a960582",
            ],
            "transaction_index": "0x9d",
        },
        {
            "transaction_hash": "0xc1b74e10a88ad2bc610432a182ae6d8200bd684704c44dfd0b915b86d4554211",
            "address": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
            "block_hash": "0xa5542fac95d9d23fa3481614579810c6314931cbb3082b4c241781d8eb7650a3",
            "block_number": "0x1601e91",
            "data": "0x0000000000000000000000000000000000000000000000000121de58aa468493",
            "log_index": "0x149",
            "removed": False,
            "topics": [
                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "0x0000000000000000000000005141b82f5ffda4c6fe1e372978f1c5427640a190",
                "0x000000000000000000000000e0554a476a092703abdb3ef35c80e0d76d32939f",
            ],
            "transaction_index": "0x9d",
        },
        {
            "transaction_hash": "0xc1b74e10a88ad2bc610432a182ae6d8200bd684704c44dfd0b915b86d4554211",
            "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "block_hash": "0xa5542fac95d9d23fa3481614579810c6314931cbb3082b4c241781d8eb7650a3",
            "block_number": "0x1601e91",
            "data": "0x0000000000000000000000000000000000000000000000000000000011898e69",
            "log_index": "0x14b",
            "removed": False,
            "topics": [
                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "0x0000000000000000000000001111111254eeb25477b68fb85ed929f73a960582",
                "0x000000000000000000000000f621fb08bbe51af70e7e0f4ea63496894166ff7f",
            ],
            "transaction_index": "0x9d",
        },
        {
            "transaction_hash": "0xc1b74e10a88ad2bc610432a182ae6d8200bd684704c44dfd0b915b86d4554211",
            "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
            "block_hash": "0xa5542fac95d9d23fa3481614579810c6314931cbb3082b4c241781d8eb7650a3",
            "block_number": "0x1601e91",
            "data": "0x0000000000000000000000000000000000000000000000000000000011898e69",
            "log_index": "0x14c",
            "removed": False,
            "topics": [
                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "0x000000000000000000000000f621fb08bbe51af70e7e0f4ea63496894166ff7f",
                "0x000000000000000000000000b8f275fbf7a959f4bce59999a2ef122a099e81a8",
            ],
            "transaction_index": "0x9d",
        },
    ]

    logs = [Log(**log_data) for log_data in logs_data]

    return TransactionReceipt(
        transaction_hash=TRANSFER_TX_HASH,
        block_hash="0xa5542fac95d9d23fa3481614579810c6314931cbb3082b4c241781d8eb7650a3",
        block_number="0x1601e91",
        logs=logs,
        contract_address=None,
        effective_gas_price="0x360bc194",
        cumulative_gas_used="0x112d0aa",
        from_="0x2b2cf32c66ea5d1daf9ec70daf7146f445719664",
        gas_used="0x7a251",
        logs_bloom="0x200000000200000000000001001008000040000000004000000000008000000001000000000000000000000020a400000080020000000000000000080000100000000080808000008000100000000000000001000100000008002000004200000820000000012000010000800000000020000000000000010000810000000004000000000000000000000080080000201010000000020801050000080000000000000280000000000080004020000000400000000800080802000000000001002000400000000001000000000040000000000000000004000000028200000200000800000008400800480080001000000000000400000000000000000",
        status="0x1",
        to="0x1231deb6f5749ef6ce6943a275a1d3e7486f4eae",
        transaction_index="0x9d",
        type="0x2",
    )


@pytest.fixture(scope="session")
def approval_receipt():
    """Construct real transaction receipt with Approval events from raw data."""
    logs_data = [
        {
            "transaction_hash": "0x353bbe9c19982849849227f8745a7fb633502bbabde3068f2aeb3295083bc78e",
            "address": "0x30a538effd91acefb1b12ce9bc0074ed18c9dfc9",
            "block_hash": "0x5f42f60b97c076b40d8cad6b8f6cb1dc8f08f50ce0bc6e429e37d2541c96a22d",
            "block_number": "0x15c604ab",
            "data": "0x0000000000000000000000000000000000000000000000000000865666fd1589",
            "log_index": "0x5",
            "removed": False,
            "topics": [
                "0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925",
                "0x000000000000000000000000353801845f8ae3ece792f5597cd96a17c46e6def",
                "0x00000000000000000000000070cbb871e8f30fc8ce23609e9e0ea87b6b222f58",
            ],
            "transaction_index": "0x3",
        }
    ]

    logs = [Log(**log_data) for log_data in logs_data]

    return TransactionReceipt(
        transaction_hash=APPROVAL_TX_HASH,
        block_hash="0x5f42f60b97c076b40d8cad6b8f6cb1dc8f08f50ce0bc6e429e37d2541c96a22d",
        block_number="0x15c604ab",
        logs=logs,
        contract_address=None,
        effective_gas_price="0x989680",
        cumulative_gas_used="0x6b34d",
        from_="0x353801845f8ae3ece792f5597cd96a17c46e6def",
        gas_used="0x7844",
        logs_bloom="0x800000000000000000000000000000000000000000080000000000000000000004000000000000000000000000000000000000000000000000000200000000000000000000000000000400000000000000000000000000000000000000000000000000000000000400000000000000002000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000001000000000000000000000000000000000000000000000000000000000010010000000000000000000000010000000000000000000000000000000000000000000000000000000000000",
        status="0x1",
        to="0x30a538effd91acefb1b12ce9bc0074ed18c9dfc9",
        transaction_index="0x3",
        type="0x2",
    )


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_receipt_transfer_events(transfer_receipt):
    """Test extracting Transfer events from constructed transaction receipt."""
    events = [TransferEvent]
    result = await EventReceiptUtility.get_events_from_receipt(events, transfer_receipt)

    # Should find 4 Transfer events in this transaction
    assert len(result) == 4
    assert all(event_data.name == "Transfer" for event_data in result)
    assert all(hasattr(event_data.event, "sender") for event_data in result)
    assert all(hasattr(event_data.event, "recipient") for event_data in result)
    assert all(hasattr(event_data.event, "amount") for event_data in result)


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_receipt_approval_events(approval_receipt):
    """Test extracting Approval events from constructed transaction receipt."""
    events = [ApprovalEvent]
    result = await EventReceiptUtility.get_events_from_receipt(events, approval_receipt)

    # Should find 1 Approval event in this transaction
    assert len(result) == 1
    assert result[0].name == "Approval"
    assert hasattr(result[0].event, "owner")
    assert hasattr(result[0].event, "spender")
    assert hasattr(result[0].event, "value")


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_receipt_no_matches(transfer_receipt):
    """Test extracting events with no matches."""
    events = [ApprovalEvent]  # Looking for Approval in Transfer transaction
    result = await EventReceiptUtility.get_events_from_receipt(events, transfer_receipt)

    assert len(result) == 0


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_receipt_multiple_event_types(transfer_receipt):
    """Test extracting multiple event types from receipt."""
    events = [TransferEvent, ApprovalEvent]
    result = await EventReceiptUtility.get_events_from_receipt(events, transfer_receipt)

    # Should only find Transfer events in this transaction
    assert len(result) == 4
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
async def test_get_single_event_from_receipt_approval(approval_receipt):
    """Test extracting single Approval event from receipt."""
    result = await EventReceiptUtility.get_single_event_from_receipt(
        ApprovalEvent, approval_receipt
    )

    assert result is not None
    assert result.name == "Approval"


@pytest.mark.asyncio(scope="session")
async def test_convenience_functions(transfer_receipt):
    """Test that convenience functions work correctly."""
    result1 = await get_events_from_receipt([TransferEvent], transfer_receipt)
    assert len(result1) == 4

    result2 = await get_single_event_from_receipt(TransferEvent, transfer_receipt)
    assert result2 is not None


@pytest.mark.asyncio(scope="session")
async def test_convenience_functions_with_approval(approval_receipt):
    """Test convenience functions with Approval events."""
    result1 = await get_events_from_receipt([ApprovalEvent], approval_receipt)
    assert len(result1) == 1

    result2 = await get_single_event_from_receipt(ApprovalEvent, approval_receipt)
    assert result2 is not None


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_tx_hash_mocked(transfer_receipt, monkeypatch):
    """Test extracting events from transaction hash with mocked RPC call."""
    from eth_rpc.transaction import Transaction

    async def mock_get_receipt_by_hash(tx_hash):
        return transfer_receipt

    monkeypatch.setattr(Transaction, "get_receipt_by_hash", mock_get_receipt_by_hash)

    events = [TransferEvent]
    result = await EventReceiptUtility.get_events_from_tx_hash(events, TRANSFER_TX_HASH)

    assert len(result) == 4
    assert all(event_data.name == "Transfer" for event_data in result)


@pytest.mark.asyncio(scope="session")
async def test_get_single_event_from_tx_hash_mocked(approval_receipt, monkeypatch):
    """Test extracting single event from transaction hash with mocked RPC call."""
    from eth_rpc.transaction import Transaction

    async def mock_get_receipt_by_hash(tx_hash):
        return approval_receipt

    monkeypatch.setattr(Transaction, "get_receipt_by_hash", mock_get_receipt_by_hash)

    result = await EventReceiptUtility.get_single_event_from_tx_hash(
        ApprovalEvent, APPROVAL_TX_HASH
    )

    assert result is not None
    assert result.name == "Approval"


@pytest.mark.asyncio(scope="session")
async def test_get_events_from_tx_hash_invalid_hash_mocked(monkeypatch):
    """Test handling of invalid transaction hash with mocked RPC call."""
    from eth_rpc.transaction import Transaction

    async def mock_get_receipt_by_hash(tx_hash):
        return None

    monkeypatch.setattr(Transaction, "get_receipt_by_hash", mock_get_receipt_by_hash)

    invalid_hash = HexStr("0x" + "0" * 64)
    events = [TransferEvent]

    result = await EventReceiptUtility.get_events_from_tx_hash(events, invalid_hash)
    assert len(result) == 0


@pytest.mark.asyncio(scope="session")
async def test_convenience_functions_from_tx_hash_mocked(
    transfer_receipt, approval_receipt, monkeypatch
):
    """Test convenience functions with transaction hash and mocked RPC calls."""
    from eth_rpc.transaction import Transaction

    async def mock_get_receipt_by_hash(tx_hash):
        if tx_hash == TRANSFER_TX_HASH:
            return transfer_receipt
        elif tx_hash == APPROVAL_TX_HASH:
            return approval_receipt
        return None

    monkeypatch.setattr(Transaction, "get_receipt_by_hash", mock_get_receipt_by_hash)

    result1 = await get_events_from_tx_hash([TransferEvent], TRANSFER_TX_HASH)
    assert len(result1) == 4

    result2 = await get_single_event_from_tx_hash(ApprovalEvent, APPROVAL_TX_HASH)
    assert result2 is not None
