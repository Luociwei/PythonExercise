# -*- coding: utf-8 -*-
import time
from ..bus.i2c_bus_emulator import I2CBusEmulator
from ..bus.axi4_lite_def import PLI2CDef


class CAT24CXXDef:
    WRITE_CYCLE_TIME = 0.015
    FPGA_BUFSZ = 32
    ADDRESS_BIT = 0X07
    ADDR_ENABLE = 0x50
    CAT24C01_PAGE_SIZE = 16
    CAT24C01_PAGE_NUM = 8
    CAT24C01_ADDR_SIZE = 1
    CAT24C01_MASK = 0x00
    CAT24C02_PAGE_SIZE = 16
    CAT24C02_PAGE_NUM = 16
    CAT24C02_ADDR_SIZE = 1
    CAT24C02_MASK = 0x00
    CAT24C04_PAGE_SIZE = 16
    CAT24C04_PAGE_NUM = 32
    CAT24C04_ADDR_SIZE = 1
    CAT24C04_MASK = 0x01
    CAT24C08_PAGE_SIZE = 16
    CAT24C08_PAGE_NUM = 64
    CAT24C08_ADDR_SIZE = 1
    CAT24C08_MASK = 0x03
    CAT24C16_PAGE_SIZE = 16
    CAT24C16_PAGE_NUM = 128
    CAT24C16_ADDR_SIZE = 1
    CAT24C16_MASK = 0x07
    CAT24C32_PAGE_SIZE = 32
    CAT24C32_PAGE_NUM = 128
    CAT24C32_ADDR_SIZE = 2
    CAT24C32_MASK = 0x00
    CAT24C64_PAGE_SIZE = 32
    CAT24C64_PAGE_NUM = 256
    CAT24C64_ADDR_SIZE = 2
    CAT24C64_MASK = 0x00
    CAT24C128_PAGE_SIZE = 64
    CAT24C128_PAGE_NUM = 256
    CAT24C128_ADDR_SIZE = 2
    CAT24C128_MASK = 0x00
    CAT24C256_PAGE_SIZE = 64
    CAT24C256_PAGE_NUM = 512
    CAT24C256_ADDR_SIZE = 2
    CAT24C256_MASK = 0x00
    CAT24C512_PAGE_SIZE = 128
    CAT24C512_PAGE_NUM = 512
    CAT24C512_ADDR_SIZE = 2
    CAT24C512_MASK = 0x00


