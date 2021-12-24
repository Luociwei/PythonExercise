# -*- coding: utf-8 -*-

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.1'


class AD5272EmulatorPlugin(object):
    RDAC_DEFAULT = 0x2
    CONTROL_DEFAULT = 0x8

    def __init__(self):
        self._reg = dict()
        self.write(0x2c, [AD5272EmulatorPlugin.RDAC_DEFAULT << 2, 0x00])
        self.write(0x2c, [AD5272EmulatorPlugin.CONTROL_DEFAULT << 2, 0x00])

    def write(self, addr, wr_data):
        assert len(wr_data) < 4
        reg_addr = wr_data[0] >> 2
        wr_to_reg = [wr_data[0], wr_data[1]]
        self._reg[reg_addr] = wr_to_reg

    def read(self, addr, wr_len=2):
        return [0x1, 0x2]

    def write_and_read(self, addr, wr_data, rd_len):
        assert rd_len > 0
        assert len(wr_data) > 0
        reg_addr = (wr_data[0] - 1)
        return self._reg[reg_addr][0: rd_len]
