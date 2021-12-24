# -*- coding: UTF-8 -*-
import math
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.1'


class AD527xDef:
    '''
    AD527xDef shows the registers address of AD527x
    AD5272 resolution is 10 bits, AD5274 resolution is 8 bits.
    '''
    WRITE_TO_RDAC = 0x1
    READ_FROM_RDAC = 0x2
    WRITE_TO_CONTROL = 0x7
    READ_FROM_CONTROL = 0x8
    SOFTWARE_SHUTDOWN = 0x9


class AD527xException(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class AD527x(object):
    '''
    AD527x digital rheostat function class

    ClassType = ADC

    Args:
        dev_addr:    hexmial, I2C device address of AD527x.
        i2c_bus:     instance(I2C)/None, Class instance of I2C bus, if not using this parameter, will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        AD527x = AD527x(0x50, i2c)
    '''

    def __init__(self, dev_addr, i2c_bus=None):
        # the ad527x i2c address is seven bits, but high five bits is 0b101100
        assert (dev_addr & (~0xD3)) == 0x2c
        self.dev_addr = dev_addr
        self.resolution = 10
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator('ad5272_emulator', 256)
        else:
            self.i2c_bus = i2c_bus

    def write_command(self, command, data):
        '''
        AD527x write data to AD527X through the commands,
        these commands are similar to register address.

        Args:
            command:    hexmial, [0~0xF], Write datas to this address.
            data:       hexmial, [0~0x3FF], Data for register.

        Examples:
            # Need to send the 0x2 to allow update of
            # wiper position through a digital interface
            AD527x.write_command(0x00, 0x2)

        '''
        assert type(data) is int and command in range(0xF)

        if command == 0x7 or command == 0x9:
            write_data = [command << 2, data & 0xf]
        else:
            if self.resolution == 10:
                write_data = [command << 2 | (data >> 8 & 0x3), data & 0xff]
            else:
                write_data = [(command << 2) |
                              ((data >> 6) & 0x3), (data & 0x3f) << 2]
        self.i2c_bus.write(self.dev_addr, write_data)

    def read_command(self, command):
        '''
        AD527x read data through the commands,
        these commands are similar to register address.

        Args:
            command:    hexmial, [0~0xF], Write datas to this address.

        Returns:
            list.

        Examples:
            recv_byte = AD527x.read_command(0x00)
            print (recv_byte)

        '''
        # tell AD527x that I'm going to read
        assert command in range(0xF)
        self.write_command(command, 0x00)
        # read 2 bytes from AD527x
        recv_byte = self.i2c_bus.read(self.dev_addr, 2)
        return recv_byte

    def get_resistor(self):
        '''
        AD527x get the resistor data from RDAC wiper register.

        Returns:
            float, value, unit ohm.

        Examples:
            resistor = AD527x.get_resistor()

        '''
        reg = self.read_command(AD527xDef.READ_FROM_RDAC)
        read_data = (reg[0] << 8) | reg[1]
        # default 100KΩ, general formula is use the resolution and nominal
        # resistance to calculate
        resistor = (read_data &
                    0x3FF) / math.pow(2, self.resolution) * math.pow(10, 5)
        return resistor  # unit: ohm

    def set_resistor(self, resistor):
        '''
        AD527x set the resistor data to RDAC.
        If the resistor data is a multiple of (max output of resistor / 2^resolution),
        the actual resistor of AD527X is less then resistor data that you set.
        eg:
            The max output resistor of AD5272 is 100Khom,and the resolution is 10,
            so the step value is 100Kohm / 2^10 = 97.65625 ohm
            if the resistor you want to output is 2000 ohm, the
            actual output of resistor is 1953.125 ohm(20 times of 97.65625 ohm)

        Args:
            resistor:   float, [0~100000], unit ohm,  resistor data.

        Examples:
            AD527x.set_resistor(4583.9)

        '''
        # default 100KΩ, against general formula can get the resistor
        data = int(resistor / math.pow(10, 5) *
                   math.pow(2, self.resolution))
        # send 0x1 command to write contents of serial register data to RDAC
        self.write_command(AD527xDef.WRITE_TO_RDAC, data)

    def set_work_mode(self, work_mode):
        '''
        AD527x software shutdown.

        Args:
            work_mode:  string, ["normal", "shutdown"], Set the mode.

        Examples:
            AD527x.set_resistor("shutdown")

        '''
        assert work_mode in ['normal', 'shutdown']
        data = 0x0
        if 'normal' == work_mode:
            data = 0x0
        elif 'shutdown' == work_mode:
            data = 0x1
        # set AD527x work mode
        self.write_command(AD527xDef.SOFTWARE_SHUTDOWN, data)

    def set_control_register(self, reg_data):
        '''
        AD527x set the control data to control register.

        Args:
            reg_data:     int, [0~0x7], Set control register.

        Examples:
            AD527x.set_control_registers(0x6)

        '''
        assert type(reg_data) is int and reg_data in range(0x7)
        # send 0x7 command to write contents of the serial register data
        # to the control register.
        self.write_command(AD527xDef.WRITE_TO_CONTROL, reg_data)

    def get_control_register(self):
        '''
        AD527x get the control data from  control register.

        Returns:
            int, value.

        Examples:
            reg_data = AD527x.get_control_register()
            print(reg_data)

        '''
        # send 0x8 command to read contents of the control register.
        reg_data = self.read_command(AD527xDef.READ_FROM_CONTROL)
        # only last four bit valid
        return reg_data[1] & 0xF


class AD5274(AD527x):
    '''
    AD5274 digital rheostat function class, its resolution is 8

    ClassType = ADC

    Args:
        dev_addr:    hexmial, I2C device address of AD527x.
        i2c_bus:     instance(I2C)/None, Class instance of I2C bus, if not using this parameter, will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        AD5274 = AD5274(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        super(AD5274, self).__init__(dev_addr, i2c_bus)
        self.resolution = 8


class AD5272(AD527x):
    '''
    AD5272 digital rheostat function class, its resolution is 10

    ClassType = ADC

    Args:
        dev_addr:    hexmial, I2C device address of AD527x.
        i2c_bus:     instance(I2C)/None, Class instance of I2C bus, if not using this parameter, will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        AD5272 = AD5272(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        super(AD5272, self).__init__(dev_addr, i2c_bus)
        self.resolution = 10