class CAT24CXXException(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class CAT24CXX(object):
    '''
    CAT24CXX EEPROM function class

    Args:
        dev_addr:  hexmial,       I2C device address of CAT24CXX.
        i2c_bus:   instance(I2C)/None, Class instance of I2C bus, if not using this parameter,
                                  will create Emulator.

    Examples:
       axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
       i2c = PLI2CBus(axi)
       eeprom = CAT24CXX(0x50, i2c)

    '''
    rpc_public_api = ['read', 'write']

    def __init__(self, dev_addr, i2c_bus):
        if i2c_bus is None:
            self.iic_bus = I2CBusEmulator("cat24cxx_emulator",
                                          PLI2CDef.REG_SIZE)
        else:
            self.iic_bus = i2c_bus
        dev_addr &= CAT24CXXDef.ADDRESS_BIT
        dev_addr |= CAT24CXXDef.ADDR_ENABLE
        self.device_addr = dev_addr & (~self.mask)

    def address_to_byte_list(self, addr):
        '''
        CAT24CXX use it to change address to the byte list

        Args:
            addr:    hexmial, [0~0xFF], CAT24CXX address.

        Returns:
            list, [value, ...].

        Examples:
            self.address_to_byte_list(0x12)

        '''
        if self.address_size == 2:
            return [(addr >> 8 & 0xff), (addr & 0xff)]
        else:
            return [(addr & 0xff), ]

    def read(self, addr, length):
        '''
        CAT24CXX read specific length datas from address,
        support cross pages reading operation

        Args:
            addr:      hexmial, [0~0xFF], Read datas from this address.
            length:    int, [0~1024],     Length to read.

        Returns:
            list, [value, ...].

        Examples:
            result = cat24cxx.read(0x00, 10)
            print(result)

        '''
        if addr + length > self.chip_size:
            raise CAT24CXXException("read data len over chip size")

        read_len = length
        read_addr = addr
        read_bytes = 0
        if (read_addr & (self.page_size - 1)) + read_len > self.page_size:
            read_bytes = self.page_size - (read_addr & (self.page_size - 1))
        else:
            read_bytes = read_len

        result = []
        while read_len > 0:
            if self.device_type == "CAT24C04"\
                    or self.device_type == "CAT24C08"\
                    or self.device_type == "CAT24C16":
                device_addr = self.device_addr |\
                    ((read_addr >> 8) & self.mask)
            else:
                device_addr = self.device_addr
            mem_addr = self.address_to_byte_list(read_addr)
            '''FPGA i2c bus a frame max size is 32 bytes data.'''
            if read_bytes > (CAT24CXXDef.FPGA_BUFSZ - 1 - len(mem_addr)):
                read_bytes = CAT24CXXDef.FPGA_BUFSZ - 1 - len(mem_addr)
            read_result = self.iic_bus.write_and_read(
                device_addr, mem_addr, read_bytes)
            result += read_result
            read_len -= read_bytes
            read_addr += read_bytes

            if (read_addr & (self.page_size - 1)) + read_len > self.page_size:
                read_bytes = self.page_size - (read_addr & (self.page_size - 1))
            else:
                read_bytes = read_len

        return result

    def write(self, addr, data):
        '''
        CAT24CXX write datas to address, support cross pages writing operation

        Args:
            addr:       int, [0~1024], Write datas to this address.
            data:       list,          Length to read.

        Examples:
            wr_data = [0x01, 0x02, 0x03, 0x04]
            cat24cxx.write(0x00, wr_data)

        '''
        write_len = len(data)
        if addr + write_len > self.chip_size:
            raise CAT24CXXException("write data len over chip size")

        data = list(data)
        write_addr = addr
        write_bytes = 0
        if write_len > self.page_size or\
                (write_addr & (self.page_size - 1)) != 0:
            write_bytes = self.page_size - \
                (write_addr & (self.page_size - 1))
        else:
            write_bytes = write_len

        while write_len > 0:
            if self.device_type == "CAT24C04" \
                    or self.device_type == "CAT24C08" \
                    or self.device_type == "CAT24C16":
                device_addr = self.device_addr | (
                    (write_addr >> 8) & self.mask)
            else:
                device_addr = self.device_addr

            mem_addr = self.address_to_byte_list(write_addr)
            '''FPGA i2c bus a frame max size is 32 bytes data.'''
            if write_bytes > (CAT24CXXDef.FPGA_BUFSZ - 1 - len(mem_addr)):
                write_bytes = CAT24CXXDef.FPGA_BUFSZ - 1 - len(mem_addr)
            write_data = data[0:write_bytes]
            self.iic_bus.write(device_addr, mem_addr + write_data)
            del data[0:write_bytes]
            write_len -= write_bytes
            write_addr += write_bytes
            if write_len > self.page_size or (write_addr & (self.page_size - 1)) != 0:
                write_bytes = self.page_size - (write_addr & (self.page_size - 1))
            else:
                write_bytes = write_len
            time.sleep(CAT24CXXDef.WRITE_CYCLE_TIME)


class CAT24C01(CAT24CXX):
    '''
    CAT24C01 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C01.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C01(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C01_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C01_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C01_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C01_MASK
        self.device_type = 'CAT24C01'
        super(CAT24C01, self).__init__(dev_addr, i2c_bus)


class CAT24C02(CAT24CXX):
    '''
    CAT24C02 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C02.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C02(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C02_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C02_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C02_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C02_MASK
        self.device_type = 'CAT24C02'
        super(CAT24C02, self).__init__(dev_addr, i2c_bus)


class CAT24C04(CAT24CXX):
    '''
    CAT24C04 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C04.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C04(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C04_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C04_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C04_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C04_MASK
        self.device_type = 'CAT24C04'
        super(CAT24C04, self).__init__(dev_addr, i2c_bus)


class CAT24C08(CAT24CXX):
    '''
    CAT24C08 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C08.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C08(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C08_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C08_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C08_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C08_MASK
        self.device_type = 'CAT24C08'
        super(CAT24C08, self).__init__(dev_addr, i2c_bus)


class CAT24C16(CAT24CXX):
    '''
    CAT24C16 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C16.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C16(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C16_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C16_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C16_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C16_MASK
        self.device_type = 'CAT24C16'
        super(CAT24C16, self).__init__(dev_addr, i2c_bus)


class CAT24C32(CAT24CXX):
    '''
    CAT24C32 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C32.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C32(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C32_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C32_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C32_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C32_MASK
        self.device_type = 'CAT24C32'
        super(CAT24C32, self).__init__(dev_addr, i2c_bus)


class CAT24C64(CAT24CXX):
    '''
    CAT24C64 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C64.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C64(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C64_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C64_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C64_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C64_MASK
        self.device_type = 'CAT24C64'
        super(CAT24C64, self).__init__(dev_addr, i2c_bus)


class CAT24C128(CAT24CXX):
    '''
    CAT24C128 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C128.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C128(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C128_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C128_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C128_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C128_MASK
        self.device_type = 'CAT24C128'
        super(CAT24C128, self).__init__(dev_addr, i2c_bus)


class CAT24C256(CAT24CXX):
    '''
    CAT24C256 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C256.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C256(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C256_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C256_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C256_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C256_MASK
        self.device_type = 'CAT24C256'
        super(CAT24C256, self).__init__(dev_addr, i2c_bus)


class CAT24C512(CAT24CXX):
    '''
    CAT24C512 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of CAT24C512.
        i2c_bus:     instance(I2C)/None,  Class instance of I2C bus, if not using this parameter,
                                          will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = CAT24C512(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = CAT24CXXDef.CAT24C512_PAGE_SIZE
        self.chip_size = CAT24CXXDef.CAT24C512_PAGE_NUM * self.page_size
        self.address_size = CAT24CXXDef.CAT24C512_ADDR_SIZE
        self.mask = CAT24CXXDef.CAT24C512_MASK
        self.device_type = 'CAT24C512'
        super(CAT24C512, self).__init__(dev_addr, i2c_bus)
