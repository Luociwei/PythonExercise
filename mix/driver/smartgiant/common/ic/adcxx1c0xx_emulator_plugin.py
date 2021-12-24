# -*- coding: utf-8 -*-

__author__ = 'ouyangde@gzseeing,com'
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


class ADCxx1C0xxEmulatorPlugin(object):
    def __init__(self):
        self._reg = dict()

    def read(self, addr, rd_len):
        data = []
        for i in range(rd_len):
            if addr + i in self._reg.keys():
                data.append(self._reg[addr + i])
            else:
                data.append(0)
        return data

    def write(self, addr, wr_data):
        for i in range(len(wr_data)):
            self._reg[addr + i] = wr_data[i]

    def write_and_read(self, addr, wr_data, rd_len):
        for i in range(len(wr_data)):
            self._reg[addr + i] = wr_data[i]

        data = []
        for i in range(len(wr_data), len(wr_data) + rd_len):
            if addr + i in self._reg.keys():
                data.append(self._reg[addr + i])
            else:
                data.append(0)
        return data

    def read_volt(self):

        adc_raw_data_list = self.read(ADCxx1C0xxDef.CONVERSION_RESULT_REG, 2)
        adc_raw_data = 0
        for i in range(2):
            adc_raw_data = adc_raw_data << 8 | adc_raw_data_list[i]

        adc_raw_data = adc_raw_data & ((1 << ADC121C021Def.RESOLUTION) - 1)
        voltage = adc_raw_data * 3300 / float(1 << ADC121C021Def.RESOLUTION)
        return voltage
