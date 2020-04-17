from yaspin import yaspin
from src.config import config
import yaml
from src.services.irancell.irancell import Irancell
from src.cli.common import *

MAIN_COLOR = 'yellow'
SORT_OPTIONS = ['id', 'name', 'type', 'size', 'international', 'local', 'price', 'unit-price', 'duration']


@click.group()
def irancell():
    pass


@irancell.group()
def offers():
    pass


@irancell.command()
@click.option('--phone', type=str)
@click.option('--password', type=str)
@click.option('--overwrite', is_flag=True, default=False)
def login(phone, password, overwrite):
    if not overwrite and config['irancell']['auth']['phone']:
        click.confirm('Login config exist, are you sure to overwrite it?', abort=True)

    phone = phone or click.prompt('Enter your phone number', type=str)
    password = password or click.prompt('Enter your password', type=str, hide_input=True)

    config['irancell']['auth']['phone'].set(phone)
    config['irancell']['auth']['password'].set(password)

    irancell = Irancell(config['irancell'])

    with yaspin(text=click.style('Authentication...', fg='white'), color="yellow") as spinner:
        try:
            irancell.authenticate()
            spinner.text = ''
            spinner.fail(click.style('Login Success', fg='green'))
        except:
            spinner.text = ''
            spinner.fail(click.style('Login Failed', fg='red'))
            return

    with open(config['config_path'].get(), 'a+') as f:
        f.seek(0)
        raw_config_file = yaml.load(f, Loader=yaml.FullLoader)
        raw_config_file['irancell']['auth']['phone'] = phone
        raw_config_file['irancell']['auth']['password'] = password
        f.truncate(0)
        f.write(yaml.dump(raw_config_file))


@click.option('--force', is_flag=True, default=False, prompt='Are you sure to remove session keys')
@irancell.command()
def logout(force):
    if force:
        with open(config['config_path'].get(), 'a+') as f:
            f.seek(0)
            raw_config_file = yaml.load(f, Loader=yaml.FullLoader)
            raw_config_file['irancell']['auth']['phone'] = ''
            raw_config_file['irancell']['auth']['password'] = ''
            f.truncate(0)
            f.write(yaml.dump(raw_config_file))


@irancell.command()
def status():
    with yaspin(text=click.style('Authentication...', fg='white'), color="yellow") as spinner:
        irancell = Irancell(config['irancell'])
        irancell.authenticate()
        spinner.text = 'Getting Information...'
        balance, offers = irancell.get_account_balance_and_offers()

    click.echo(get_balance_info(balance, MAIN_COLOR))
    click.echo()

    table = get_active_offers_table(offers, MAIN_COLOR)
    click.echo(table.table)


@click.option('--no-time-limit', is_flag=True, default=False)
@click.option('--max-price', type=int, default=None)
@click.option('--limit', type=int, default=None)
@click.option('--sort-by', default='price', type=click.Choice(SORT_OPTIONS))
@click.option('--desc', is_flag=True, default=False)
@offers.command()
def show(no_time_limit, max_price, limit, sort_by, desc):
    with yaspin(text=click.style('Authentication...', fg='white'), color="yellow") as spinner:
        irancell = Irancell(config['irancell'])
        irancell.authenticate()
        spinner.text = 'Getting Information...'
        offers = irancell.get_offers()

    offers = filtered_offers(offers, sort_by, desc, max_price, no_time_limit, limit)
    table = get_offers_table(offers, MAIN_COLOR)

    balance, _ = irancell.get_account_balance_and_offers()
    balance_info = get_balance_info(balance, MAIN_COLOR)

    if len(offers) > 20:
        click.echo_via_pager(balance_info + '\n\n' + table.table)
    else:
        click.echo(balance_info + '\n\n' + table.table)


@click.argument('id', type=str)
@click.option('--force', is_flag=True, default=False)
@offers.command()
def buy(id, force):
    with yaspin(text=click.style('Authentication...', fg='white'), color="yellow") as spinner:
        irancell = Irancell(config['irancell'])
        irancell.authenticate()
        spinner.text = 'Getting Information...'
        balance, _ = irancell.get_account_balance_and_offers()
        offers = irancell.get_offers()

    results = list(filter(lambda o: o.hash == id, offers))

    if len(results) == 0:
        return click.echo(click.style('Id not found', fg='red'))
    elif len(results) > 1:
        return click.echo(click.style('Duplicate Id, please report this bug.', fg='red'))

    [offer] = results

    if not force:
        click.echo(get_offer_information(offer, MAIN_COLOR))
        click.echo()
        click.echo(get_payment_info(balance, offer.price, MAIN_COLOR))

        if balance < offer.price:
            return click.echo(click.style('* not enough money to buy this offer *', fg='red'))

        click.echo()
        click.confirm('Ary you sure?', abort=True)

        with yaspin(text=click.style('Purchasing...', fg=MAIN_COLOR), color="yellow"):
            irancell.buy_offer(offer.id)

        click.echo(click.style('purchase complete.', fg='green'))
