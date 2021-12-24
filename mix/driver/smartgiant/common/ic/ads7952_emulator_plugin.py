# -*- coding: utf-8 -*-


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class ADS7952EmulatorPlugin(object):
    def __init__(self):
        self._reg = dict()

    def write(self, wr_data):
        reg_addr = ((wr_data[0] >> 4) & 0xFF)
        self._reg[reg_addr] = wr_data

    def read(self, rd_len):
        return [0, 0]

    def transfer(self, wr_data, rd_len, sync=True):
        reg_addr = ((wr_data[0] >> 4) & 0xFF)
        self._reg[reg_addr] = wr_data
        return [0 for i in range(rd_len)]
