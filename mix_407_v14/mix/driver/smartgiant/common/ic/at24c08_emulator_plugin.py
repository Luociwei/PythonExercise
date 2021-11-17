# -*- coding: utf-8 -*-

__author__ = 'st@trantest.com'
__version__ = '0.1'


class AT24C08EmulatorPlugin(object):

    def __init__(self):
        self._eprom_size = 8192
        self._eep_adr = {addr: [0] for addr in range(self._eprom_size)}

    def write(self, addr, wr_data):
        eep_wr_adr = wr_data[0] | (addr & 0x03)
        wr_to_eep = [i for i in wr_data[1:]]
        for index in range(len(wr_to_eep)):
            self._eep_adr[eep_wr_adr + index] = [wr_to_eep[index]]

    def read(self, addr, wr_data, wr_len):
        raise NotImplementedError('AT24C08 no need to implement this function')

    def write_and_read(self, addr, wr_data, rd_len):
        eep_rd_adr = wr_data[0] | (addr & 0x03)
        rd_from_eep = [self._eep_adr[eep_rd_adr + index][0] for index in range(rd_len)]
        return rd_from_eep
