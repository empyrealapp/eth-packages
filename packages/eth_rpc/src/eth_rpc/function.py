from inspect import isclass
from types import GenericAlias
from typing import Generic, NamedTuple, TypeVar, get_args, get_origin

from eth_abi import decode, encode
from eth_hash.auto import keccak as keccak_256
from eth_typing import HexAddress, HexStr, Primitives
from pydantic import BaseModel
from pydantic.fields import FieldInfo

from ._request import Request
from .types import Name, NoArgs
from .utils import is_annotation

T = TypeVar(
    "T",
    bound=tuple
    | BaseModel
    | Primitives
    | list[Primitives]
    | tuple[Primitives, ...]
    | HexAddress,
)
U = TypeVar("U")


def map_name(name):
    return {
        HexAddress: "address",
    }.get(name, name.__name__)


# TODO: this needs a massive overhaul
def convert_base_model(
    base: type[BaseModel], with_name: bool = False, as_tuple: bool = False
):
    lst = []
    for key, field_info in base.model_fields.items():
        lst.append(convert_field_info(key, field_info, with_name=with_name))
    if as_tuple:
        return ",".join(lst)
    return lst


def convert_field_info(alias: str, field: FieldInfo, with_name: bool = False):
    name = "" if not with_name else alias
    field_type = field.annotation

    for metadata in field.metadata:
        if isinstance(metadata, Name) and with_name:
            name = metadata.value

    type_origin = get_origin(field_type)
    if type_origin == list:
        list_type = get_args(field_type)[0]
        converted_list_type = convert(list_type)
        if isinstance(converted_list_type, list):
            converted_list_type = f"({','.join(converted_list_type)})"
        return f"{converted_list_type}[] {name}".strip()
    elif type_origin == tuple:
        tuple_args = f"({','.join([convert(t) for t in get_args(field_type)])}) {name}"
        return tuple_args
    return f"{map_name(field_type)} {name}".strip()


def convert(type, with_name: bool = False):
    name = ""
    # unwrap annotations
    if is_annotation(type):
        type, *annotations = get_args(type)
        if with_name:
            for annotation in annotations:
                if isinstance(annotation, Name):
                    name = annotation.value

    # if it's a list or a tuple
    if isinstance(type, GenericAlias):
        if get_origin(type) in [list, "list"]:
            list_type = get_args(type)[0]
            converted_list_type = convert(list_type)
            # if the list type is a tuple:
            if isinstance(converted_list_type, list):
                converted_list_type = f"({','.join(converted_list_type)})"
            return f"{converted_list_type}[] {name}".strip()
        else:
            tuple_args = [convert(t, with_name=with_name) for t in get_args(type)]
            return tuple_args
    elif getattr(type, "__orig_bases__", [None])[0] == NamedTuple:
        return f"({','.join([convert(t) for t in type.__annotations__.values()])}) {name}".strip()
    elif isclass(type) and issubclass(type, BaseModel):
        return f"({convert_base_model(type, with_name=with_name, as_tuple=True)}) {name}".strip()
    return f"{map_name(type)} {name}".strip()


class FuncSignature(BaseModel, Request, Generic[T, U]):
    alias: str | None = None
    name: str

    def get_identifier(self):
        """This works most of the time"""
        signature = f'{self.name}({",".join(self.get_inputs())})'
        return f"0x{keccak_256(signature.encode('utf-8')).hex()[:8]}"

    def get_inputs(self):
        inputs, _ = self.__pydantic_generic_metadata__["args"]
        if inputs is NoArgs:
            return []
        if (
            type(inputs) is not GenericAlias
            and isclass(inputs)
            and issubclass(inputs, BaseModel)
        ):
            converted_inputs = convert_base_model(inputs)
        else:
            converted_inputs = convert(inputs)
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

        if is_annotation(outputs):
            outputs = get_args(outputs)[0]

        if (
            isclass(outputs)
            and not isinstance(outputs, GenericAlias)
            and issubclass(outputs, BaseModel)
        ):
            converted_outputs = convert_base_model(outputs)
        else:
            converted_outputs = convert(outputs)
        return converted_outputs

    def get_output_name(self):
        return [self._get_name(output) for output in get_args(self._output)]

    def encode_call(self, *, inputs: T) -> HexStr:
        identifier = self.get_identifier()
        if isinstance(inputs, BaseModel):
            input_data = encode(
                self.get_inputs(), list(inputs.model_dump().values())
            ).hex()
        elif not isinstance(inputs, tuple):
            input_data = encode(self.get_inputs(), [inputs]).hex()
        else:
            input_data = encode(self.get_inputs(), inputs).hex()
        return HexStr(f"{identifier}{input_data}")

    def decode_result(self, result: HexStr) -> U:
        output = self.get_output()
        if not isinstance(output, list):
            output = [output]
            decoded_output = decode(output, bytes.fromhex(result.removeprefix("0x")))[0]
        else:
            decoded_output = decode(output, bytes.fromhex(result.removeprefix("0x")))

        # NOTE: https://github.com/pydantic/pydantic/discussions/5970
        # TODO: this is discussed to see if its a bug or not.  Annotations are a class but can't be checked as a subclass
        if (
            isclass(self._output)
            and not isinstance(self._output, GenericAlias)
            and issubclass(self._output, BaseModel)
        ):
            init_dict = {}
            for (key, field_info), val in zip(
                self._output.model_fields.items(), decoded_output
            ):
                init_dict[field_info.alias or key] = val
            return self._output(**init_dict)  # type: ignore
        return decoded_output

    @staticmethod
    def _get_name(type):
        if is_annotation(type):
            type, *annotations = get_args(type)
            for annotation in annotations:
                if isinstance(annotation, Name):
                    return annotation.value
        return ""
