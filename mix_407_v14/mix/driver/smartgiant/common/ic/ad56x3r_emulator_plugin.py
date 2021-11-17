# -*- coding: utf-8 -*-

__author__ = 'dongdongzhang@SmartGiant'
__version__ = '0.1'


class AD56X3RDef:

    COMMAND_WRITE_TO_INPUT_REG = 0x00
    COMMAND_UPDATE_DAC_REG = 0x01
    COMMAND_WRITE_TO_INPUT_REG_AND_UPDATE_ALL = 0x02
    COMMAND_WRITE_AND_UPDATE_DAC_CHAN = 0x03
    COMMAND_POWER_UP_OR_DOWN = 0x04
    COMMAND_RESET = 0x05
    COMMAND_LDAC_SETUP = 0x06
    COMMAND_REFERENCE_SETUP = 0x07
    AD5667_RESLUTION = 16
    AD5647_RESLUTION = 14
    AD5627_RESLUTION = 12


class AD56x3rEmulatorPlugin(object):
    def __init__(self):
        self._reg = dict()

    def write(self, wr_data):
        for i in range(len(wr_data)):
            self._reg[i] = wr_data[i]

    def read(self, rd_len):
        data = []
        for i in range(rd_len):
            if i in self._reg.keys():
                data.append(self._reg[i])
            else:
                data.append(0)
        return data

    def transfer(self, wr_data, rd_len, sync=True):
        for index in range(len(wr_data)):
            self._reg[index] = wr_data[index]
        result_data = []
        if sync is True:
            for index in range(len(wr_data)):
                if index in self._reg.keys():
                    result_data.append(self._reg[index])
                else:
                    result_data.append(0)
            return result_data
        else:
            for index in range(rd_len):
                if index in self._reg.keys():
                    result_data.append(self._reg[index])
                else:
                    result_data.append(0)
        return result_data
