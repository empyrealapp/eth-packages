from typing import Annotated

from eth_rpc import ProtocolBase, ContractFunc
from eth_rpc.types import primitives, Name, NoArgs, Struct


class StringKeyValue(Struct):
    key: primitives.string
    value: primitives.string


class StringArrayKeyValue(Struct):
    key: primitives.string
    value: list[primitives.string]


class BytesKeyValue(Struct):
    key: primitives.string
    value: bytes

class BytesArrayKeyValue(Struct):
    key: primitives.string
    value: list[bytes]


class Bytes32KeyValue(Struct):
    key: primitives.string
    value: primitives.bytes32

class Bytes32ArrayKeyValue(Struct):
    key: primitives.string
    value: list[primitives.bytes32]


class BoolKeyValue(Struct):
    key: primitives.string
    value: primitives.bool


class BoolArrayKeyValue(Struct):
    key: primitives.string
    value: list[primitives.bool]


class IntKeyValue(Struct):
    key: primitives.string
    value: primitives.int256


class IntArrayKeyValue(Struct):
    key: primitives.string
    value: list[primitives.int256]


class UintKeyValue(Struct):
    key: primitives.string
    value: primitives.uint256


class UintArrayKeyValue(Struct):
    key: primitives.string
    value: list[primitives.uint256]


class AddressKeyValue(Struct):
    key: primitives.string
    value: primitives.address


class AddressArrayKeyValue(Struct):
    key: primitives.string
    value: list[primitives.address]


class StringItems(Struct):
    items: list[StringKeyValue]
    array_items: Annotated[list[StringArrayKeyValue], Name("arrayItems")]


class BytesItems(Struct):
    items: list[BytesKeyValue]
    array_items: Annotated[list[BytesArrayKeyValue], Name("arrayItems")]


class Bytes32Items(Struct):
    items: list[Bytes32KeyValue]
    array_items: Annotated[list[Bytes32ArrayKeyValue], Name("arrayItems")]


class BoolItems(Struct):
    items: list[BoolKeyValue]
    array_items: Annotated[list[BoolArrayKeyValue], Name("arrayItems")]


class IntItems(Struct):
    items: list[IntKeyValue]
    array_items: Annotated[list[IntArrayKeyValue], Name("arrayItems")]


class UintItems(Struct):
    items: list[UintKeyValue]
    array_items: Annotated[list[UintArrayKeyValue], Name("arrayItems")]


class AddressItems(Struct):
    items: list[AddressKeyValue]
    array_items: Annotated[list[AddressArrayKeyValue], Name("arrayItems")]


class EventLogData(Struct):
    address_items: Annotated[AddressItems, Name("addressItems")]
    uint_items: Annotated[UintItems, Name("uintItems")]
    int_items: Annotated[IntItems, Name("intItems")]
    bool_items: Annotated[BoolItems, Name("boolItems")]
    bytes32_items: Annotated[Bytes32Items, Name("bytes32Items")]
    bytes_items: Annotated[BytesItems, Name("bytesItems")]
    string_items: Annotated[StringItems, Name("stringItems")]


class EventEmitter(ProtocolBase):
    emit_data_log1: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, bytes],
            None
        ],
        Name("emitDataLog1"),
    ]

    emit_data_log2: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.bytes32, bytes],
            None
        ],
        Name("emitDataLog2"),
    ]

    emit_data_log3: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.bytes32, primitives.bytes32, bytes],
            None
        ],
        Name("emitDataLog3"),
    ]

    emit_data_log4: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.bytes32, primitives.bytes32, primitives.bytes32, bytes],
            None
        ],
        Name("emitDataLog4"),
    ]

    emit_event_log: Annotated[
        ContractFunc[
            tuple[primitives.string, EventLogData],
            None
        ],
        Name("emitEventLog"),
    ]

    emit_event_log1: Annotated[
        ContractFunc[
            tuple[primitives.string, primitives.bytes32, EventLogData],
            None
        ],
        Name("emitEventLog1"),
    ]

    emit_event_log2: Annotated[
        ContractFunc[
            tuple[primitives.string, primitives.bytes32, primitives.bytes32, EventLogData],
            None
        ],
        Name("emitEventLog2"),
    ]

    role_store: Annotated[
        ContractFunc[
            NoArgs,
            primitives.address
        ],
        Name("roleStore"),
    ]
