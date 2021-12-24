# -*- coding: UTF-8 -*-
from array import *

from ...bus.i2c_bus_emulator import I2CBusEmulator
from register_definitions import *
from hi_functions import *

__author__ = 'yongjiu@SmartGiant' + 'tianrun.lin@SmartGiant' + 'zhangsong.deng@SmartGiant'
__version__ = '0.2'


class TPS6598xDef():
    EMULATOR_REG_SIZE = 256
    DEVICE_MASK = 0x60
    DEVICE_ID = 0x20
    REG_MAX_ADDR = 0x7f
    REG_MIN_ADDR = 0x00
    REG_MAX_LEN = 69
    REG_MIN_LEN = 1


class TPS6598xException(Exception):
    def __init__(self, device_address, err_str):
        self._err_reason = '[0x%x] %s' % (device_address, err_str)

    def __str__(self):
        return self._err_reason


class TPS6598x(object):
    '''
    TPS6598x USB Type-C & USB PD Controller Power Switch  function class.

    ClassType = USB

    Args:
        device_address:      int, [0x20 ~ 0x3F], seven bit i2c address and top two bit is 0b01, eg.0x38.
        i2c_bus:             instance(I2C)/None, class instance of I2C bus, If not using, will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_I2C_1', 256)\r\n
        i2c = MIXI2CSG(axi)\r\n
        tps = TPS6598x(0x38, i2c)\r\n

    '''

    def __init__(self, device_address, i2c_bus=None):
        assert isinstance(device_address, int)
        assert (device_address & TPS6598xDef.DEVICE_MASK) == TPS6598xDef.DEVICE_ID

        self._dev_addr = device_address
        self._i2c_bus = i2c_bus or I2CBusEmulator('i2c_emulator', TPS6598xDef.EMULATOR_REG_SIZE)

    def write_reg(self, register_address, data):
        '''
        Write data into TPS6598x register

        Args:
            register_address:    int, [0x00~0x7F],  eg.0x08.
            data:                list, eg.[0x5A,0xA5].

        Raise:
            raise an Exception while i2c operation fail.

        Examples:
            tps.write_reg(0x08, [0x5A, 0xA5])\r\n

        '''
        assert isinstance(register_address, int)
        assert register_address >= TPS6598xDef.REG_MIN_ADDR
        assert register_address <= TPS6598xDef.REG_MAX_ADDR

        data_list = [register_address, len(data)]
        data_list += data

        self._i2c_bus.write(self._dev_addr, data_list)

    def read_reg(self, register_address, length):
        '''
        Read data from TPS6598x register

        Args:
            register_address:    int, [0x00~0x7F], eg.0x08.
            length:              int, [1~69], read bytes, eg.5.

        Returns:
            tuple, (read_data_length,register_data_array), eg.(5,array('B', [90,165,90,165]))

        Raise:
            raise an Exception while i2c operation fail.

        Examples:
            rd_data = tps.read_reg(0x08, 5)\r\n
            print(rd_data)\r\n

        '''
        assert isinstance(register_address, int)
        assert isinstance(length, int)
        assert register_address >= TPS6598xDef.REG_MIN_ADDR
        assert register_address <= TPS6598xDef.REG_MAX_ADDR
        assert length >= TPS6598xDef.REG_MIN_LEN
        assert length <= TPS6598xDef.REG_MAX_LEN

        read_data = self._i2c_bus.write_and_read(self._dev_addr, [register_address], length)
        # register data start with index 1 of the list
        return (len(read_data), array('B', read_data[1:]))
