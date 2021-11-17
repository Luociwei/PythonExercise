# -*- coding: utf-8 -*-
from pin_emulator import PinEmulator


class Pin(object):
    '''
    Pin function class which provide function to set control

    ClassType = GPIO

    level and direction of a pin in chip.

    Args:
        io:      instance/None, io instance, if not using, will create emulator.
        pin_id:  int, [0],      io pin id.

    Examples:
        i2c = I2C('/dev/i2c-0')
        cat9555 = CAT9555(0x20, i2c)
        pin = Pin(cat9555, 0)

        # set pin output level high
        pin.set_dir('output')
        pin.set_level(1)

        # get pin input level
        pin.set_dir('input')
        level = pin.get_level()
        # level == 0 for low level, level == 1 for high level
        print('level={}'.format(level))

        # get pin direction
        dir = pin.get_dir()
        print('dir={}'.format(dir))

    '''
    rpc_public_api = [
        'get_level',
        'set_level',
        'get_dir',
        'set_dir'
    ]

    def __init__(self, io, pin_id, pin_dir=None):
        if io is None:
            self.io = PinEmulator("pin_emualtor")
        else:
            self.io = io
        self.pin_id = pin_id
        if pin_dir:
            self.set_dir(pin_dir)

    def get_level(self):
        '''
        Get level of the pin.

        Returns:
            int, value.

        '''
        return self.io.get_pin(self.pin_id)

    def set_level(self, level):
        '''
        Set level of pin.

        Args:
            level: int, [0, 1], 1 is high level, 0 is low level.

        '''
        assert level in [0, 1]
        self.io.set_pin(self.pin_id, level)
        return 'done'

    # level property to be used locally like 'pin.level=1' or 'print pin.level'
    level = property(fset=set_level, fget=get_level)

    def get_dir(self):
        '''
        Get direction of pin.

        Returns:
            string, type is lower-case string, 'input' or 'output'

        '''
        return self.io.get_pin_dir(self.pin_id)

    def set_dir(self, pin_dir):
        '''
        Set direction of pin.

        Args:
            pin_dir:  string, ['input', 'output'], Set the io direction.

        '''
        assert pin_dir in ['input', 'output']
        self.io.set_pin_dir(self.pin_id, pin_dir)
        return 'done'

    # direction property to be used locally like
    #   pin.direction =  'output'
    # or
    #   print pin.direction
    direction = property(fset=set_dir, fget=get_dir)
