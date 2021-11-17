# -*- coding: utf-8 -*-
__author__ = 'zhiwei.deng@SmartGiant'
__version__ = '0.1'


class MIXAxiLiteToStreamSGEmulatorPlugin(object):
    def __init__(self):
        self._reg = range(0x20)
        self._reg[0x0C] = [4]
        self._reg[0x0D] = [4]
        self._reg[0x10] = [0x7f, 0x7f]
        self._reg[0x12] = [1]
        self._reg[0x14] = 4
        self._reg[0x18] = [1]

    def read_8bit_inc(self, addr, rd_len):
        return self._reg[addr]

    def write_32bit_fix(self, addr, data):
        pass

    def read_32bit_fix(self, addr, rd_len):
        return self._reg[addr]
