from typing import Annotated, Any

from eth_abi import encode
from eth_rpc import ContractFunc, ProtocolBase
from eth_rpc.types import METHOD, Name, NoArgs, primitives

from ..utils import Command, SimulacrumSubmission, Tweet


class XSource(ProtocolBase):
    convert: ContractFunc[bytes, Command] = METHOD

    default_gas: Annotated[
        ContractFunc[NoArgs, primitives.uint256],
        Name("defaultGas"),
    ] = METHOD

    load_command: Annotated[
        ContractFunc[primitives.bytes32, Command],
        Name("loadCommand"),
    ] = METHOD

    lookup_address_with_index: Annotated[
        ContractFunc[tuple[primitives.bytes32, primitives.uint256], primitives.address],
        Name("lookupAddress"),
    ] = METHOD

    lookup_address: Annotated[
        ContractFunc[primitives.bytes32, primitives.address],
        Name("lookupAddress"),
    ] = METHOD

    max_gas: Annotated[
        ContractFunc[NoArgs, primitives.uint256],
        Name("maxGas"),
    ] = METHOD

    oracle: ContractFunc[NoArgs, primitives.address] = METHOD

    submit: ContractFunc[SimulacrumSubmission, Annotated[bool, "success"]] = METHOD

    submit_many: Annotated[
        ContractFunc[tuple[list[bytes], list[bytes], bool], None],
        Name("submitMany"),
    ] = METHOD

    update_oracle: Annotated[
        ContractFunc[primitives.address, None],
        Name("updateOracle"),
    ] = METHOD

    verify: ContractFunc[tuple[bytes, bytes], bool] = METHOD

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
