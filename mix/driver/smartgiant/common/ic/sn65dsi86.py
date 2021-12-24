# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class SN65DSI86(object):
    '''
    SN65DSI86 function class

    ClassType = DAC

    Args:
        dev_addr:   hexmial,             i2c bus device address.
        i2c_bus:    instance(I2C)/None,  i2c bus instance, if not using, will create emulator.

    Examples:
        axi4_bus = AXI4LteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        sn65dsi86 = SN65DSI86(0x2c, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        assert (dev_addr & (~0x01)) == 0x2c
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator("sn65dsi86_emulator", 256)
        else:
            self.i2c_bus = i2c_bus
        self.dev_addr = dev_addr

    def write_register(self, reg_addr, wr_data):
        '''
        SN65DIS86 write data to register

        Args:
            reg_addr:   hexmial, [0~0xFF], register address.
            wr_data:    list,              list to write,eg:[0x12,0x23].

        Examples:
            sn65dsi86.write_register(0x01, [0x12,0x23])

        '''
        assert isinstance(reg_addr, int)
        assert isinstance(wr_data, list)
        assert reg_addr >= 0 and reg_addr <= 0xFF

        data = [reg_addr]
        data.extend(wr_data)
        self.i2c_bus.write(self.dev_addr, data)

    def read_register(self, reg_addr, rd_len=1):
        '''
        SN65DSI86 read data from register

        Args:
            reg_addr:   hexmial, [0~0xFF], register address.
            rd_len:     int, default 1,    length of data to be read.

        Examples:
            sn65dsi86.read_register(0x01, 2)

        '''
        assert isinstance(reg_addr, int)
        assert isinstance(rd_len, int)
        assert reg_addr >= 0 and reg_addr <= 0xFF
        assert rd_len > 0

        return self.i2c_bus.write_and_read(self.dev_addr, [reg_addr], rd_len)
