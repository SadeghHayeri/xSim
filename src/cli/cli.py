import click
from src.cli.irancell import irancell


@click.group()
def cli():
    pass


cli.add_command(irancell)
cli()
