# -*- coding: utf-8 -*-

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class AD569XEmulatorPlugin(object):

    def __init__(self):
        self._reg = [0, 0, 0]

    def write(self, addr, wr_data):
        assert len(wr_data) < 4
        if len(wr_data) > 1:
            self._reg = [i for i in wr_data]

    def read(self, addr, data_len=2):
        assert data_len > 0
        return self._reg[1:]

    def write_and_read(self, addr, wr_data, rd_len):
        raise NotImplementedError('AD569X no need to implement this function')
