from typing import Annotated

from eth_rpc import ContractFunc, Event, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, Struct, primitives
from pydantic import BaseModel, Field

from ..models import Command


class NewBlockEventType(BaseModel):
    index: primitives.uint256
    hash: primitives.bytes32


NewBlockEvent = Event[NewBlockEventType](name="NewBlock")


class SimulacrumBlock(Struct):
    number: primitives.uint256
    timestamp: primitives.uint256
    commands: list[primitives.bytes32]
    command_count: primitives.uint256
    hash: primitives.bytes32
    mined: bool


class Blocks(ProtocolBase):
    mine_block: Annotated[
        ContractFunc[
            primitives.uint256,
            None,
        ],
        Name("mineBlock"),
    ] = METHOD

    get_command: Annotated[
        ContractFunc[primitives.bytes32, Command],
        Name("getCommand"),
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

    get_block: Annotated[
        ContractFunc[
            primitives.uint256,
            SimulacrumBlock,
        ],
        Name("getBlock"),
    ] = METHOD

    current_block: Annotated[
        ContractFunc[
            NoArgs,
            primitives.uint256,
        ],
        Name("currentBlock"),
    ] = METHOD


class NonceArgs(BaseModel):
    owner_id: primitives.bytes32
    namespace: primitives.bytes32
    index: primitives.uint256 = Field(default=primitives.uint256(0))
