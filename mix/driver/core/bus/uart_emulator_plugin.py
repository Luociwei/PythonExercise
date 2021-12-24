# -*- coding: utf-8 -*-


class UARTEmulatorPlugin(object):
    def __init__(self):
        self._reg = []

    def read(self, rd_len, timeout=0):
        data = []
        for i in range(rd_len):
            if i < len(self._reg):
                data.append(self._reg[i])
        i = rd_len - 1
        while i >= 0:
            if i < len(self._reg):
                del self._reg[i]
            i -= 1
        return data

    def write(self, wr_data):
        for i in range(len(wr_data)):
            self._reg.append(wr_data[i])
