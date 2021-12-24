# -*- coding: utf-8 -*-
import time
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class AT24C08Def:
    PAGE_SIZE = 16
    PAGE_NUM = 64
    CHIP_SIZE = PAGE_SIZE * PAGE_NUM
    ADDR_MASK = 0x03
    WRITE_WAIT_TIME = 0.015


class AT24C08(object):
    '''
    AT24C08 function class

    ClassType = ADC

    Args:
        dev_addr:  hexmial,             at24c08 i2c bus device address。
        i2c_bus:   instance(I2C)/None,  i2c bus class instance, if not
                                        using , will create emulator。

    Examples:
              axi4_bus = AXI4LiteBus('/dev/MIX_DUT1_I2C_0', 256)
              i2c_bus = MIXI2CSG(axi4_bus)
              at24c08 = AT24C08(0x50, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        assert (dev_addr & (~0x07)) == 0x50
        self.dev_addr = dev_addr
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator('at24c08_emulator', 256)
        else:
            self.i2c_bus = i2c_bus

    def read(self, address, length):
        '''
        AT24C08 read specific length data

        Args:
            address:  hexmial,       the address to read data from.
            length:   int, [0~1024], length of data to read.

        Examples:
            data = at24c08.read(0x00, 10)
            print(data)

        '''
        assert length > 0
        assert address >= 0
        assert (address + length) <= AT24C08Def.CHIP_SIZE

        result = []
        while length > 0:
            dev_addr = self.dev_addr | ((address >> 8) & AT24C08Def.ADDR_MASK)
            if ((address & (AT24C08Def.PAGE_SIZE - 1)) + length) > AT24C08Def.PAGE_SIZE:
                rd_len = AT24C08Def.PAGE_SIZE - (address & (AT24C08Def.PAGE_SIZE - 1))
            else:
                rd_len = length

            result.extend(self.i2c_bus.write_and_read(dev_addr, [address & 0xFF], rd_len))

            length -= rd_len
            address += rd_len

        return result

    def write(self, address, data):
        '''
        AT24C08 write data to specific address

        Args:
            address:    hexmial, the address to write data.
            data:       list,    data to be write.

        Examples:
            at24c08.write(0x00, [0x01, 0x02, 0x03])

        '''
        assert address >= 0
        assert address + len(data) <= AT24C08Def.CHIP_SIZE

        length = len(data)

        while length > 0:
            dev_addr = self.dev_addr | ((address >> 8) & AT24C08Def.ADDR_MASK)
            if ((address & (AT24C08Def.PAGE_SIZE - 1)) + length) > AT24C08Def.PAGE_SIZE:
                wr_len = AT24C08Def.PAGE_SIZE - (address & (AT24C08Def.PAGE_SIZE - 1))
            else:
                wr_len = length

            wr_data = [address & 0xFF]
            wr_data.extend(data[0:wr_len])
            self.i2c_bus.write(dev_addr, wr_data)

            length -= wr_len
            address += wr_len
            data = data[wr_len:len(data)]
            time.sleep(AT24C08Def.WRITE_WAIT_TIME)
