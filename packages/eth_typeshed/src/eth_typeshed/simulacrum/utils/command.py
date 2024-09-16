from enum import IntEnum

from eth_rpc.types import Bytes32Hex as Bytes32
from eth_rpc.types import primitives
from eth_rpc.types.struct import Struct


class CommandStatus(IntEnum):
    PENDING = 0
    SUCCESS = 1
    FAILURE = 2
    GAS_USED = 3


class Reference(Struct):
    platform: Bytes32
    identifier: Bytes32


class Field(Struct):
    key: Bytes32
    value: primitives.string


class Command(Struct):
    id: Bytes32 = primitives.bytes32(b"")
    chain_id: primitives.uint256 = primitives.uint256(0)
    nonce: primitives.uint256 = primitives.uint256(0)
    value: primitives.uint256 = primitives.uint256(0)
    owner_id: Bytes32
    namespace: Bytes32 = primitives.bytes32(b"")
    wallet_index: primitives.uint16 = primitives.uint16(0)

    metaprotocol: Bytes32
    modifiers: list[Bytes32] = []
    references: list[Reference] = []
    args: list[primitives.string] = []
    kwargs: list[Field] = []

    timestamp: primitives.uint64 = primitives.uint64(0)
    gas: primitives.uint256 = primitives.uint256(0)
    bribe: primitives.uint256 = primitives.uint256(0)
    hash: Bytes32 = primitives.bytes32(b"")
    status: CommandStatus = CommandStatus.PENDING
    gas_used: primitives.uint256 = primitives.uint256(0)

    def __repr__(self):
        protocol = self.metaprotocol.decode("utf-8").rstrip("\x00")
        namespace = self.namespace.decode("utf-8").rstrip("\x00")
        return (
            f'<Command namespace="{namespace}" protocol="{protocol}" args={self.args}>'
        )

    __str__ = __repr__
