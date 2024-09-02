from typing import Annotated

from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import Name, primitives
from pydantic import BaseModel


class Route(BaseModel):
    from_: Annotated[primitives.address, Name("from")]
    to: primitives.address
    stable: bool


class EthSwapRequest(BaseModel):
    amount_out_min: primitives.uint256
    route: list[Route]
    to: primitives.address
    deadline: primitives.uint256


class TokenSwapRequest(BaseModel):
    amount_in: primitives.uint256
    amount_out_min: primitives.uint256
    route: list[Route]
    to: primitives.address
    deadline: primitives.uint256


class LynexV2Router(ProtocolBase):
    swap_exact_tokens_for_tokens_supporting_fee_on_transfer_tokens: Annotated[
        ContractFunc[
            TokenSwapRequest,
            None,
        ],
        Name("swapExactTokensForTokensSupportingFeeOnTransferTokens"),
    ]

    swap_exact_eth_for_tokens_supporting_fee_on_transfer_tokens: Annotated[
        EthSwapRequest,
        Name("swapExactETHForTokensSupportingFeeOnTransferTokens"),
    ]

    # TODO: finish adding methods
