def size_string(size, decimal_places=1):
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
