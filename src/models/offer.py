from src.util.humanreadable import size_string as hr_size


class Volume:
    def __init__(self, volume_type, value, limitation_hours = None):
        self.type = volume_type
        self.value = value
        self.limitation_hours = limitation_hours


class Offer:
    def __init__(self, fa_name, id=None, start_time=None, expire_time=None):
        self.duration = None
        self.fa_name = fa_name
        self.volumes = []

    def set_duration(self, duration):
        self.duration = duration

    def add_value(self, volume_type, value, limitation_hours = None):
        self.volumes.append(Volume(volume_type, value, limitation_hours))

    def set_id(self, id):
        self.id = id

    def set_start_time(self, start_time):
        self.start_time = start_time

    def set_expire_time(self, expire_time):
        self.expire_time = expire_time

    # def __str__(self):
    #     string = '{}/{}'.format(hr_size(self.remaining_size), hr_size(self.total_size))
    #     if self.limitation_time:
    #         string += ' ({}{}-{}{})'.format(self.limitation_time[0]['hour'], self.limitation_time[0]['type'],
    #                                         self.limitation_time[1]['hour'], self.limitation_time[1]['type'])
    #     return string
