import click
from yaspin import yaspin
from yaspin.spinners import Spinners
import time
from src.config import config
import yaml
from os import path
from src.services.irancell.irancell import Irancell
import sys


@click.group()
def irancell():
    pass


@irancell.command()
@click.option('--phone', type=str)
@click.option('--password', type=str)
@click.option('--overwrite', is_flag=True, default=False)
def login(phone, password, overwrite):
    if not overwrite and config['irancell']['auth']['phone']:
        if not click.confirm('Login config exist, are you sure to overwrite it?'):
            return

    phone = click.prompt('Enter your phone number', type=str)
    password = click.prompt('Enter your password', type=str, hide_input=True)

    config['irancell']['auth']['phone'].set(phone)
    config['irancell']['auth']['password'].set(password)

    irancell = Irancell(config['irancell'])

    with yaspin(text=click.style('Authentication...', fg='yellow'), color="yellow") as spinner:
        try:
            irancell.authenticate()
            spinner.text = ''
            spinner.fail(click.style('Login Success', fg='green', bold=True))
        except:
            spinner.text = ''
            spinner.fail(click.style('Login Failed', fg='red', bold=True))
            return

    with open(config['config_path'].get(), 'a+') as f:
        f.seek(0)
        raw_config_file = yaml.load(f, Loader=yaml.FullLoader)
        raw_config_file['irancell']['auth']['phone'] = phone
        raw_config_file['irancell']['auth']['password'] = password
        f.truncate(0)
        f.write(yaml.dump(raw_config_file))





@irancell.command()
def logout():
    pass


@irancell.command()
def status():
    pass


@irancell.command()
def search():
    pass
