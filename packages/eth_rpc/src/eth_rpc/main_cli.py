import json

import click
from eth_typing import HexAddress

from .block_explorer import get_abi
from .codegen import codegen as codegen_cmd


@click.group()
def cli():
    pass


@click.group()
def codegen():
    pass


@click.command()
@click.argument("input_file")
@click.option("--output", "-o", default="abi.py")
@click.option("--contract-name", "-c", default="AnonContract")
def load(input_file, output, contract_name: str):
    with open(input_file, "r") as f:
        raw_abi = f.read()

    abi = json.loads(raw_abi)
    if isinstance(abi, dict):
        try:
            abi = abi["abi"]
        except KeyError:
            raise ValueError("Invalid Format")
    with open(output, "w") as f:
        f.write(codegen_cmd(abi, contract_name))


@click.command()
@click.option("--network", "-n", default="ethereum")
@click.option("--address", "-a", required=True)
@click.option("--output", "-o", default="abi.py")
@click.option("--api_key", "-a", required=True)
@click.option("--contract-name", "-c", default="AnonContract")
def explorer(
    network: str, address: HexAddress, output: str, api_key, contract_name: str
):
    if network.lower() != "ethereum":
        click.echo("Network not yet supported.  Coming soon!")
        return
    abi = get_abi(address, api_key)
    with open(output, "w") as f:
        f.write(codegen_cmd(abi, contract_name))


cli.add_command(codegen)
codegen.add_command(load)
codegen.add_command(explorer)

if __name__ == "__main__":
    cli()
