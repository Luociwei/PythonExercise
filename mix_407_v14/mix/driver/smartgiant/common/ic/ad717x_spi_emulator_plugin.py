# -*- coding: utf-8 -*-


class AD717XSPIEmulatorPlugin(object):
    def __init__(self):
        self._reg = dict()

    def write(self, wr_data):
        self._reg[wr_data[0] & 0x3F] = wr_data[1:]

    def read(self, rd_len):
        data = []
        for i in range(rd_len):
            if i in self._reg.keys():
                data.append(self._reg[i])
            else:
                data.append(0)
        return data

    def transfer(self, wr_data, rd_len, sync=False):
        if wr_data[0] in self._reg:
            return self._reg[wr_data[0] & 0x3F]
        else:
            return [0 for i in range(rd_len)]
