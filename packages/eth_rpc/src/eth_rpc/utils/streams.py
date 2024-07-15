from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eth_rpc.models import EventData


def sort_key(row: "EventData"):
    return (row.tx.block_number, row.tx.transaction_index, row.tx.log_index)


def combine(*args: Iterator["EventData"]):
    generators: list[Iterator["EventData"]] = list(args)
    values = [next(generator) for generator in generators]
    dedupe = {}
    while len(generators):
        min_index = values.index(min(values, key=sort_key))
        min_value = values[min_index]
        try:
            values[min_index] = next(generators[min_index])
        except StopAsyncIteration:
            generators.pop(min_index)
            values.pop(min_index)
        if (key := sort_key(min_value)) not in dedupe:
            dedupe[key] = True
            yield min_value


async def acombine(*args: AsyncIterator["EventData"]):
    generators: list[AsyncIterator["EventData"]] = list(args)

    values = []
    for generator in generators:
        try:
            value = await anext(generator)
            values.append(value)
        except StopAsyncIteration:
            continue  # Skip this generator if it's already exhausted

    dedupe = {}
    while len(generators):
        if not generators or not values:
            break
        min_index = values.index(min(values, key=sort_key))
        min_value = values[min_index]
        try:
            values[min_index] = await anext(generators[min_index])
        except StopAsyncIteration:
            generators.pop(min_index)
            values.pop(min_index)
        if (key := sort_key(min_value)) not in dedupe:
            dedupe[key] = True
            yield min_value


def ordered_iterator(events: list["EventData"]) -> Iterator["EventData"]:
    for event in sorted(
        events,
        key=lambda x: (x.tx.block_number, x.tx.transaction_index, x.tx.log_index),
    ):
        yield event
