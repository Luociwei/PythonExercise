# -*- coding: utf-8 -*-

__author__ = 'elee@trantest.com'
__version__ = '0.1'


class AD5693EmulatorPlugin(object):
    ''' Chip driver please hw initial reg dict for five key:0x00, 0x10, 0x20, 0x30, 0x40
        in tern of SPEC '''
    def __init__(self):
        self.reg = dict()

    def dump(self):
        print(self.reg)

    def write(self, addr, wr_data):
        reg_addr = wr_data[0]
        self.reg[reg_addr] = wr_data[1:]

    def read(self, addr, wr_data, wr_len):
        raise NotImplementedError('AD5693 no need to implement this function')

    def write_and_read(self, addr, wr_data, rd_len):
        reg_addr = wr_data[0]
        assert (reg_addr >> 4) is 1
        return self.reg[reg_addr]
