# -*- coding: utf-8 -*-


class I2CEmulatorPlugin(object):
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
