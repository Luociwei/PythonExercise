# -*- coding: utf-8 -*-
import time


class AT24CXXDef:
    WRITE_CYCLE_TIME = 0.015
    FPGA_BUFSZ = 32
    ADDRESS_BIT = 0X07
    ADDR_ENABLE = 0x50
    AT24C01_PAGE_SIZE = 8
    AT24C01_PAGE_NUM = 16
    AT24C01_ADDR_SIZE = 1
    AT24C01_MASK = 0x00
    AT24C02_PAGE_SIZE = 8
    AT24C02_PAGE_NUM = 32
    AT24C02_ADDR_SIZE = 1
    AT24C02_MASK = 0x00
    AT24C04_PAGE_SIZE = 16
    AT24C04_PAGE_NUM = 32
    AT24C04_ADDR_SIZE = 1
    AT24C04_MASK = 0x01
    AT24C08_PAGE_SIZE = 16
    AT24C08_PAGE_NUM = 64
    AT24C08_ADDR_SIZE = 1
    AT24C08_MASK = 0x03
    AT24C16_PAGE_SIZE = 16
    AT24C16_PAGE_NUM = 128
    AT24C16_ADDR_SIZE = 1
    AT24C16_MASK = 0x07
    AT24C32_PAGE_SIZE = 32
    AT24C32_PAGE_NUM = 128
    AT24C32_ADDR_SIZE = 2
    AT24C32_MASK = 0x00
    AT24C64_PAGE_SIZE = 32
    AT24C64_PAGE_NUM = 256
    AT24C64_ADDR_SIZE = 2
    AT24C64_MASK = 0x00
    AT24C128_PAGE_SIZE = 64
    AT24C128_PAGE_NUM = 256
    AT24C128_ADDR_SIZE = 2
    AT24C128_MASK = 0x00
    AT24C256_PAGE_SIZE = 64
    AT24C256_PAGE_NUM = 512
    AT24C256_ADDR_SIZE = 2
    AT24C256_MASK = 0x00
    AT24C512_PAGE_SIZE = 128
    AT24C512_PAGE_NUM = 512
    AT24C512_ADDR_SIZE = 2
    AT24C512_MASK = 0x00


