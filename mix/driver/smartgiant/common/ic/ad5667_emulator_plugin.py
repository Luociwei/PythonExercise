# -*- coding: utf-8 -*-

__author__ = 'Jiasheng.Xie'
__version__ = '0.1'


class AD56X7RDef:

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


class AD5667EmulatorPlugin(object):

    def __init__(self):
        self.reg = dict()

    def write(self, addr, wr_data):
        assert len(wr_data) < 4
        self.reg[addr] = wr_data

    def read(self, addr, len=3):
        return self.reg[addr][:len]

    def write_and_read(self, addr, wr_data, rd_len):
        raise NotImplementedError('AD5667 no need to implement this function')

