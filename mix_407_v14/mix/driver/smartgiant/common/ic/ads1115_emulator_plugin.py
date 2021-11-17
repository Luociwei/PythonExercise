# -*- coding: utf-8 -*-

__author__ = 'edison@trantest.com'
__version__ = '0.1'


class ADS1115EmulatorPlugin(object):
    CONVERSION_REGISTER = 0x0
    CONFIG_REGISTER = 0x01
    LO_THRESH_REGISTER = 0x02
    HI_THRESH_REGISTER = 0x03

    def __init__(self):
        ''' Please hw_init 0x01, 0x02, 0x03 register value at first.
            CONVERSION_REGISTER we set a fake value(0x0) to dict.'''
        self._reg = {ADS1115EmulatorPlugin.CONVERSION_REGISTER: [0, 0]}
        self._reg[ADS1115EmulatorPlugin.CONFIG_REGISTER] = [0x85, 0x83]

    def write(self, addr, wr_data):
        assert len(wr_data) < 4
        reg_addr = wr_data[0]
        wr_to_reg = [i for i in wr_data[1:]]
        self._reg[reg_addr] = wr_to_reg

    def read(self, addr, wr_data=[], wr_len=2):
        raise NotImplementedError('ADS1115 no need to implement this function')

    def write_and_read(self, addr, wr_data, rd_len):
        assert rd_len > 0
        assert len(wr_data) > 0
        reg_addr = wr_data[0]
        return self._reg[reg_addr][0: rd_len]
