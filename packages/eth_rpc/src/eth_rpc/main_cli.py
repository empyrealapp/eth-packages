import json

import click

from .codegen import codegen as codegen_cmd


@click.group()
def cli():
    pass


@click.command()
@click.argument("input_file")
@click.argument("output_file")
@click.option("-c", "--class-name")
def codegen(input_file, output_file, class_name: str | None = None):
    if not class_name:
        class_name = "AnonContract"
    with open(input_file, "r") as f:
        raw_abi = f.read()

    abi = json.loads(raw_abi)
    with open(output_file, "w") as f:
        f.write(codegen_cmd(abi, class_name))


cli.add_command(codegen)

if __name__ == "__main__":
    cli()
