import click
from src.cli.irancell import irancell


@click.group()
def cli():
    pass


def main():
    cli.add_command(irancell)
    cli()


if __name__ == '__main__':
    main()
