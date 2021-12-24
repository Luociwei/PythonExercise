# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class ADS1110Def:
    VOLTAGE_REF = 2048  # The ADS1110 contains an onboard 2.048V voltage reference.
    INIT_CONGING = 0X8C

    DATA_RATE = {
        '15SPS': {'config': (0x03 << 2), 'code': 32768},  # pow(2, 16 - 1) = 32768
        '30SPS': {'config': (0x02 << 2), 'code': 16384},  # pow(2, 15 - 1) = 16384
        '60SPS': {'config': (0x01 << 2), 'code': 8192},   # pow(2, 14 - 1) = 8192
        '240SPS': {'config': (0x00 << 2), 'code': 2048}   # pow(2, 12 - 1) = 2048
    }

    GAIN_SET = {
        'GAIN_1': {'config': 0x00, 'gain': 1},
        'GAIN_2': {'config': 0x01, 'gain': 2},
        'GAIN_4': {'config': 0x02, 'gain': 4},
        'GAIN_8': {'config': 0x03, 'gain': 8}
    }


class ADS1110Exception(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class ADS1110(object):
    '''
    The ADS1110 is a precision, continuously self−calibrating Analog-to-Digital (A/D)
    converter with differential inputs and up to 16 bits of resolution in a small SOT23-6 package.
    The onboard 2.048V reference provides an input range of ±2.048V differentially. The ADS1110 uses
    an I2C-compatible serial interface and operates from a single power supply ranging from 2.7V to 5.5V.

    ClassType = ADC

    Args:
        dev_addr:   hexmial,             ads1110 i2c bus device address.
        i2c_bus:    instance(I2C)/None,  i2c bus class instance, if not using, will create emulator.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_I2C_0', 256)
        i2c_bus = MIXI2CSG(axi4_bus)
        ads1110 = ADS1110(0x48, i2c_bus)

    '''
    def __init__(self, dev_addr, i2c_bus=None):
        assert (dev_addr & (~0x03)) == 0x48

        self._dev_addr = dev_addr
        if i2c_bus is None:
            self.i2c_bus = I2CBusEmulator('i2c_emulator', 256)
        else:
            self.i2c_bus = i2c_bus

        self.code = ADS1110Def.DATA_RATE['15SPS']['code']
        self.gain = ADS1110Def.GAIN_SET['GAIN_1']['gain']

    def write_register(self, write_data):
        '''
        ADS1110 write register function

        Args:
            write_data:  hexmial, [0~0xff], value to be write to register.

        Examples:
            ads1110.write_register(0x01)

        '''
        self.i2c_bus.write(self._dev_addr, [write_data])

    def read_register(self):
        '''
        ADS1110 read register function

        Examples:
            data = ads1110.read_register()
            print(data)

        '''

        rd_data = self.i2c_bus.read(self._dev_addr, 3)
        value = (rd_data[0] << 8) | rd_data[1]

        return value

    def initial(self, data_rate='15SPS', gain_set='GAIN_1'):
        '''
        ADS1110 set configuration register

        Args:
            data_rate:   string, ['15SPS', '30SPS', '60SPS', '240SPS'], config ADS1110’s data rate.
            gain_set:    string, ['GAIN_1', 'GAIN_2', 'GAIN_4', 'GAIN_8'], config ADS1110’s gain setting.

        Examples:
            ads1110.initial('15SPS', 'GAIN_2')

        '''
        assert data_rate in ADS1110Def.DATA_RATE
        assert gain_set in ADS1110Def.GAIN_SET

        write_data = ADS1110Def.INIT_CONGING & (0xf3 | ADS1110Def.DATA_RATE[data_rate]['config'])
        write_data |= ADS1110Def.GAIN_SET[gain_set]['config']

        self.code = ADS1110Def.DATA_RATE[data_rate]['code']
        self.gain = ADS1110Def.GAIN_SET[gain_set]['gain']

        self.write_register(write_data)

    def read_volt(self, channel=0):
        '''
        ADS1110 read voltage function

        Returns:
            float, value, unit mV.

        Examples:
            data = ads1110.read_voltage()
            print(data)

        '''
        assert channel == 0
        data_code = self.read_register()
        if data_code & (1 << 16):
            data_code = ~data_code + 1

        return float(data_code) * ADS1110Def.VOLTAGE_REF / self.code / self.gain
