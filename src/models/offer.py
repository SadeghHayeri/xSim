from src.util.humanreadable import size_string as hr_size
from src.models.enums import IrancellServiceType

class Volume:
    def __init__(self, volume_type, value, limitation_hours=None):
        self.type = volume_type
        self.value = value
        self.remaining = None
        self.limitation_hours = limitation_hours

    def __str__(self):
        if self.type == IrancellServiceType.CHARKHONE:
            return str(self.value) + 'T'

        if self.remaining:
            string = '{}/{}'.format(hr_size(self.remaining), hr_size(self.value))
        else:
            string = hr_size(self.value)

        string += ' I' if self.type == IrancellServiceType.INTERNATIONAL else ' L'

        if self.limitation_hours:
            string += ' ({}{}-{}{})'.format(self.limitation_hours[0]['hour'], self.limitation_hours[0]['type'],
                                            self.limitation_hours[1]['hour'], self.limitation_hours[1]['type'])
        return string


class Offer:
    def __init__(self, fa_name, id=None, start_time=None, expire_time=None):
        self.id = id
        self.start_time = start_time
        self.expire_time = expire_time
        self.duration = None
        self.fa_name = fa_name
        self.volumes = []

    def set_duration(self, duration):
        self.duration = duration

    def add_value(self, volume_type, value, limitation_hours=None):
        self.volumes.append(Volume(volume_type, value, limitation_hours))

    def set_id(self, id):
        self.id = id

    def set_start_time(self, start_time):
        self.start_time = start_time

    def set_expire_time(self, expire_time):
        self.expire_time = expire_time

    def __str__(self):
        return ' - '.join([str(volume) for volume in self.volumes])
