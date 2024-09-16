from typing import Annotated

from eth_rpc import ContractFunc, Event, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, Struct, primitives
from pydantic import BaseModel, Field

from .utils import Command


class NewBlockEventType(BaseModel):
    index: primitives.uint256
    hash: primitives.bytes32


NewBlockEvent = Event[NewBlockEventType](name="NewBlock")


class Blocks(ProtocolBase):
    mine_block: Annotated[
        ContractFunc[
            primitives.uint256,
            None,
        ],
        Name("mineBlock"),
    ] = METHOD

    get_nonce: Annotated[
        ContractFunc[
            Command,
            primitives.uint256,
        ],
        Name("getNonce"),
    ] = METHOD

    get_block_commands: Annotated[
        ContractFunc[
            primitives.uint256,
            list[Command],
        ],
        Name("getBlockCommands"),
    ] = METHOD

    default_gas: Annotated[
        ContractFunc[
            NoArgs,
            primitives.uint256,
        ],
        Name("defaultGas"),
    ] = METHOD

    pending_txs: Annotated[
        ContractFunc[
            NoArgs,
            primitives.uint256,
        ],
        Name("pendingTxs"),
    ] = METHOD


class NonceArgs(BaseModel):
    owner_id: primitives.bytes32
    namespace: primitives.bytes32
    index: primitives.uint256 = Field(default=primitives.uint256(0))


class SimulacrumBlock(Struct):
    number: primitives.uint256
    timestamp: primitives.uint256
    commands: list[primitives.bytes32]
    command_count: primitives.uint256
    hash: primitives.bytes32
    mined: bool


class BlockStorage(ProtocolBase):
    get_nonce: Annotated[
        ContractFunc[
            NonceArgs,
            primitives.uint256,
        ],
        Name("getNonce"),
    ] = METHOD

    get_block: Annotated[
        ContractFunc[
            primitives.uint256,
            SimulacrumBlock,
        ],
        Name("getBlock"),
    ] = METHOD

    get_command_by_hash: Annotated[
        ContractFunc[
            primitives.bytes32,
            Command,
        ],
        Name("getCommandByHash"),
    ] = METHOD
