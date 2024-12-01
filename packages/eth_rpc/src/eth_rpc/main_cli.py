import asyncio
import json

import click
from eth_rpc.networks import Network, get_network_by_name
from eth_typing import HexAddress

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
@click.option("--api-key", "-a", required=True)
@click.option("--contract-name", "-c", default="AnonContract")
@click.option("--full-struct-names", "-f", is_flag=True, required=False)
def explorer(
    network: str,
    address: HexAddress,
    output: str,
    api_key,
    contract_name: str,
    full_struct_names: bool = False,
):
    if network.lower() not in ["ethereum", "base", "arbitrum"]:
        click.echo("Network not yet supported.  Coming soon!")
        return

    network_type: type[Network] = get_network_by_name(network)

    abi = asyncio.run(network_type.get_abi(address, api_key))
    with open(output, "w") as f:
        f.write(codegen_cmd(abi, contract_name, full_struct_names=full_struct_names))


cli.add_command(codegen)
codegen.add_command(load)
codegen.add_command(explorer)

if __name__ == "__main__":
    cli()