class AT24CXXException(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class AT24CXX(object):
    '''
    AT24CXX EEPROM function class

    Args:
        dev_addr:  hexmial,       I2C device address of AT24CXX.
        i2c_bus:   instance(I2C), Class instance of I2C bus.

    Examples:
       axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
       i2c = PLI2CBus(axi)
       eeprom = AT24CXX(0x50, i2c)

    '''
    rpc_public_api = ['read', 'write']

    def __init__(self, dev_addr, i2c_bus):
        if i2c_bus is None:
            raise AT24CXXException("__init__ error! Please check the parameter i2c_bus")
        else:
            self.iic_bus = i2c_bus
        dev_addr &= AT24CXXDef.ADDRESS_BIT
        dev_addr |= AT24CXXDef.ADDR_ENABLE
        self.device_addr = dev_addr & (~self.mask)

    def address_to_byte_list(self, addr):
        '''
        AT24CXX use it to change address to the byte list

        Args:
            addr:    hexmial, [0~0xFF], AT24CXX address.

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
        AT24CXX read specific length datas from address,
        support cross pages reading operation

        Args:
            addr:      hexmial, (>=0), Read data from this address.
            length:    int, (>=0),     Length to read.

        Returns:
            list, [value, ...].

        Examples:
            result = cat24cxx.read(0x00, 10)
            print(result)

        '''
        if addr + length > self.chip_size:
            raise AT24CXXException("read data len over chip size")

        read_len = length
        read_addr = addr
        read_bytes = 0
        if (read_addr & (self.page_size - 1)) + read_len > self.page_size:
            read_bytes = self.page_size - (read_addr & (self.page_size - 1))
        else:
            read_bytes = read_len

        result = []
        while read_len > 0:
            if self.device_type == "AT24C04"\
                    or self.device_type == "AT24C08"\
                    or self.device_type == "AT24C16":
                device_addr = self.device_addr |\
                    ((read_addr >> 8) & self.mask)
            else:
                device_addr = self.device_addr
            mem_addr = self.address_to_byte_list(read_addr)
            '''FPGA i2c bus a frame max size is 32 bytes data.'''
            if read_bytes > (AT24CXXDef.FPGA_BUFSZ - 1 - len(mem_addr)):
                read_bytes = AT24CXXDef.FPGA_BUFSZ - 1 - len(mem_addr)
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
        AT24CXX write datas to address, support cross pages writing operation

        Args:
            addr:       int, (>=0), Write data to this address.
            data:       list,          Length to read.

        Examples:
            wr_data = [0x01, 0x02, 0x03, 0x04]
            cat24cxx.write(0x00, wr_data)

        '''
        write_len = len(data)
        if addr + write_len > self.chip_size:
            raise AT24CXXException("write data len over chip size")

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
            if self.device_type == "AT24C04" \
                    or self.device_type == "AT24C08" \
                    or self.device_type == "AT24C16":
                device_addr = self.device_addr | (
                    (write_addr >> 8) & self.mask)
            else:
                device_addr = self.device_addr

            mem_addr = self.address_to_byte_list(write_addr)
            '''FPGA i2c bus a frame max size is 32 bytes data.'''
            if write_bytes > (AT24CXXDef.FPGA_BUFSZ - 1 - len(mem_addr)):
                write_bytes = AT24CXXDef.FPGA_BUFSZ - 1 - len(mem_addr)
            write_data = data[0:write_bytes]
            self.iic_bus.write(device_addr, mem_addr + write_data)
            del data[0:write_bytes]
            write_len -= write_bytes
            write_addr += write_bytes
            if write_len > self.page_size or (write_addr & (self.page_size - 1)) != 0:
                write_bytes = self.page_size - (write_addr & (self.page_size - 1))
            else:
                write_bytes = write_len
            time.sleep(AT24CXXDef.WRITE_CYCLE_TIME)


class AT24C01(AT24CXX):
    '''
    AT24C01 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C01.
        i2c_bus:     instance(I2C),  Class instance of I2C bus, if not using this parameter,

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C01(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C01_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C01_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C01_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C01_MASK
        self.device_type = 'AT24C01'
        super(AT24C01, self).__init__(dev_addr, i2c_bus)


class AT24C02(AT24CXX):
    '''
    AT24C02 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C02.
        i2c_bus:     instance(I2C),  Class instance of I2C bus.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C02(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C02_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C02_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C02_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C02_MASK
        self.device_type = 'AT24C02'
        super(AT24C02, self).__init__(dev_addr, i2c_bus)


class AT24C04(AT24CXX):
    '''
    AT24C04 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C04.
        i2c_bus:     instance(I2C),  Class instance of I2C bus.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C04(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C04_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C04_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C04_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C04_MASK
        self.device_type = 'AT24C04'
        super(AT24C04, self).__init__(dev_addr, i2c_bus)


class AT24C08(AT24CXX):
    '''
    AT24C08 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C08.
        i2c_bus:     instance(I2C),  Class instance of I2C bus.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C08(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C08_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C08_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C08_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C08_MASK
        self.device_type = 'AT24C08'
        super(AT24C08, self).__init__(dev_addr, i2c_bus)


class AT24C16(AT24CXX):
    '''
    AT24C16 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C16.
        i2c_bus:     instance(I2C),  Class instance of I2C bus.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C16(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C16_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C16_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C16_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C16_MASK
        self.device_type = 'AT24C16'
        super(AT24C16, self).__init__(dev_addr, i2c_bus)


class AT24C32(AT24CXX):
    '''
    AT24C32 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C32.
        i2c_bus:     instance(I2C),  Class instance of I2C bus.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C32(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C32_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C32_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C32_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C32_MASK
        self.device_type = 'AT24C32'
        super(AT24C32, self).__init__(dev_addr, i2c_bus)


class AT24C64(AT24CXX):
    '''
    AT24C64 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C64.
        i2c_bus:     instance(I2C),  Class instance of I2C bus.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C64(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C64_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C64_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C64_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C64_MASK
        self.device_type = 'AT24C64'
        super(AT24C64, self).__init__(dev_addr, i2c_bus)


class AT24C128(AT24CXX):
    '''
    AT24C128 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C128.
        i2c_bus:     instance(I2C),  Class instance of I2C bus.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C128(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C128_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C128_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C128_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C128_MASK
        self.device_type = 'AT24C128'
        super(AT24C128, self).__init__(dev_addr, i2c_bus)


class AT24C256(AT24CXX):
    '''
    AT24C256 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C256.
        i2c_bus:     instance(I2C),  Class instance of I2C bus.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C256(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C256_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C256_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C256_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C256_MASK
        self.device_type = 'AT24C256'
        super(AT24C256, self).__init__(dev_addr, i2c_bus)


class AT24C512(AT24CXX):
    '''
    AT24C512 EEPROM function class

    ClassType = EEPROM

    Args:
        dev_addr:    hexmial,        I2C device address of AT24C512.
        i2c_bus:     instance(I2C),  Class instance of I2C bus.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_DUT1_I2C_1', 256)
        i2c = PLI2CBus(axi)
        eeprom = AT24C512(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        self.page_size = AT24CXXDef.AT24C512_PAGE_SIZE
        self.chip_size = AT24CXXDef.AT24C512_PAGE_NUM * self.page_size
        self.address_size = AT24CXXDef.AT24C512_ADDR_SIZE
        self.mask = AT24CXXDef.AT24C512_MASK
        self.device_type = 'AT24C512'
        super(AT24C512, self).__init__(dev_addr, i2c_bus)
