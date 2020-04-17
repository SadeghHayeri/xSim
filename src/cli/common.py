import click
from terminaltables import AsciiTable
from src.models.enums import IrancellServiceType
from src.util.humanreadable import size_string as hr_size, to_time_string, to_toman


def get_colorful_table(title, header, table_data, title_color, header_color, data_color):
    colorful_header = [click.style(name, bold=True, fg=header_color) for name in header]
    colorful_data = [[click.style(name, fg=data_color) if name else '' for name in row] for row in table_data]

    table = AsciiTable([colorful_header] + colorful_data, click.style(title, fg=title_color))

    for i in range(len(table_data[0])):
        table.justify_columns[i] = 'center'

    return table


def get_colorful_key_value(key, value, color):
    return click.style(key + ': ', fg=color) + click.style(value, fg=color, bold=True)


def get_limitation_hours_string(volume):
    if volume.limitation_hours:
        return ' ({}{}-{}{})'.format(
            volume.limitation_hours[0]['hour'],
            volume.limitation_hours[0]['type'],
            volume.limitation_hours[1]['hour'],
            volume.limitation_hours[1]['type'],
        )
    return ''


def get_international_and_internal_strings(offer, with_remaining=False):
    international = []
    internal = []
    for volume in offer.volumes:
        name = hr_size(volume.size) + get_limitation_hours_string(volume)

        if with_remaining:
            name = '{} / {}'.format(hr_size(volume.remaining), name)

        if volume.type == IrancellServiceType.INTERNATIONAL:
            international.append(name)
        elif volume.type == IrancellServiceType.INTERNAL:
            internal.append(name)
    return international, internal


def get_offers_table(offers, color):
    header = ['Id', 'Name', 'Duration', 'Type', 'International', 'Internal', 'Price', 'Unit Price']

    table_data = []
    for i, offer in enumerate(offers):
        international_strings, internal_strings = get_international_and_internal_strings(offer)
        table_data.append([
            offer.hash,
            str(offer),
            to_time_string(offer.duration),
            offer.type,
            ' + '.join(international_strings),
            ' + '.join(internal_strings),
            to_toman(offer.price),
            to_toman(offer.get_unit_price()),
        ])

    return get_colorful_table('Offers', header, table_data, color, 'white', color)


def get_active_offers_table(offers, color):
    header = ['Id', 'Name', 'Duration', 'Type', 'International', 'Internal', 'Expire Time']

    table_data = []
    for i, offer in enumerate(offers):
        international_strings, internal_strings = get_international_and_internal_strings(offer, with_remaining=True)
        table_data.append([
            offer.hash,
            str(offer),
            to_time_string(offer.duration),
            offer.type,
            ' + '.join(international_strings),
            ' + '.join(internal_strings),
            str(offer.expire_time),
        ])

    return get_colorful_table('Active Offers', header, table_data, color, 'white', color)


def get_offer_information(offer, color):
    result = []
    inters, internals = get_international_and_internal_strings(offer)
    result.append(get_colorful_key_value('Name', str(offer), color))
    result.append(get_colorful_key_value('Duration', to_time_string(offer.duration), color))
    result.append(get_colorful_key_value('International', ' + '.join(inters), color))
    result.append(get_colorful_key_value('Internal', ' + '.join(internals) or '-', color))

    if internals:
        result[len(result) - 1] += click.style(' (USELESS)', fg='red')
    return '\n'.join(result)


def filtered_offers(offers, sort_by, desc, max_price, no_time_limit, limit_count):
    sort_functions = {
        'type': lambda o: 0,
        'name': lambda o: str(o),
        'size': lambda o: o.get_total_size(),
        'international': lambda o: o.get_total_size(IrancellServiceType.INTERNATIONAL),
        'internal': lambda o: o.get_total_size(IrancellServiceType.INTERNAL),
        'price': lambda o: o.price,
        'unit-price': lambda o: o.get_unit_price(),
        'duration': lambda o: o.duration,
    }

    if sort_by:
        offers.sort(key=sort_functions[sort_by], reverse=desc)

    if max_price is not None:
        offers = list(filter(lambda o: o.price <= max_price * 10, offers))

    if no_time_limit:
        offers = list(filter(lambda o: any(map(lambda v: not v.limitation_hours, o.volumes)), offers))

    if limit_count is not None:
        offers = offers[:limit_count]

    return offers


def get_balance_info(balance, color):
    return click.style('Balance: ', fg=color) + click.style(to_toman(balance), fg=color, bold=True)


def get_payment_info(balance, price, color):
    result = [
        get_colorful_key_value('Price', to_toman(price), color),
        '{} -> {}'.format(
            get_balance_info(balance, color),
            click.style(to_toman(balance - price), fg=color, bold=True)
        )
    ]
    return '\n'.join(result)
