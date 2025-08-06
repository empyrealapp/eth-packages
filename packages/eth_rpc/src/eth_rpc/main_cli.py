import asyncio
import json

import click
from eth_rpc.networks import Network, get_network_by_name
from eth_typing import HexAddress

from .codegen import codegen as codegen_cmd


@click.group()
def cli():
    """
    eth-rpc command line interface for Ethereum development tools.

    This CLI provides utilities for generating type-safe Python contract
    interfaces from ABIs, enabling better developer experience and type safety
    when working with smart contracts.
    """
    pass


@click.group()
def codegen():
    """
    Generate type-safe Python contract interfaces from ABIs.

    The codegen commands help you create strongly-typed Python classes
    from contract ABIs, providing IDE support, type checking, and runtime
    validation for your smart contract interactions.
    """
    pass


@click.command()
@click.argument("input_file", type=click.Path(exists=True, readable=True))
@click.option(
    "--output",
    "-o",
    default="abi.py",
    help="Output file path for the generated Python contract class",
)
@click.option(
    "--contract-name",
    "-c",
    default="AnonContract",
    help="Name for the generated Python contract class",
)
def load(input_file, output, contract_name: str):
    """
    Generate a contract class from a local ABI file.

    Reads a JSON ABI file and generates a type-safe Python contract class
    that can be used with eth-rpc for contract interactions.

    INPUT_FILE: Path to the JSON file containing the contract ABI

    Examples:
        eth_rpc codegen load contract.json -o my_contract.py -c MyContract

        eth_rpc codegen load erc20_abi.json -o erc20.py -c ERC20Token

    The generated file will contain:
    - Import statements for required types
    - A ProtocolBase subclass with typed method definitions
    - Proper type annotations for all function inputs and outputs
    """
    try:
        with open(input_file, "r") as f:
            raw_abi = f.read()

        abi = json.loads(raw_abi)
        if isinstance(abi, dict):
            try:
                abi = abi["abi"]
            except KeyError:
                raise ValueError(
                    "Invalid ABI format: expected 'abi' key in JSON object or direct ABI array"
                )

        generated_code = codegen_cmd(abi, contract_name)

        with open(output, "w") as f:
            f.write(generated_code)

        click.echo(f"✓ Generated {contract_name} contract class in {output}")
        click.echo(
            f"  Functions: {len([f for f in abi if f.get('type') == 'function'])}"
        )

    except json.JSONDecodeError as e:
        raise click.ClickException(f"Invalid JSON in {input_file}: {e}")
    except Exception as e:
        raise click.ClickException(f"Error generating contract: {e}")


@click.command()
@click.option(
    "--network",
    "-n",
    default="ethereum",
    type=click.Choice(["ethereum", "base", "arbitrum"], case_sensitive=False),
    help="Blockchain network to fetch the contract from",
)
@click.option(
    "--address",
    "-a",
    required=True,
    help="Contract address to fetch ABI from (must be verified on block explorer)",
)
@click.option(
    "--output",
    "-o",
    default="abi.py",
    help="Output file path for the generated Python contract class",
)
@click.option(
    "--api-key",
    "-k",
    required=True,
    help="Block explorer API key (Etherscan, Basescan, or Arbiscan)",
)
@click.option(
    "--contract-name",
    "-c",
    default="AnonContract",
    help="Name for the generated Python contract class",
)
@click.option(
    "--full-struct-names",
    "-f",
    is_flag=True,
    help="Use full struct names including contract prefix (default: short names)",
)
def explorer(
    network: str,
    address: HexAddress,
    output: str,
    api_key: str,
    contract_name: str,
    full_struct_names: bool = False,
):
    """
    Generate a contract class from a verified contract on a block explorer.
    
    Fetches the ABI from Etherscan (or equivalent) for a verified contract
    and generates a type-safe Python contract class.
    
    Examples:
        eth_rpc codegen explorer \\
            --address 0xA0b86a33E6441b8e776f1c0b8e8e8e8e8e8e8e8e \\
            --api-key YOUR_ETHERSCAN_KEY \\
            --contract-name USDC \\
            --output usdc.py
        
        eth_rpc codegen explorer \\
            --network arbitrum \\
            --address 0x... \\
            --api-key YOUR_ARBISCAN_KEY \\
            --contract-name UniswapV3Pool \\
            --full-struct-names
    
    Requirements:
        - Contract must be verified on the block explorer
        - Valid API key for the respective block explorer
        - Network must be supported (ethereum, base, arbitrum)
    
    The generated class provides:
        - Full type safety for all contract methods
        - IDE autocomplete and error checking
        - Runtime input/output validation
        - Support for both read and write operations
    """
    try:
        if network.lower() not in ["ethereum", "base", "arbitrum"]:
            raise click.ClickException(
                f"Network '{network}' not supported. "
                "Supported networks: ethereum, base, arbitrum"
            )

        network_type: type[Network] = get_network_by_name(network)

        click.echo(f"Fetching ABI for {address} on {network}...")
        abi = asyncio.run(network_type.get_abi(address, api_key))

        if not abi:
            raise click.ClickException(
                f"Could not fetch ABI for {address}. "
                "Ensure the contract is verified and the API key is valid."
            )

        click.echo(f"Generating {contract_name} class...")
        generated_code = codegen_cmd(
            abi, contract_name, full_struct_names=full_struct_names
        )

        with open(output, "w") as f:
            f.write(generated_code)

        function_count = len([f for f in abi if f.get("type") == "function"])
        click.echo(f"✓ Generated {contract_name} contract class in {output}")
        click.echo(f"  Network: {network.title()}")
        click.echo(f"  Address: {address}")
        click.echo(f"  Functions: {function_count}")

        if full_struct_names:
            click.echo("  Using full struct names")

    except Exception as e:
        raise click.ClickException(f"Error fetching contract ABI: {e}")


cli.add_command(codegen)
codegen.add_command(load)
codegen.add_command(explorer)

if __name__ == "__main__":
    cli()
