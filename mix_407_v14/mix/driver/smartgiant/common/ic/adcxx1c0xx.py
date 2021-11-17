# -*- coding: utf-8 -*-

from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLSPIDef

__author__ = 'ouyangde@gzseeing.com'
__version__ = '0.1'


class ADCxx1C0xxDef:
    CONVERSION_RESULT_REG = 0x00
    ALERT_STATUS_REG = 0x01
    CONFIGURATION_REG = 0x02
    LOW_LIMIT_REG = 0x03
    HIGH_LIMIT_REG = 0x04
    HYSTERESIS_REG = 0x05
    LOWEST_CONS_REG = 0x06
    HIGHEST_CONS_REG = 0x07

    ADC121C021_RESOLUTION = 12


class ADCxx1C0xxException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class ADCxx1C0xx(object):
    '''
    ADCxx1C0xx is analog-to-digital converter function class.

    ClassType = ADC

    Args:
        dev_addr: hexmial,                     I2C device address of ADCxx1C0xx.
        mvref:    int, unit mV, default 3300,  reference voltage.
        i2c_bus:  instance(I2C)/None, Class instance of I2C bus, If not using this parameter, will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/AXI4_I2C_1', 256)
        i2c_bus = MIXI2CSG(axi)
        adcxx1c0xx = ADCxx1C0xx(0x50, 3300, i2c_bus)

    '''

    def __init__(self, dev_addr, mvref=3300, i2c_bus=None):

        assert dev_addr >= 0
        assert mvref >= 0
        self.resolution = None
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator(
                "adcxx1c0xx_emulator", PLSPIDef.REG_SIZE)
        else:
            self.i2c_bus = i2c_bus
        self.dev_addr = dev_addr
        self.vref = mvref
        self.dev_name = self.i2c_bus._dev_name

    def read_register(self, address, length=2):
        '''
        ADCxx1C0xx read specific length datas from address

        Args:
            address:    hexmial, [0~0x7],    Read datas from this address, must be 0-0x7.
            length:     int, dafault 2,      Length to read.

        Examples:
            result = adcxx1c0xx.read_register(0x02, 2)
            print (result)

        '''

        assert address in range(8)
        assert length > 0

        self.i2c_bus.write(self.dev_addr, [address])
        result = self.i2c_bus.read(self.dev_addr, length)

        if result is False:
            raise ADCxx1C0xxException(self.dev_name, 'read 0x%x error!'
                                      % hex(address))
        return result

    def write_register(self, address, data_list):
        '''
        ADCxx1C0xx write data_list from address

        Args:
            address:    hexmial, [0~0x7],  Read datas from this address,must be 0-0x7
            data_list:  list,              List of write data, eg:[0x12,0x23]

        Examples:
            adcxx1c0xx.write_register(0x02, [0x12,0x23])

        '''

        assert address in range(8)

        ret = self.i2c_bus.write(
            self.dev_addr, [address] + data_list[::-1])
        if ret is False:
            raise ADCxx1C0xxException(self.dev_name, 'write 0x%x error!'
                                      % hex(address))
        return ret

    def read_volt(self, channel=0):
        '''
        ADCxx1C0xx read voltage

        Args:
            channel:    int, [0], default 0, Channel index must be zero.

        Examples:
            voltage = adcxx1c0xx.read_volt(0)
            print(voltage)

        '''

        assert channel is 0
        adc_raw_data_list = self.read_register(
            ADCxx1C0xxDef.CONVERSION_RESULT_REG)

        adc_raw_data = 0
        for i in range(2):
            adc_raw_data = adc_raw_data << 8 | adc_raw_data_list[i]
        adc_raw_data = adc_raw_data & ((1 << self.resolution) - 1)
        # according to the datasheet, ADC transfer voltage need to
        # reference the vref and the resolution
        voltage = adc_raw_data * int(self.vref) / \
            float(1 << self.resolution)
        return voltage


class ADC121C021(ADCxx1C0xx):
    '''
    ADC121C021 8-Bit analog-to-digital converter function class

    ClassType = ADC

    Args:
        dev_addr: hexmial,            I2C device address of ADC121C021.
        mvref:    int, unit mV,       reference voltage.
        i2c_bus:  instance(I2C)/None, Class instance of I2C bus, If not using this parameter, will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/MIX_I2C_1', 256)
        i2c_bus = MIXI2CSG(axi)
        adc121C021 = ADC121C021(0x50, 3300, i2c_bus)

    '''

    def __init__(self, dev_addr, mvref, i2c_bus):
        super(ADC121C021, self).__init__(dev_addr, mvref, i2c_bus)
        self.resolution = ADCxx1C0xxDef.ADC121C021_RESOLUTION
