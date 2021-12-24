# -*- coding: utf-8 -*-
import os


class GPIOException(Exception):
    def __init__(self, err_str):
        self.err_reason = "GPIO {}".format(err_str)

    def __str__(self):
        return self.err_reason


class GPIODef:
    IO_PIN_OUTPUT = 0
    IO_PIN_INPUT = 1

    OUTPUT = 'output'
    INPUT = 'input'

    LEGACY_PS_GPIO_BASE_ID = 906
    PS_GPIO_MAX_PIN_ID = 117
    MAX_PIN_ID = 1023
    MIN_PIN_ID = 0

    INVERSION = 1
    NOT_INVERSION = 0

    HIGH_LEVEL = 1
    LOW_LEVEL = 0

    DEFAULT_OUTPUT_DICT = {0: 'low', 1: 'high'}


class GPIO(object):
    '''
    Singleton wrapper of Xilinx GPIO driver.

    ClassType = GPIO

    This is to ensure only 1 instance is created for the same gpio
    , even if instantiated multiple times.
    Please refer to _GPIO class docstring for parameters.

    Args:
        pin_id:          int, [0~1023],                 io pin id.
        default_dir:     string, ['input', 'output'],   set gpio default direction.
                                                        If not given, default direction is input.
        is_inversion:    int, [0, 1],                   0 for not inverse pin level, 1 for inverse pin level.

    Examples:
        GPIO_1 = GPIO(59, 'output')
        GPIO_2 = GPIO(59, 'output')
        assert GPIO_1 == GPIO_2          # True

    '''

    instances = {}

    def __new__(cls, pin_id=0, default_dir='input', is_inversion=0):
        assert isinstance(pin_id, int)
        assert isinstance(is_inversion, int)
        assert pin_id >= GPIODef.MIN_PIN_ID
        assert pin_id <= GPIODef.MAX_PIN_ID
        assert is_inversion in [GPIODef.NOT_INVERSION, GPIODef.INVERSION]

        if pin_id in cls.instances:
            # use existing instance
            pass
        else:
            # create a new one
            instance = _GPIO(pin_id, default_dir, is_inversion)
            cls.instances[pin_id] = instance
        return cls.instances[pin_id]


class _GPIO(object):
    '''
    This driver is used to control xilinx gpio device

    ClassType = GPIO

    Note that this driver just can create one pin instance.

    Args:
        pin_id:          int, [0~1023],                 io pin id.
        default_dir:     string, ['input', 'output'],   set gpio default direction.
                                                        If not given, default direction is input.
        is_inversion:    int, [0, 1],                   0 for not inverse pin level, 1 for inverse pin level.

    Examples:
        io = GPIO(59, 'output')  # user can control cat9555 pin0 by io instance.

    '''
    rpc_public_api = ['get_level', 'set_level', 'get_dir', 'set_dir']

    def __init__(self, pin_id=0, default_dir='input', is_inversion=0):

        # expand pin_id range to (0~1023) from (0~117), and compatible legacy (0~117)
        self.pin_num = pin_id if pin_id > GPIODef.PS_GPIO_MAX_PIN_ID else GPIODef.LEGACY_PS_GPIO_BASE_ID + pin_id
        self.is_inversion = is_inversion

        if False is os.path.exists('/sys/class/gpio/gpio{}'.format(self.pin_num)):
            export_fd = os.open('/sys/class/gpio/export', os.O_WRONLY)
            os.write(export_fd, '{}'.format(self.pin_num))
            os.close(export_fd)

        if False is os.path.exists('/sys/class/gpio/gpio{}'.format(self.pin_num)):
            raise GPIOException('open failed!')

        self.gpio_value_fd = os.open('/sys/class/gpio/gpio{}/value'.format(self.pin_num), os.O_RDWR)
        self.gpio_dir_fd = os.open('/sys/class/gpio/gpio{}/direction'.format(self.pin_num), os.O_RDWR)

        self.set_dir(default_dir)

    def __del__(self):
        os.close(self.gpio_value_fd)
        os.close(self.gpio_dir_fd)

        unexport_fd = os.open('/sys/class/gpio/unexport', os.O_WRONLY)

        os.write(unexport_fd, '{}'.format(self.pin_num))

        os.close(unexport_fd)

    def get_level(self):
        '''
        GPIO get pin level

        Returns:
            int, value.

        Examples:
            level = io.get_level()
            print(level)

        '''

        # commands.getstatusoutput return tuple: (state, result)
        os.lseek(self.gpio_value_fd, 0, 0)
        result = os.read(self.gpio_value_fd, 1)

        level = int(result) ^ self.is_inversion
        return level

    def set_level(self, level):
        '''
        GPIO set pin level

        Args:
            level:   int, [0], 1 is high level, 0 is low level.

        Examples:
            io.set_level(1)

        '''
        assert level in [GPIODef.LOW_LEVEL, GPIODef.HIGH_LEVEL]

        if self.is_inversion:
            level ^= 1  # inverse pin level

        os.write(self.gpio_value_fd, '{}'.format(level))

    # level property to be used locally like 'pin.level=1' or 'print pin.level'
    level = property(fset=set_level, fget=get_level)

    def get_dir(self):
        '''
        GPIO get pin direction

        Returns:
            string, str.

        Examples:
            dir = io.get_dir()
            print(dir)

        '''
        os.lseek(self.gpio_dir_fd, 0, 0)
        result = os.read(self.gpio_dir_fd, 3)
        # delete '\n' when reads back 3 bytes and get 'in\n' when gpio is set to input
        result = result.replace('\n', '')
        # result is 'in' or 'out'
        if result == 'in':
            return GPIODef.INPUT
        else:
            return GPIODef.OUTPUT

    def set_dir(self, pin_dir):
        '''
        GPIO set pin direction

        Args:
            pin_dir:     string, ["input", "output"], Set the io direction.

        Examples:
            io.set_dir('input')

        '''
        assert pin_dir in [GPIODef.INPUT, GPIODef.OUTPUT]

        # Set the direction if the set direction is different from the current one
        if self.get_dir() != pin_dir:
            # commands.getstatusoutput return tuple: (state, result)
            if pin_dir == GPIODef.INPUT:
                os.write(self.gpio_dir_fd, 'in')
            else:
                level = self.get_level()
                if self.is_inversion:
                    level = 0 if level else 1
                # If the default level is set to 0, direction set to low else direction set to high
                os.write(self.gpio_dir_fd, GPIODef.DEFAULT_OUTPUT_DICT[level])

    # direction property to be used locally like
    #   pin.direction =  'output'
    # or
    #   print pin.direction
    direction = property(fset=set_dir, fget=get_dir)
