# -*- coding: UTF-8 -*-
import time
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLI2CDef

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.1'


class TMP10xDef:
    '''
    TMP10xDef shows the register address of TMP10x
    TMP100/101/102/105/106/108 are 12 bits, TMP103 is 8 bits,
    TMP100/101 temperature range is -55℃ to +125℃,
    TMP102/105/106/108 temperature range is -40℃ to +125℃.
    TMP112 range is -55°C~128°C in 12-bit mode, and 13-bit mode is -55°C~150°C
    '''
    COMMAND_TEMPERATURE = 0x00  # read only
    COMMAND_CONFIGURATION = 0x01  # read/write

    RESOLUTION_MULTIPLE = 0.0625
    WAIT_READ_TIME = 0.027
    WAIT_TIME = 0.001
    TIME_OUT = 100

    TMP112_CONVERT_RATE = [1.0 / 0.25, 1.0 / 1, 1.0 / 4, 1.0 / 8]   # 0.25, 1, 4, 8 Hz, desided by CR0 CR1


class TMP10xException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class TMP10x(object):
    '''
    TMP10x digital temperature sensor function class to get the temperature

    ClassType = ADC

    Args:
        dev_addr:  hexmial,               I2C device address of TMP10x.
        i2c_bus:   instance(I2C)/None,    Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        TMP10x = TMP10x(0x50, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus=None):
        self.data_length = 1
        self.config_data = [0x25, 0x10]
        self.dev_addr = dev_addr
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator(
                'ads1115_emulator', PLI2CDef.REG_SIZE)
        else:
            self.i2c_bus = i2c_bus

    def read_register(self, reg_addr, length):
        '''
        TMP10x read specific length datas from address, support TMP103
        one bit or TMP100/101/102/105/106/108 two bits

        Args:
            reg_addr:    hexmial, [0~0x03], Read datas from this address.
            length:      int, [1~2],        Length to read.

        Returns:
            list, [value].

        Examples:
            result = TMP10x.read_register(0x00, 2)
            print(result)

        '''
        assert reg_addr in [0x00, 0x01, 0x02, 0x03]
        result = self.i2c_bus.write_and_read(
            self.dev_addr, [reg_addr], self.data_length)
        return result

    def write_register(self, reg_addr, data):
        '''
        TMP10x write specific length datas from address, support to
        write one or two bytes

         Args:
            reg_addr:    hexmial, [0x00~0x03], Read datas from this address.
            data:        hexmial, [0x00~0xFF], Data to write.

        Examples:
            TMP10x.write_register(0x01, 0x2)

        '''
        assert reg_addr != 0x00 and reg_addr in [0x1, 0x2, 0x3]
        write_data = []
        write_data.append(reg_addr)
        write_data = write_data + data
        self.i2c_bus.write(self.dev_addr, write_data)

    def get_temperature(self):
        '''
        TMP10x read datas from address, support to
        write one or two bytes, transform to temperature

        Returns:
            float, value.

        Examples:
            temperature = TMP10x.get_temperature()
            print(temperature)

        '''
        self.write_register(TMP10xDef.COMMAND_CONFIGURATION, self.config_data)
        time.sleep(TMP10xDef.WAIT_READ_TIME)    # need 0.027s read
        timeout = TMP10xDef.TIME_OUT  # wait 0.1s timeout
        time_ms = 0
        while time_ms < timeout:
            result = self.read_register(TMP10xDef.COMMAND_CONFIGURATION, 2)
            if not (result[0] & 0x3):
                break
            time.sleep(TMP10xDef.WAIT_TIME)    # need to read the status bit
            time_ms += 1
        if time_ms > timeout:
            raise TMP10xException("tmp10x", 'temperature_get timeout!')
        if self.data_length == 1:
            regval = self.read_register(TMP10xDef.COMMAND_TEMPERATURE, 1)
            temp = regval[0]
            if temp & 0x80:  # minus temperature
                # eight bit maximum inversion
                temperature = -(~(temp) + 1 & 0xff)
            else:
                temperature = temp
            return temperature
        else:
            regval = self.read_register(TMP10xDef.COMMAND_TEMPERATURE, 2)
            temp = (regval[0] << 4) | (regval[1] >> 4)
            if temp & 0x800:  # minus temperature
                # twelve bits maximum inversion
                temperature = -((~(temp - 1)) & 0x7ff) * \
                    TMP10xDef.RESOLUTION_MULTIPLE
            else:
                temperature = temp * TMP10xDef.RESOLUTION_MULTIPLE
            return temperature


class TMP100(TMP10x):
    '''
    TMP100 digital temperature sensor function class to get the temperature

    ClassType = ADC

    Args:
        dev_addr:  hexmial,               I2C device address of TMP100.
        i2c_bus:   instance(I2C)/None,    Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        TMP100 = TMP10x(0x48, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        assert (dev_addr & (~0x37)) == 0x48
        super(TMP100, self).__init__(dev_addr, i2c_bus)
        self.data_length = 2
        self.config_data = [0x21]


class TMP101(TMP10x):
    '''
    TMP101 digital temperature sensor function class to get the temperature

    ClassType = ADC

    Args:
        dev_addr:  hexmial,               I2C device address of TMP101.
        i2c_bus:   instance(I2C)/None,    Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        TMP101 = TMP10x(0x48, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        assert (dev_addr & (~0x37)) == 0x48
        super(TMP101, self).__init__(dev_addr, i2c_bus)
        self.data_length = 2
        self.config_data = [0x21]


class TMP102(TMP10x):
    '''
    TMP102 digital temperature sensor function class to get the temperature

    ClassType = ADC

    Args:
        dev_addr:  hexmial,               I2C device address of TMP102.
        i2c_bus:   instance(I2C)/None,    Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        TMP102 = TMP10x(0x48, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        assert (dev_addr & (~0x37)) == 0x48
        super(TMP102, self).__init__(dev_addr, i2c_bus)
        self.data_length = 2
        self.config_data = [0x60, 0x60]


class TMP103(TMP10x):
    '''
    TMP103 digital temperature sensor function class to get the temperature

    ClassType = ADC

    Args:
        dev_addr:  hexmial,               I2C device address of TMP103.
        i2c_bus:   instance(I2C)/None,    Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        TMP103 = TMP10x(0x70, i2c)

    '''
    def __init__(self, dev_addr, i2c_bus):
        assert (dev_addr & (~0x0f)) == 0x70
        super(TMP103, self).__init__(dev_addr, i2c_bus)
        self.data_length = 1
        self.config_data = [0x21]


class TMP105(TMP10x):
    '''
    TMP105 digital temperature sensor function class to get the temperature

    ClassType = ADC

    Args:
        dev_addr:  hexmial,               I2C device address of TMP105.
        i2c_bus:   instance(I2C)/None,    Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        TMP105 = TMP10x(0x48, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        assert (dev_addr & (~0x37)) == 0x48
        super(TMP105, self).__init__(dev_addr, i2c_bus)
        self.data_length = 2
        self.config_data = [0x21]


class TMP106(TMP10x):
    '''
    TMP106 digital temperature sensor function class to get the temperature

    ClassType = ADC

    Args:
        dev_addr:  hexmial,               I2C device address of TMP106.
        i2c_bus:   instance(I2C)/None,    Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        TMP106 = TMP10x(0x48, i2c)

    '''
    def __init__(self, dev_addr, i2c_bus):
        assert (dev_addr & (~0x37)) == 0x48
        super(TMP106, self).__init__(dev_addr, i2c_bus)
        self.data_length = 2
        self.config_data = [0x21]


class TMP108(TMP10x):
    '''
    TMP108 digital temperature sensor function class to get the temperature

    ClassType = ADC

    Args:
        dev_addr:  hexmial,               I2C device address of TMP108.
        i2c_bus:   instance(I2C)/None,    Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        TMP108 = TMP10x(0x48, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        assert (dev_addr & (~0x37)) == 0x48
        super(TMP108, self).__init__(dev_addr, i2c_bus)
        self.data_length = 2
        self.config_data = [0x25, 0x10]


class TMP112(TMP10x):
    '''
    TMP108 digital temperature sensor function class to get the temperature

    ClassType = ADC

    Args:
        dev_addr:  hexmial,               I2C device address of TMP108.
        i2c_bus:   instance(I2C)/None,    Class instance of I2C bus,
                                          If not using this parameter,
                                          will create Emulator

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c = MIXI2CSG(axi)
        tmp112 = TMP112(0x48, i2c)

    '''

    def __init__(self, dev_addr, i2c_bus):
        assert (dev_addr & (~0x37)) == 0x48
        super(TMP112, self).__init__(dev_addr, i2c_bus)
        self.data_length = 2
        self.config_data = [0x60, 0xB0]

    def get_temperature(self):
        '''
        TMP116 transfer temperature.

        Returns:
            float, value.

        Examples:
            temperature = tmp116.get_temperature()
            print(temperature)

        '''
        self.write_register(TMP10xDef.COMMAND_CONFIGURATION, self.config_data)
        time.sleep(TMP10xDef.TMP112_CONVERT_RATE[self.config_data[1] >> 6])    # waiting for convertion

        timeout_s = TMP10xDef.TIME_OUT / 1000.0  # wait 0.1s timeout
        start = time.time()

        while True:
            if time.time() - start >= timeout_s:
                raise TMP10xException("tmp10x", 'temperature_get timeout!')

            result = self.read_register(TMP10xDef.COMMAND_CONFIGURATION, 2)

            # break while if chip is not working in shutdown mode
            if not (result[0] & 0x1):
                break

            time.sleep(TMP10xDef.WAIT_TIME)    # need to read the status bit

        regval = self.read_register(TMP10xDef.COMMAND_TEMPERATURE, 2)
        temp = regval[0] << 8 | regval[1]
        rshift = 3 if temp & 0x1 else 4         # EM bit had enable, deside 12-bit mode or 13-bit mode

        if temp & 0x8000:
            temp = ((~temp) + 1 << rshift) >> rshift
            resolution = -1.0 * TMP10xDef.RESOLUTION_MULTIPLE
        else:
            temp >>= rshift
            resolution = TMP10xDef.RESOLUTION_MULTIPLE

        return temp * resolution
