from inspect import isclass
from types import GenericAlias
from typing import Generic, TypeVar, cast, get_args, get_origin

from eth_abi import decode, encode
from eth_hash.auto import keccak as keccak_256
from eth_typing import HexAddress, HexStr
from pydantic import BaseModel

from .._request import Request
from ..types import BASIC_TYPES, Name, NoArgs, Struct
from ..utils import is_annotation, transform_primitive

T = TypeVar(
    "T",
    bound=tuple
    | BaseModel
    | BASIC_TYPES
    | list[BASIC_TYPES]
    | tuple[BASIC_TYPES | Struct, ...]
    | HexAddress,
)
U = TypeVar("U")


class FuncSignature(Request, Generic[T, U]):
    alias: str | None = None
    name: str

    def get_identifier(self):
        """This works most of the time"""
        signature = f'{self.name}({",".join(self.get_inputs())})'
        return f"0x{keccak_256(signature.encode('utf-8')).hex()[:8]}"

    def get_inputs(self):
        from ..types import Struct

        inputs, _ = self.__pydantic_generic_metadata__["args"]
        if inputs is NoArgs:
            return []
        if (
            type(inputs) is not GenericAlias
            and isclass(inputs)
            and issubclass(inputs, BaseModel)
        ):
            converted_inputs = transform_primitive(inputs)
            if issubclass(inputs, Struct):
                converted_input_tuple = ",".join(converted_inputs)
                return [f"({converted_input_tuple})"]
        else:
            if get_origin(inputs) == list:
                return [transform_primitive(inputs)]
            elif get_origin(inputs) == tuple:
                return tuple(transform_primitive(input) for input in get_args(inputs))
            else:
                converted_inputs = transform_primitive(inputs)
        if not isinstance(converted_inputs, list):
            return [converted_inputs]
        return converted_inputs

    @property
    def _output(self):
        output_type = self.__pydantic_generic_metadata__["args"][1]
        if is_annotation(output_type):
            return get_args(output_type)[0]
        return output_type

    @property
    def _inputs(self):
        input_type = self.__pydantic_generic_metadata__["args"][0]
        if is_annotation(input_type):
            return get_args(input_type)[0]
        return input_type

    def get_output(self):
        outputs = self._output
        if outputs is type(None):
            return None

        if is_annotation(outputs):
            outputs = get_args(outputs)[0]

        if (
            isclass(outputs)
            and not isinstance(outputs, GenericAlias)
            and issubclass(outputs, BaseModel)
        ):
            converted_outputs = transform_primitive(outputs)
        else:
            converted_outputs = transform_primitive(outputs)
        return converted_outputs

    def get_output_name(self):
        return [self._get_name(output) for output in get_args(self._output)]

    @classmethod
    def _encode(cls, value):
        if isinstance(value, tuple):
            return tuple(cls._encode(val) for val in value)
        elif isinstance(value, list):
            return [cls._encode(val) for val in value]
        elif isinstance(value, BaseModel):
            return tuple(cls._encode(val) for val in value.model_dump().values())
        return value

    def encode_call(self, *, inputs: T) -> HexStr:
        from ..types import Struct

        identifier = self.get_identifier()
        # TODO: this is hard
        if inputs == ():
            return identifier

        if isinstance(inputs, BaseModel):
            if isinstance(inputs, Struct):
                input_data = inputs.to_bytes().hex()
            else:
                input_data = encode(
                    self.get_inputs(),
                    list(inputs.model_dump().values()),
                ).hex()
        elif isinstance(inputs, tuple):
            input_data = encode(
                self.get_inputs(), [self._encode(val) for val in inputs]
            ).hex()
        elif isinstance(inputs, list):
            input_data = encode(
                self.get_inputs(), [[self._encode(val) for val in inputs]]
            ).hex()
        else:
            input_data = encode(self.get_inputs(), [inputs]).hex()
        return HexStr(f"{identifier}{input_data}")

    def decode_result(self, result: HexStr) -> U:
        if isclass(self._output) and issubclass(self._output, Struct):
            return self._output.from_bytes(result)

        output = self.get_output()
        if output is None:
            # return None if the expected return type is None
            return output  # type: ignore

        if not isinstance(output, list):
            output = [output]
            decoded_output = decode(output, bytes.fromhex(result.removeprefix("0x")))[0]

            if get_origin(self._output) == list:
                output_list_type = get_args(self._output)[0]
                if isclass(output_list_type) and issubclass(output_list_type, Struct):
                    decoded_arr: U = cast(
                        U,
                        [output_list_type.from_tuple(item) for item in decoded_output],
                    )
                    return decoded_arr
        else:
            if isclass(self._output) and issubclass(self._output, Struct):
                return self._output.from_bytes(bytes.fromhex(result.removeprefix("0x")))
            else:
                decoded_output = decode(
                    output, bytes.fromhex(result.removeprefix("0x"))
                )

        # NOTE: https://github.com/pydantic/pydantic/discussions/5970
        # TODO: this is discussed to see if its a bug or not.  Annotations are a class but can't be checked as a subclass
        if (
            isclass(self._output)
            and not isinstance(self._output, GenericAlias)
            and issubclass(self._output, BaseModel)
        ):
            decoded = decoded_output
            output = self._output
            response = {}
            for (name, field), value in zip(output.model_fields.items(), decoded):
                response[name] = Struct.cast(field.annotation, value)
            return output(**response)
        return decoded_output

    @staticmethod
    def _get_name(type):
        if is_annotation(type):
            type, *annotations = get_args(type)
            for annotation in annotations:
                if isinstance(annotation, Name):
                    return annotation.value
        return ""
