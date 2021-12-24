# -*- coding: utf-8 -*-

from ..bus.i2c_bus_emulator import I2CBusEmulator
from ..bus.axi4_lite_def import PLSPIDef
from time import sleep


class M24CxxDef:
    PAGE_SIZE = 8
    PAGE_NUM = 8
    CHIP_SIZE = PAGE_SIZE * PAGE_NUM
    WRITE_WAIT_TIME = 0.004


class M24CxxException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class M24Cxx(object):
    '''
    MC24Cxx function class

    Args:
        dev_addr:  hexmial,        I2C device address.
        i2c_bus:   instance(I2C)/None,  Class instance of I2C bus,
                                        If not using this parameter,
                                        will create Emulator.
        page_size: int, chip page size in bytes.
        chip_size: int, chip chip size in bytes.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c_bus = PLI2CBus(axi)
        eeprom = M24Cxx(0x50, i2c_bus)

    '''
    rpc_public_api = ['write', 'read']

    def __init__(self, dev_addr, i2c_bus=None, page_size=None, chip_size=None):

        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator(
                'm24cxx_emulator', PLSPIDef.REG_SIZE)
        else:
            self.i2c_bus = i2c_bus
        self.page_size = page_size if page_size else M24CxxDef.PAGE_SIZE
        self.chip_size = chip_size if chip_size else M24CxxDef.CHIP_SIZE
        self.dev_addr = dev_addr
        self.dev_name = self.i2c_bus._dev_name

    def write(self, address, data_list):
        '''
        MC24Cxx write data

        Args:
            address:    hexmial,   eeprom address.
            data_list:  list,      data list, each element takes one byte.

        Examples:
            write 0x1,0x2,to the address 0x00 of eeprom
            eeprom.write(0x00, [0x01, 0x02])

        '''

        if address + len(data_list) > self.chip_size:
            raise M24CxxException(self.dev_name, 'write data error !')

        left = len(data_list)
        while left > 0:
            send_list = []
            num = self.page_size - (address % self.page_size)
            if num >= left:
                num = left
            send_list += [address >> 8 & 0xFF, address & 0xFF]
            send_list += data_list[0:num]
            ret = self.i2c_bus.write(self.dev_addr, send_list)
            sleep(M24CxxDef.WRITE_WAIT_TIME)
            if ret is False:
                return False
            data_list = data_list[num:]
            left -= num
            address += num
        return ret

    def read(self, address, length):
        '''
        MC24Cxx read specific length data

        Args:
            address:   hexmial,  eeprom address.
            length:    int,      read length.

        Returns:
            list, each element takes one byte.

        Raises:
            M24CxxException:    read 3 byte from the address 0x00 of eeprom
                                eeprom.read(0x00, 3)

        Examples:
            read 2 data from the address 0x00 of eeprom
            eeprom.read(0x00, 2)

        '''

        if address + length > self.chip_size:
            raise M24CxxException(
                self.dev_name, 'm24xx read api param error!')
        recv_data = []
        while length > 0:
            send_list = []
            num = self.page_size - (address % self.page_size)
            if num >= length:
                num = length
            send_list += [address >> 8 & 0xFF, address & 0xFF]
            ret = self.i2c_bus.write_and_read(self.dev_addr, send_list, num)
            if ret is False:
                raise M24CxxException(self.dev_name, 'm24xx read error!')
            recv_data += ret
            length -= num
            address += num
        return recv_data


class M24C08(M24Cxx):
    '''
    MC24C08 EEPROM: 8kbit (1KB) i2c EEPROM

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator.

    Examples:
        i2c = I2C('/dev/i2c-1')
        eeprom = M24C08(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        super(M24C08, self).__init__(dev_addr, i2c_bus, 16, 1024)


class M24C32(M24Cxx):
    '''
    MC24C32 EEPROM: 32kbit (4KB) i2c EEPROM

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator.

    Examples:
        i2c = I2C('/dev/i2c-1')
        eeprom = M24C32(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        super(M24C32, self).__init__(dev_addr, i2c_bus, 32, 4096)


class M24128(M24Cxx):
    '''
    MC24128: 128kbit (16KB) i2c EEPROM

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c_bus = PLI2CBus(axi)
        eeprom = M24128(0x50, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        super(M24128, self).__init__(dev_addr, i2c_bus, 64, 16384)


class M24256(M24Cxx):
    '''
    MC24256 function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c_bus = PLI2CBus(axi)
        eeprom = M24256(0x50, i2c_bus)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        super(M24256, self).__init__(dev_addr, i2c_bus, 64, 32768)
