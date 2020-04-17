from src.util.humanreadable import size_string as hr_size, to_time_string
from src.models.enums import IrancellServiceType
from math import inf
from hashlib import md5


class Volume:
    def __init__(self, volume_type, size, limitation_hours=None):
        self.type = volume_type
        self.size = size
        self.remaining = None
        self.limitation_hours = limitation_hours

    def set_remaining(self, remaining):
        self.remaining = remaining

    def set_size(self, size):
        self.size = size

    def set_limitation_hours(self, limitation_hours):
        self.limitation_hours = limitation_hours

    def __str__(self):
        if self.type == IrancellServiceType.CHARKHONE:
            return str(self.size) + 'T'

        string = hr_size(self.size)
        string += ' '
        string += 'I' if self.type == IrancellServiceType.INTERNATIONAL else 'L'

        if self.limitation_hours:
            string += ' ({}{}-{}{})'.format(self.limitation_hours[0]['hour'], self.limitation_hours[0]['type'],
                                            self.limitation_hours[1]['hour'], self.limitation_hours[1]['type'])
        return string


class Offer:
    def __init__(self, fa_name, id=None, start_time=None, expire_time=None):
        self.id = id
        self.hash = md5(id.encode()).hexdigest()[5:10] if id else None
        self.start_time = start_time
        self.expire_time = expire_time
        self.duration = None
        self.fa_name = fa_name
        self.price = None
        self.volumes = []
        self.expiry_day = None
        self.auto_renew = None
        self.type = 'Internet'

    def set_duration(self, duration):
        self.duration = duration

    def add_volume(self, volume_type, size, limitation_hours=None):
        self.volumes.append(Volume(volume_type, size, limitation_hours))

    def set_id(self, id):
        self.id = id
        self.hash = md5(id.encode()).hexdigest()[5:10]

    def set_start_time(self, start_time):
        self.start_time = start_time

    def set_expire_time(self, expire_time):
        self.expire_time = expire_time

    def get_unit_price(self, count_limit_hours=True, count_local=False):
        total_size = 0
        for volume in self.volumes:

            if (not volume.limitation_hours or count_limit_hours) \
                    and (volume.type == IrancellServiceType.INTERNATIONAL or count_local):
                total_size += volume.size

        if total_size == 0:
            return inf

        if self.price is None:
            return None

        return int(self.price / (total_size / 1024 ** 3))

    def get_total_size(self, target_type=None):
        total_size = 0
        for volume in self.volumes:
            if not target_type or volume.type == target_type:
                total_size += volume.size
        return total_size

    def __str__(self):
        return to_time_string(self.duration) + ' ' + ' + '.join([str(volume) for volume in self.volumes])
