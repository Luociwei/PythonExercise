# -*- coding: utf-8 -*-
__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class SN65DSI86EmulatorPlugin(object):
    def __init__(self):
        self.reg = dict()

    def read(self, addr, rd_len):
        data = []
        for i in range(rd_len):
            if addr + i in self.reg.keys():
                data.append(self.reg[addr + i])
            else:
                data.append(0)
        return data

    def write(self, addr, wr_data):
        for i in range(len(wr_data)):
            self.reg[addr + i] = wr_data[i]

    def write_and_read(self, addr, wr_data, rd_len):
        for i in range(len(wr_data)):
            self.reg[addr + i] = wr_data[i]

        data = []
        for i in range(len(wr_data), len(wr_data) + rd_len):
            if addr + i in self.reg.keys():
                data.append(self.reg[addr + i])
            else:
                data.append(0)
        return data
