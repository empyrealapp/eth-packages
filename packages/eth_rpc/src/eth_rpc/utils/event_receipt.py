from typing import TYPE_CHECKING, Optional, TypeVar

from eth_typing import HexStr

if TYPE_CHECKING:
    from ..event import Event
    from ..models import EventData, TransactionReceipt
    from ..transaction import Transaction

T = TypeVar("T")


class EventReceiptUtility:
    """
    Utility for extracting and decoding events from transaction receipts.

    This utility takes Event types and transaction receipts/hashes, matches events
    by their topic0 signatures, and returns properly decoded EventData objects.
    """

    @staticmethod
    async def get_events_from_receipt(
        events: list["Event[T]"], receipt: "TransactionReceipt"
    ) -> list["EventData[T]"]:
        """
        Extract and decode events from a transaction receipt.

        Args:
            events: List of Event types to match against
            receipt: Transaction receipt containing logs

        Returns:
            List of decoded EventData objects for matched events
        """
        matched_events = []

        for log in receipt.logs:
            for event in events:
                if event.match(log):
                    try:
                        event_data = event.process_log(log)
                        matched_events.append(event_data)
                    except Exception:
                        continue

        return matched_events

    @staticmethod
    async def get_events_from_tx_hash(
        events: list["Event[T]"], tx_hash: HexStr
    ) -> list["EventData[T]"]:
        """
        Extract and decode events from a transaction hash.

        Args:
            events: List of Event types to match against
            tx_hash: Transaction hash to get receipt for

        Returns:
            List of decoded EventData objects for matched events
        """
        from ..transaction import Transaction

        receipt = await Transaction.get_receipt_by_hash(tx_hash)
        if not receipt:
            return []

        return await EventReceiptUtility.get_events_from_receipt(events, receipt)

    @staticmethod
    async def get_single_event_from_receipt(
        event: "Event[T]", receipt: "TransactionReceipt"
    ) -> Optional["EventData[T]"]:
        """
        Extract and decode a single event type from a transaction receipt.

        Args:
            event: Event type to match against
            receipt: Transaction receipt containing logs

        Returns:
            First matching decoded EventData object, or None if no matches
        """
        results = await EventReceiptUtility.get_events_from_receipt([event], receipt)
        return results[0] if results else None

    @staticmethod
    async def get_single_event_from_tx_hash(
        event: "Event[T]", tx_hash: HexStr
    ) -> Optional["EventData[T]"]:
        """
        Extract and decode a single event type from a transaction hash.

        Args:
            event: Event type to match against
            tx_hash: Transaction hash to get receipt for

        Returns:
            First matching decoded EventData object, or None if no matches
        """
        results = await EventReceiptUtility.get_events_from_tx_hash([event], tx_hash)
        return results[0] if results else None


async def get_events_from_receipt(
    events: list["Event[T]"], receipt: "TransactionReceipt"
) -> list["EventData[T]"]:
    """
    Convenience function to extract and decode events from a transaction receipt.
    """
    return await EventReceiptUtility.get_events_from_receipt(events, receipt)


async def get_events_from_tx_hash(
    events: list["Event[T]"], tx_hash: HexStr
) -> list["EventData[T]"]:
    """
    Convenience function to extract and decode events from a transaction hash.
    """
    return await EventReceiptUtility.get_events_from_tx_hash(events, tx_hash)


async def get_single_event_from_receipt(
    event: "Event[T]", receipt: "TransactionReceipt"
) -> Optional["EventData[T]"]:
    """
    Convenience function to extract and decode a single event from a transaction receipt.
    """
    return await EventReceiptUtility.get_single_event_from_receipt(event, receipt)


async def get_single_event_from_tx_hash(
    event: "Event[T]", tx_hash: HexStr
) -> Optional["EventData[T]"]:
    """
    Convenience function to extract and decode a single event from a transaction hash.
    """
    return await EventReceiptUtility.get_single_event_from_tx_hash(event, tx_hash)
