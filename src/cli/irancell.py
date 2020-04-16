import click
from yaspin import yaspin
from src.config import config
import yaml
from src.services.irancell.irancell import Irancell
from terminaltables import AsciiTable
from src.models.enums import IrancellServiceType
from src.util.humanreadable import size_string as hr_size, to_time_string
from hashlib import md5

MAIN_COLOR = 'yellow'
SORT_OPTIONS = ['id', 'name', 'type', 'size', 'international', 'local', 'price', 'unit-price', 'duration']


@click.group()
def irancell():
    pass


@irancell.command()
@click.option('--phone', type=str)
@click.option('--password', type=str)
@click.option('--overwrite', is_flag=True, default=False)
def login(phone, password, overwrite):
    if not overwrite and config['irancell']['auth']['phone']:
        click.confirm('Login config exist, are you sure to overwrite it?', abort=True)

    phone = click.prompt('Enter your phone number', type=str)
    password = click.prompt('Enter your password', type=str, hide_input=True)

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

    sort_func = {
        'type': lambda o: 0,
        'name': lambda o: str(o),
        'size': lambda o: o.get_total_size(),
        'international': lambda o: o.get_total_size(IrancellServiceType.INTERNATIONAL),
        'local': lambda o: o.get_total_size(IrancellServiceType.LOCAL),
        'price': lambda o: o.price,
        'unit-price': lambda o: o.get_unit_price(),
        'duration': lambda o: o.duration,
    }

    if sort_by:
        offers.sort(key=sort_func[sort_by], reverse=desc)

    if max_price is not None:
        offers = list(filter(lambda o: o.price <= max_price * 10, offers))

    if no_time_limit:
        offers = list(filter(lambda o: any(map(lambda v: not v.limitation_hours, o.volumes)), offers))

    if limit is not None:
        offers = offers[:limit]

    table_data = [
        [
            click.style('Id', bold=True),
            click.style('Name', bold=True),
            click.style('Duration', bold=True),
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
            click.style(md5(offer.id.encode()).hexdigest()[5:10], fg=MAIN_COLOR),
            click.style(str(offer), fg=MAIN_COLOR),
            click.style(to_time_string(offer.duration), fg=MAIN_COLOR),
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

    results = list(filter(lambda o: md5(o.id.encode()).hexdigest()[5:10] == id, offers))

    if len(results) == 0:
        return click.echo(click.style('Id not found', fg='red'))
    elif len(results) > 1:
        return click.echo(click.style('Bad Id, please report this bug.', fg='red'))

    [target_offer] = results

    if not force:

        international_msg = []
        local_msg = []
        for volume in target_offer.volumes:
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

        click.echo(click.style('name: ') + click.style(str(target_offer), bold=True, fg=MAIN_COLOR))
        click.echo(click.style('duration: ') + click.style(to_time_string(target_offer.duration), bold=True, fg=MAIN_COLOR))
        click.echo(click.style('international: ') + click.style(' + '.join(international_msg) or '-', bold=True, fg=MAIN_COLOR))
        click.echo(click.style('local: ') + click.style(' + '.join(local_msg) or '-', bold=True, fg='red'))
        click.echo()

        click.echo(click.style('balance: ', fg='white')
                   + click.style(
            '{:0,.0f} Toman -> {:0,.0f} Toman'.format(balance / 10, balance / 10 - target_offer.price // 10),
            fg=MAIN_COLOR,
            bold=True
        ))

        click.echo(click.style('offer price: ', fg='white')
                   + click.style('{:0,.0f} Toman'.format(target_offer.price // 10), fg='red', bold=True))

        if balance < target_offer.price:
            return click.echo(click.style('* not enough money to buy this offer *', fg='red'))

        click.echo()
        click.confirm('Ary you sure to buy this package?', abort=True)

        with yaspin(text=click.style('Purchasing...', fg=MAIN_COLOR), color="yellow") as spinner:
            irancell.buy_offer(target_offer.id)

        click.echo(click.style('purchase complete.', fg='green'))
