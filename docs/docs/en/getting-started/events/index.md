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

Once you have defined the BaseModel for the event's interface, you need to create an Event instance that has the Event Type as a Generic Argument.


```python
# This will yield EventData[V2SwapEventType] when you subscribe
V2SwapEvent = Event[V2SwapEventType](name="Swap")
```
