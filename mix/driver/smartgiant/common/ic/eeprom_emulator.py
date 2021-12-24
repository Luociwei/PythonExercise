# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class EepromEmulator(object):
    def __init__(self, dev_name):
        self._dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._regs = dict()

    def __del__(self):
        del_recorder(self._recorder)

    def read(self, address, length):
        assert length > 0
        assert address >= 0
        self._recorder.record("read 0x%02x with %d bytes" % (address, length))
        result = []
        for i in range(length):
            if address + i not in self._regs.keys():
                result.append(0)
            else:
                result.append(self._regs[address + i])

        return result

    def write(self, address, wr_data):
        assert address >= 0
        record_data = '['
        for i in range(len(wr_data)):
            self._regs[address + i] = wr_data[i]
            record_data += "0x%02x" % wr_data[i]
            if i != len(wr_data) - 1:
                record_data += ', '
        record_data += ']'

        self._recorder.record("write " + record_data + " to 0x%02x" % (address))
