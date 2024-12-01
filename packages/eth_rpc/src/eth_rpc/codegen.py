import re
from typing import Any

from eth_rpc.types import NoArgs, primitives


def to_snake_case(name):
    if name.isupper():
        return name
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _convert_type(type_: str) -> Any:
    if type_ in ["bytes", "bool"]:
        return type_
    if type_.endswith("[]"):
        return list[_convert_type(type_[:-2])]  # type: ignore
    for _type in dir(primitives):
        if _type == type_:
            return getattr(primitives, type_)
    if type_.startswith("enum "):
        return primitives.uint8
    raise ValueError(f"Invalid Type {type_}")


def object_to_type(obj):
    if "components" in obj:
        components = [object_to_type(t) for t in obj["components"]]
        return tuple[*components]
    try:
        converted_type = _convert_type(obj["internalType"])
        return converted_type
    except ValueError:
        return _convert_type(obj["type"])


def convert_types(types_, full_struct_names: bool = True):
    lst = []
    models = []
    for type_ in types_:
        if "components" in type_:
            if full_struct_names:
                py_model_name = "".join(type_["internalType"].split(".")).removeprefix(
                    "struct "
                )
            else:
                py_model_name = (
                    type_["internalType"].split(".")[-1].removeprefix("struct ")
                )
            field_name = py_model_name
            while field_name.endswith("[]"):
                field_name = f"list[{py_model_name[:-2]}]"
            lst.append(field_name)
            models.append((py_model_name, type_["components"]))
        else:
            converted_type = object_to_type(type_)
            lst.append(converted_type)
    if len(lst) == 0:
        return lst, models
    if len(lst) == 1:
        return lst[0], models
    return (tuple[*lst], models)


def codegen(
    abi: list[dict[str, Any]], contract_name: str, full_struct_names: bool = True
) -> str:  # noqa: C901
    """
    Convert an ABI to the string implementation of a ProtocolBase.

    Make sure to convert it to snakecase and use the Annotated[type, Name("name")] syntax for the contract func

    For Example:
    [{"inputs":[],"name":"WETH","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]

    would convert to:

    from eth_rpc import ProtocolBase, ContractFunc
    from eth_rpc.types import primitives, NoArgs, Struct

    class WETH(ProtocolBase):
        WETH: ContractFunc[NoArgs, primitives.address]
    """
    # Begin building the class string
    imports = [
        "from typing import Annotated\n",
        "from eth_rpc import ProtocolBase, ContractFunc",
        "from eth_rpc.types import primitives, Name, NoArgs, Struct",
        "\n",
    ]
    lines = [
        f"\nclass {contract_name}(ProtocolBase):",
    ]

    # Iterate over each function in the ABI
    model_dict = {}
    for func in abi:
        if func["type"] != "function":
            continue  # Skip non-function types

        func_name = func.get("name", "unnamed_function")
        inputs = func.get("inputs", [])
        outputs = func.get("outputs", [])

        input_type, _models = convert_types(inputs)
        for model_name, model in _models:
            if model_name not in model_dict:
                model_dict[model_name] = model
            elif model_dict[model_name] == model:
                continue
            else:
                print(
                    f"Warning: Duplicate model name {model_name} with different fields"
                )
                count = 1
                while model_name + f"_{count}" in model_dict:
                    count += 1
                model_dict[model_name + f"_{count}"] = model
        output_type, __models = convert_types(
            outputs, full_struct_names=full_struct_names
        )

        for model in __models:
            model_name = model[0].replace("[]", "")
            if model_name not in model_dict:
                model_dict[model_name] = model[1]
            elif model_dict[model_name] == model[1]:
                continue
            else:
                print(
                    f"Warning: Duplicate model name {model_name} with different fields"
                )
                count = 1
                while model_name + f"_{count}" in model_dict:
                    count += 1
                model_dict[model_name + f"_{count}"] = model[1]

        has_name_annotation: bool = False
        alias: str
        if func_name != (
            py_name := to_snake_case(
                func_name.replace("WETH", "Weth").replace("ETH", "Eth")
            )
        ):
            has_name_annotation = True
            alias = py_name
        else:
            alias = func_name

        # Append the function definition to the class
        if input_type == NoArgs or input_type == []:
            input_type = "NoArgs"
        if output_type == []:
            output_type = "None"

        input_type = str(input_type).replace("'", "")
        output_type = str(output_type).replace("'", "")
        if not has_name_annotation:
            lines.append(
                f"\t{func_name}: ContractFunc[\n\t\t{input_type},\n\t\t{output_type}\n\t]\n"
            )
        else:
            lines.append(
                f'\t{alias}: Annotated[\n\t\tContractFunc[\n\t\t\t{input_type},\n\t\t\t{output_type}\n\t\t],\n\t\tName("{func_name}"),\n\t]\n'
            )

    # Combine all lines into a single string

    for _, fields in list(model_dict.items()):
        for field in fields:
            if field["internalType"].startswith("struct"):
                if full_struct_names:
                    model_name = (
                        "".join(field["internalType"].split("."))
                        .replace("[]", "")
                        .removeprefix("struct ")
                    )
                else:
                    model_name = field["internalType"].split(".")[-1].replace("[]", "")

                if model_name not in model_dict:
                    model_dict[model_name] = field["components"]

    models = list(model_dict.items())
    for name, fields in models:
        model_str = f"""
class {name}(Struct):
"""
        embedded_types = []
        for field in fields:
            if (internalType := field["internalType"]).startswith("struct"):
                if full_struct_names:
                    type_ = (
                        "".join(internalType.split("."))
                        .replace("[]", "")
                        .removeprefix("struct ")
                    )
                else:
                    type_ = internalType.split(".")[-1].replace("[]", "")

                while internalType.endswith("[]"):
                    type_ = list[type_]  # type: ignore[valid-type]
                    internalType = internalType[:-2]
            else:
                try:
                    type_ = _convert_type(field["internalType"])
                except ValueError:
                    type_ = object_to_type(field)
                    if field["internalType"].endswith("[]"):
                        type_ = list[type_]  # type: ignore[valid-type]
            embedded_types.append(type_)
            name = field["name"]
            snakecase_name = to_snake_case(field["name"])
            if name == snakecase_name:
                model_str += f"\t{name}: {type_}\n"
            else:
                model_str += f'\t{snakecase_name}: Annotated[{type_}, Name("{name}")]\n'
        lines = [model_str] + lines

    class_str = "\n".join(imports) + "\n".join(lines) + "\n"
    return class_str.replace("eth_rpc.types.", "").replace("\t", "    ").strip() + "\n"
