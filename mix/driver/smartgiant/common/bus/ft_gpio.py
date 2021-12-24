# -*- coding: utf-8 -*-
import ctypes
import time
from mix.driver.smartgiant.common.bus.ft4222 import FT4222


__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class FTGPIOException(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class FTGPIO(object):

    # class variable to host all FT4222 instances created.
    instances = {}

    def __new__(cls, ft4222=None, delay=0):
        if ft4222 in cls.instances:
            # use existing instance
            pass
        else:
            # create a new one
            instance = _FTGPIO(ft4222, delay)
            cls.instances[ft4222] = instance
        return cls.instances[ft4222]


class _FTGPIO(object):
    '''
    MIXGPIOSG function class

    Args:
        ft4222:   instance/None/string/int,  Class instance of FT4222 bus or locid of FT4222 device.
        delay:    int,            Optional delay between Init and Write (in miliseconds) in FT4222H.

    Examples:
        ft4222 = FT4222('4593')
        ftgpio = MIXGPIOSG(ft4222, 1)

    '''

    def __init__(self, ft4222=None, delay=0):
        if ft4222 is None:
            self._ft_4222 = FT4222(None)
        elif isinstance(ft4222, (int, basestring)):
            self._ft_4222 = FT4222(ft4222)
        else:
            self._ft_4222 = ft4222

        self._base_lib = self._ft_4222._base_lib
        self._fthandle = self._ft_4222._fthandle
        self._delay = float(delay) / 1000
        # pin dir:0=out 1=in
        self._pin0_dir = 0
        self._pin1_dir = 0
        self._pin2_dir = 0
        self._pin3_dir = 0

    def set_pin_dir(self, pin_id, dir):
        '''
        MIXGPIOSG set direction of specific pin

        Examples:
            pin_id: int, [0~3], Set direction of this pin
            dir:    string, ['input'/'output'],   Set pin specific direction

        Examples:
            ftgpio.set_pin_dir(0, 'output')
        '''

        assert dir in ['output', 'input']

        self._ft_4222.open()
        if pin_id == 0 and dir == 'input':
            self._pin0_dir |= 1
        elif pin_id == 0 and dir == 'output':
            self._pin0_dir &= 0
        elif pin_id == 1 and dir == 'input':
            self._pin1_dir |= 1
        elif pin_id == 1 and dir == 'output':
            self._pin1_dir &= 0
        elif pin_id == 2 and dir == 'input':
            self._pin2_dir |= 1
        elif pin_id == 2 and dir == 'output':
            self._pin2_dir &= 0
        elif pin_id == 3 and dir == 'input':
            self._pin3_dir |= 1
        elif pin_id == 3 and dir == 'output':
            self._pin3_dir &= 0
        else:
            raise FTGPIOException('FT4222H set pin id out of range(0 ,1 ,2, 3)')

        gpioDir = (ctypes.c_ubyte * 4)()
        gpioDir[0] = self._pin0_dir
        gpioDir[1] = self._pin1_dir
        gpioDir[2] = self._pin2_dir
        gpioDir[3] = self._pin3_dir
        ftstatus = self._base_lib.FT4222_GPIO_Init(self._fthandle, gpioDir)
        if ftstatus != 0:
            raise FTGPIOException('FT4222_GPIO_Init')

    def get_pin_dir(self, pin_id):
        '''
        FTGPIO get direction of specific pin

        Args:
            pin_id:     int, [0~3], Get direction of this pin

        Examples:
            dir = ftgpio.get_pin_dir(0)
            print(dir)
        '''

        if pin_id == 0:
            return self._pin0_dir
        elif pin_id == 1:
            return self._pin1_dir
        elif pin_id == 2:
            return self._pin2_dir
        elif pin_id == 3:
            return self._pin3_dir
        else:
            raise FTGPIOException('FT4222H get pin id out of range(0 ,1 ,2, 3)')

    def set_pin(self, pin_id, level):
        '''
        FTGPIO set specific pin level

        Args:
            pin_id: int, [0~3], Get direction of this pin
            level:  int, [0, 1],   0 for low level, 1 for high level

        Examples:
            ftgpio.set_pin(0, 0)  # set pin 0 level low
        '''
        assert pin_id in [0, 1, 2, 3]
        assert level in [0, 1]

        self._ft_4222.open()
        gpioDir = (ctypes.c_ubyte * 4)()
        gpioDir[0] = self._pin0_dir
        gpioDir[1] = self._pin1_dir
        gpioDir[2] = self._pin2_dir
        gpioDir[3] = self._pin3_dir
        ftstatus = self._base_lib.FT4222_GPIO_Init(self._fthandle, gpioDir)
        if ftstatus != 0:
            raise FTGPIOException('FT4222_GPIO_Init')

        enable = ctypes.c_bool(0)
        ftstatus = self._base_lib.FT4222_SetSuspendOut(self._fthandle, enable)
        if ftstatus != 0:
            raise FTGPIOException('FT4222_SetSuspendOut')

        enable = ctypes.c_bool(0)
        ftstatus = self._base_lib.FT4222_SetWakeUpInterrupt(self._fthandle, enable)
        if ftstatus != 0:
            raise FTGPIOException('FT4222_SetWakeUpInterrupt')

        if (self._delay > 0):
            time.sleep(self._delay)

        if level != 0:
            value = ctypes.c_bool(1)
        else:
            value = ctypes.c_bool(0)
        ftstatus = self._base_lib.FT4222_GPIO_Write(self._fthandle, pin_id, value)
        if ftstatus != 0:
            raise FTGPIOException('FT4222_GPIO_Write')

    def get_pin(self, pin_id):
        '''
        FTGPIO get specific pin level

        Args:
            pin_id:     int, [0~3], Get direction of this pin

        Examples:
            level = ftgpio.get_pin(0)
            print(level)
        '''
        assert pin_id in [0, 1, 2, 3]

        self._ft_4222.open()
        gpioDir = (ctypes.c_ubyte * 4)()
        gpioDir[0] = self._pin0_dir
        gpioDir[1] = self._pin1_dir
        gpioDir[2] = self._pin2_dir
        gpioDir[3] = self._pin3_dir
        ftstatus = self._base_lib.FT4222_GPIO_Init(self._fthandle, gpioDir)
        if ftstatus != 0:
            raise FTGPIOException('FT4222_GPIO_Init')

        enable = ctypes.c_bool(0)
        ftstatus = self._base_lib.FT4222_SetSuspendOut(self._fthandle, enable)
        if ftstatus != 0:
            raise FTGPIOException('FT4222_SetSuspendOut')

        enable = ctypes.c_bool(0)
        ftstatus = self._base_lib.FT4222_SetWakeUpInterrupt(self._fthandle, enable)
        if ftstatus != 0:
            raise FTGPIOException('FT4222_SetWakeUpInterrupt')

        level = ctypes.c_bool(0)
        ftstatus = self._base_lib.FT4222_GPIO_Read(self._fthandle, pin_id, ctypes.byref(level))
        if ftstatus != 0:
            raise FTGPIOException('FT4222_GPIO_Read')

        return int(level.value)
