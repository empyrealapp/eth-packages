# Subscription

## Subscribing to Events in Realtime
The subscribe method on the Event instance is an async generator that will yield [EventData[T]](/api/event_data/){.internal-link}, where `T` is a Generic Argument of type `BaseModel` for the event's schema.  For example:

```python
# Create an event filter for the V2SwapEvent
# Set up a filter for the V2SwapEvent, specifying the contract address
# You can also filter on the different topics, ie
event_filter = V2SwapEvent.set_filter(
    addresses=["0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852"],
    # topic1="0x...",
    # topic2="0x...",
)

# Use an asynchronous for loop to iterate over the event subscriber
async for event_data in event_filter.subscribe():
    # event_data contains two main components:
    # 1. The raw log data
    log: Log = event_data.log
    # 2. The decoded event data as an instance of V2SwapEventType
    event: V2SwapEventType = event_data.event

    # You can access other fields similarly:
    print(f"Sender: {event.sender}")
    print(f"To: {event.to}")
    print(f"Amount 0 In: {event.amount0_in}")
    print(f"Amount 1 In: {event.amount1_in}")
    print(f"Amount 0 Out: {event.amount0_out}")
    print(f"Amount 1 Out: {event.amount1_out}")

    You can also access raw log data if needed:
    print(f"Block Number: {log.block_number}")
    print(f"Transaction Hash: {log.transaction_hash}")
```

## Backfill

## Backfilling Historical Event Data

The Event class also provides functionality for retrieving historical event data within a specified block range. This is particularly useful for backfilling data. Here's an example of how to use this feature:

```python
from eth_rpc.utils import address_to_topic

class TransferEventType(BaseModel):
    sender: Annotated[primitives.address, Indexed]
    recipient: Annotated[primitives.address, Indexed]
    amount: primitives.uint256

# Create an event filter for the TransferEvent
TransferEvent = Event[TransferEventType](name="Transfer")

# Set up a filter for the TransferEvent, specifying the topic1 filter.
# This makes the subscription only return events with the sender specified.
event_filter = TransferEvent.set_filter(
    topic1=address_to_topic("0xBE0eB53F46cd790Cd13851d5EFf43D12404d33E8"),
)

# Use an asynchronous for loop to iterate over the event subscriber
# This will yield EventData[TransferEvent]
async for event_data in event_filter.backfill(start_block=16_000_000, end_block=18_000_000):
    # event_data contains two main components:
    # 1. The raw log data
    log: Log = event_data.log
    # 2. The decoded event data as an instance of V2SwapEventType
    event: V2SwapEventType = event_data.event
```
