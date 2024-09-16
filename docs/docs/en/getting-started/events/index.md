# Events

The [Event class](/api/event/){.internal-link} in `packages/eth_rpc/src/eth_rpc/event.py` is a crucial component for handling Ethereum events. Here's an overview of its functionality and usage:

## Event Class

The `Event` class is a Generic class representing an Ethereum event and provides methods to interact with it.  In order to define the schema of the event, you need to define a pydantic class with the appropriate fields, annotated with `Indexed` when necessary.

```python
from typing import Annotated

from eth_rpc import Event
from eth_rpc.types import Indexed
from pydantic import BaseModel

class V2SwapEventType(BaseModel):
    sender: Annotated[primitives.address, Indexed]
    amount0_in: primitives.uint256
    amount1_in: primitives.uint256
    amount0_out: primitives.uint256
    amount1_out: primitives.uint256
    to: Annotated[primitives.address, Indexed]
```

## Subscription

You can define an event by creating a BaseModel that defines the event's interface, and then creating an Event instance that has the Event Type as a Generic Argument.  The async generator will yield [EventData](/api/event_data/){.internal-link}, where the type of the event is the Generic type applied when the Event was initialized.  For example:


```python
# This will yield EventData[V2SwapEventType] when you subscribe
V2SwapEvent = Event[V2SwapEventType](name="Swap")
```

Then, you are able to use this event to index, filter and decode logs.  For example:

```python
# Create an event filter for the V2SwapEvent
# Set up a filter for the V2SwapEvent, specifying the contract address
event_filter = V2SwapEvent.set_filter(
    addresses=["0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852"]
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

This is also useful for backfilling data from a blockchain.  For example:

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
