# -*- coding: UTF-8 -*-
from ..bus.pin import Pin


class IOExpanderBase(object):
    '''
    Base Class for all IO Expander like CAT9555
    '''
    rpc_public_api = [
        'read_register', 'write_register', 'set_pin_dir', 'get_pin_dir',
        'set_pin', 'get_pin', 'get_pin_state',
        'set_pin_inversion', 'get_pin_inversion', 'set_pins_dir', 'get_pins_dir',
        'get_ports', 'set_ports', 'get_ports_state',
        'set_ports_inversion', 'get_ports_inversion'
    ]

    def __init__(self):
        # list of downstream buses created.
        self.ports = {}

    def __getitem__(self, index):
        '''
        Support cat9555[1] --> Pin(cat9555, 1)
        '''
        return self.pin(index)

    def pin(self, port):
        '''
        Return a Pin instance for given port;
        Create one of not created for the port before;
        Reuse exsiting one if already created.
        '''
        assert type(port) is int
        assert port >= 0

        if port not in self.ports:
            pin = Pin(self, port)
            self.ports[port] = pin

        return self.ports[port]
