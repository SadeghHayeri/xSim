from math import inf


def size_string(size, decimal_places=1):
    if size is None:
        return '?'

    if size is inf:
        return 'inf'

    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f'{size:.{decimal_places}f}{unit}'


def size_from_string(string):
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    for i, unit in enumerate(reversed(units)):
        if unit in string:
            number = int(string[:-len(unit)])
            return number * (1024 ** (4 - i))


def to_time_string(hours):
    days = hours / 24
    if days == 365:
        return '1 Year'

    if days % 365 == 0:
        return '{} Years'.format(int(days / 365))

    if days == 30:
        return '1 Month'

    if days % 30 == 0:
        return '{} Months'.format(int(days / 30))

    if days == 7:
        return '1 Week'

    if days % 7 == 0:
        return '{} Weeks'.format(int(days / 7))

    if hours == 24:
        return '1 day'

    if hours % 24 == 0:
        return '{} days'.format(int(hours / 24))

    if hours == 1:
        return '1 Hour'

    return '{} Hours'.format(int(hours))


def to_toman(price):
    return '?' if price is None else '{:0,.0f} Toman'.format(float(price / 10))
