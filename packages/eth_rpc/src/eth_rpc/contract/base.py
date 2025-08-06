from typing import TYPE_CHECKING, get_args

from eth_rpc.types import Name
from eth_rpc.utils import is_annotation
from pydantic import ConfigDict

from .contract import Contract
from .func_signature import FuncSignature
from .function import ContractFunc


class _ProtocolBase(Contract):
    """
    Base class for creating type-safe contract interfaces.

    ProtocolBase uses Python's type system and metaclass magic to automatically
    generate ContractFunc instances from type annotations. This enables:

    1. **Type Safety**: Full IDE support with autocomplete and type checking
    2. **Automatic ABI Generation**: Contract methods are inferred from type hints
    3. **Runtime Validation**: Input/output types are validated at runtime
    4. **Clean Syntax**: No need to manually instantiate ContractFunc objects

    Example:
        ```python
        class MyToken(ProtocolBase):
            balance_of: ContractFunc[primitives.address, primitives.uint256]

            get_reserves: ContractFunc[
                NoArgs,
                Annotated[tuple[primitives.uint112, primitives.uint112], Name("reserves")]
            ]

            swap: ContractFunc[
                tuple[primitives.uint256, primitives.uint256, list[primitives.address]],
                NoArgs
            ]

        token = MyToken[Ethereum](address="0x...")
        balance = await token.balance_of(user_address).get()
        ```

    The metaclass automatically:
    - Extracts type information from ContractFunc annotations
    - Creates FuncSignature objects with proper encoding/decoding
    - Handles Name annotations for custom function names
    - Injects ContractFunc instances as class attributes

    This approach trades some type system purity for significantly improved
    developer experience and code maintainability.
    """

    model_config = ConfigDict(extra="allow")

    def __init__(self, **kwargs):
        """
        Initialize the contract and inject ContractFunc instances.

        This method performs the core magic of ProtocolBase by:
        1. Iterating through all type-annotated attributes
        2. Extracting input/output types from ContractFunc annotations
        3. Creating FuncSignature objects for ABI encoding/decoding
        4. Injecting ContractFunc instances as runtime attributes

        The type injection process:
        - Parses ContractFunc[T, U] annotations to extract T (input) and U (output) types
        - Handles Annotated types to extract Name metadata for custom function names
        - Creates FuncSignature with proper type information
        - Sets the ContractFunc as an instance attribute

        Args:
            **kwargs: Contract initialization parameters (address, network, etc.)
        """
        super().__init__(**kwargs)

        for alias, func in self._func_sigs.items():
            name = alias
            if is_annotation(func):
                annotation_args = get_args(func)
                args = annotation_args[0]
                for annotation in annotation_args:
                    if isinstance(annotation, Name):
                        name = annotation.value
            else:
                args = func
            T, U = get_args(args)

            setattr(
                self,
                alias,
                ContractFunc[T, U](  # type: ignore
                    func=FuncSignature[T, U](name=name, alias=alias),  # type: ignore
                    contract=self,
                ),
            )


if TYPE_CHECKING:
    #
    #
    # At runtime, this metaclass is not used - we use the simpler _ProtocolBase
    from pydantic._internal._model_construction import ModelMetaclass

    class IndexedKlass(ModelMetaclass):
        def __getitem__(self, item):
            """Enable MyContract[Network] syntax for type checkers."""
            return self

    class ProtocolBase(_ProtocolBase, metaclass=IndexedKlass):
        """Type-safe contract interface base class with network indexing support."""

        pass

else:
    ProtocolBase = _ProtocolBase
