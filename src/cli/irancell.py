import click
from yaspin import yaspin
from src.config import config
import yaml
from src.services.irancell.irancell import Irancell
from terminaltables import AsciiTable
from src.models.enums import IrancellServiceType
from src.util.humanreadable import size_string as hr_size

MAIN_COLOR = 'yellow'


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

    with yaspin(text=click.style('Authentication...', fg=MAIN_COLOR), color="yellow") as spinner:
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
    irancell = Irancell(config['irancell'])
    # irancell.authenticate()
    balance, offers = irancell.get_account_balance_and_offers()

    click.echo(click.style('Balance: ', fg=MAIN_COLOR)
               + click.style('{:0,.0f} Toman'.format(balance / 10), fg=MAIN_COLOR, bold=True))

    table_data = [
        ['Name', 'Type', 'International', 'Local', 'Limitation Hours', 'Price', 'Unit Price']
    ]

    for offer in offers:
        limitation_hours_msg = ''
        international_msg = ''
        local_msg = ''
        for volume in offer.volumes:
            if volume.limitation_hours:
                limitation_hours_msg += '{} ({}{}-{}{})'.format(hr_size(volume.size),
                                                                volume.limitation_hours[0]['hour'],
                                                                volume.limitation_hours[0]['type'],
                                                                volume.limitation_hours[1]['hour'],
                                                                volume.limitation_hours[1]['type'])

            elif volume.type == IrancellServiceType.INTERNATIONAL:
                international_msg += hr_size(volume.size)

            elif volume.type == IrancellServiceType.LOCAL:
                local_msg += hr_size(volume.size)

        table_data.append([
            str(offer),
            'Internet',
            international_msg,
            local_msg,
            limitation_hours_msg,
            '?' if offer.price is None else '{:0,.2f} Toman'.format(float(offer.price / 10)),
            '?' if offer.price is None else '{:0,.2f} Toman'.format(float(offer.get_unit_price() / 10)),
        ])

    table = AsciiTable(table_data, 'Active Offers')
    for i in range(len(table_data[0])):
        table.justify_columns[i] = 'center'
    print('')
    print(click.style(table.table, fg='yellow'))


@irancell.group()
def offers():
    pass


SORT_OPTIONS = ['id', 'name', 'type', 'size', 'international', 'local', 'price', 'unit-price']


@click.option('--limit', type=int, default=None)
@click.option('--sort-by', default='price', type=click.Choice(SORT_OPTIONS))
@click.option('--desc', is_flag=True, default=False)
@offers.command()
def show(limit, sort_by, desc):
    irancell = Irancell(config['irancell'])
    irancell.authenticate()
    offers = irancell.get_offers()

    sort_func = {
        'name': lambda o: str(o),
        'size': lambda o: o.get_total_size(),
        'international': lambda o: o.get_total_size(IrancellServiceType.INTERNATIONAL),
        'local': lambda o: o.get_total_size(IrancellServiceType.LOCAL),
        'price': lambda o: o.price,
        'unit-price': lambda o: o.get_unit_price(),
    }

    if sort_by:
        offers.sort(key=sort_func[sort_by])

    if limit is not None:
        offers = offers[:limit]

    table_data = [
        [
            click.style('Id', bold=True),
            click.style('Name', bold=True),
            click.style('Type', bold=True),
            click.style('International', bold=True),
            click.style('Local', bold=True),
            click.style('Price', bold=True),
            click.style('Unit Price', bold=True),
        ]
    ]

    for i, offer in enumerate(offers):
        international_msg = []
        local_msg = []
        for volume in offer.volumes:
            name = hr_size(volume.size)
            if volume.limitation_hours:
                name += ' ({}{}-{}{})'.format(volume.limitation_hours[0]['hour'],
                                              volume.limitation_hours[0]['type'],
                                              volume.limitation_hours[1]['hour'],
                                              volume.limitation_hours[1]['type'])

            if volume.type == IrancellServiceType.INTERNATIONAL:
                international_msg.append(name)

            elif volume.type == IrancellServiceType.LOCAL:
                local_msg.append(name)

        white_plus = click.style(' + ', fg='white')

        table_data.append([
            click.style(str(i + 1), fg=MAIN_COLOR),
            click.style(str(offer), fg=MAIN_COLOR),
            click.style('Internet', fg=MAIN_COLOR),
            white_plus.join(map(lambda m: click.style(m, fg=MAIN_COLOR), international_msg)),
            white_plus.join(map(lambda m: click.style(m, fg=MAIN_COLOR), local_msg)),
            click.style('?' if offer.price is None else '{:0,.0f} Toman'.format(float(offer.price / 10)),
                        fg=MAIN_COLOR),
            click.style('?' if offer.price is None else '{:0,.0f} Toman'.format(float(offer.get_unit_price() / 10)),
                        fg=MAIN_COLOR),
        ])

    table = AsciiTable(table_data, click.style('Offers', fg=MAIN_COLOR))
    for i in range(len(table_data[0])):
        table.justify_columns[i] = 'center'

    page = []
    balance, _ = irancell.get_account_balance_and_offers()
    page.append(click.style('Balance: ', fg=MAIN_COLOR)
                + click.style('{:0,.0f} Toman'.format(balance / 10), fg=MAIN_COLOR, bold=True))
    page.append('')
    page.append(table.table)

    if len(table_data) > 20:
        click.echo_via_pager('\n'.join(page))
    else:
        click.echo('\n'.join(page))
