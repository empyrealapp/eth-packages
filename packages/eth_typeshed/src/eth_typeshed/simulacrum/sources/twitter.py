from typing import Annotated, Any, ClassVar

from eth_abi import encode
from eth_rpc import ContractFunc
from eth_rpc.types import METHOD, Name, primitives

from ..utils import BaseSource, Command, SimulacrumSubmission, Tweet


class XSource(BaseSource):
    source_name: ClassVar[str] = "X"
    input_type: ClassVar[type] = Tweet

    lookup_address: Annotated[
        ContractFunc[
            tuple[primitives.bytes32, primitives.uint256],
            primitives.address,
        ],
        Name("lookupAddress"),
    ] = METHOD
    convert: ContractFunc[
        primitives.bytes,
        Command,
    ] = METHOD
    load_command: Annotated[
        ContractFunc[
            primitives.bytes32,
            Command,
        ],
        Name("loadCommand"),
    ] = METHOD

    def submit_tweet(
        self,
        tweet: Tweet,
        signatures: list[bytes],
        require_success: bool = True,
    ) -> ContractFunc[
        SimulacrumSubmission,
        bool,
    ]:
        return self.submit(
            SimulacrumSubmission(
                source_data=tweet.to_bytes(),
                verification_data=encode(["bytes[]"], [signatures]),
                require_success=require_success,
            )
        )

    @classmethod
    def validate_input(cls, input: Any):
        if not isinstance(input, Tweet):
            return False
        text: str = input.full_text
        first_line = text.split("\n")[0]

        modifiers = first_line.split(" ")
        if len(modifiers) < 2:
            return False
        if modifiers[0] != "#simulacrum":
            return False
        return True
