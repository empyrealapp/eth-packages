import re
from typing import Any

from eth_rpc.types import NoArgs, primitives


def to_snake_case(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _convert_type(type_: str) -> Any:
    if type_ in ["bytes", "bool"]:
        return type_
    if type_.endswith("[]"):
        return list[_convert_type(type_[:-2])]  # type: ignore
    for type in dir(primitives):
        if type == type_:
            return getattr(primitives, type_)
    raise ValueError(f"Invalid Type {type_}")


def object_to_type(obj):
    if "components" in obj:
        components = [object_to_type(t) for t in obj["components"]]
        return tuple[*components]
    return _convert_type(obj["internalType"])


def convert_types(types_):
    lst = []
    models = []
    for type_ in types_:
        if "components" in type_:
            py_model_name = type_["internalType"].split(".")[-1]
            lst.append(py_model_name)
            models.append((py_model_name, type_["components"]))
        else:
            lst.append(object_to_type(type_))
    if len(lst) == 0:
        return lst, models
    if len(lst) == 1:
        return lst[0], models
    return (tuple[*lst], models)


def codegen(abi: list[dict[str, Any]], contract_name: str) -> str:
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
    models = []
    for func in abi:
        if func["type"] != "function":
            continue  # Skip non-function types

        func_name = func.get("name", "unnamed_function")
        inputs = func.get("inputs", [])
        outputs = func.get("outputs", [])

        input_type, _models = convert_types(inputs)
        models.extend(_models)
        output_type, _models = convert_types(outputs)
        models.extend(_models)

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
        if not has_name_annotation:
            lines.append(
                f"\t{func_name}: ContractFunc[\n\t\t{input_type},\n\t\t{output_type}\n\t]\n"
            )
        else:
            lines.append(
                f'\t{alias}: Annotated[\n\t\tContractFunc[\n\t\t\t{input_type},\n\t\t\t{output_type}\n\t\t],\n\t\tName("{func_name}"),\n\t]\n'
            )

    # Combine all lines into a single string

    for name, fields in models:
        model_str = f"""
class {name}(Struct):
"""
        for field in fields:
            type_ = _convert_type(field["internalType"])
            model_str += f"\t{field['name']}: {type_}\n"
        lines = [model_str] + lines

    class_str = "\n".join(imports) + "\n".join(lines) + "\n"
    return class_str.replace("eth_rpc.types.", "").replace("\t", "    ").strip() + "\n"
