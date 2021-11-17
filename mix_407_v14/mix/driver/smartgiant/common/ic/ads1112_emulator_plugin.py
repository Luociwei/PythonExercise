# -*- coding: utf-8 -*-

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class ADS1112EmulatorPlugin(object):

    def __init__(self):
        self._config_reg = 0x8C

    def write(self, addr, wr_data):
        assert len(wr_data) < 2
        self._config_reg = wr_data[0]

    def read(self, addr, data_len=3):
        assert data_len > 0

        ouput_reg = [0, 0, 0]
        ouput_reg[0] = 0x7F
        ouput_reg[1] = 0xFF
        self._config_reg &= ~(1 << 7)
        ouput_reg[2] = self._config_reg
        return ouput_reg

    def write_and_read(self, addr, wr_data, rd_len):
        raise NotImplementedError('ADS1112 no need to implement this function')
