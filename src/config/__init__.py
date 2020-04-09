from __future__ import division, absolute_import, print_function
import confuse
from os import path, makedirs

template = {
    'auth': {
        'phone': str,
        'password': str,
        'session': {
            'base_path': confuse.Filename(),
            'file_name': confuse.Filename(),
        },
    },
}

config = confuse.LazyConfig('manager', __name__)

config['irancell']['auth']['session']['path'] = path.join(config['irancell']['auth']['session']['base_path'].get(),
                                                          config['irancell']['auth']['session']['file_name'].get())
