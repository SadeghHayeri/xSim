from src.util.humanreadable import size as hr_size


class Offer:
    def __init__(self, id, name, start, end, total_size, remaining_size, limitation_time=None):
        self.id = id
        self.name = name
        self.start = start
        self.end = end
        self.total_size = total_size
        self.remaining_size = remaining_size
        self.used_size = total_size - remaining_size
        self.limitation_time = limitation_time

    def __str__(self):
        string = '{}/{}'.format(hr_size(self.remaining_size), hr_size(self.total_size))
        if self.limitation_time:
            string += ' ({}{}-{}{})'.format(self.limitation_time[0]['hour'], self.limitation_time[0]['type'],
                                            self.limitation_time[1]['hour'], self.limitation_time[1]['type'])
        return string
