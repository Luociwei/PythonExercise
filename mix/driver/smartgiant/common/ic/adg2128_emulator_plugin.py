# -*- coding: utf-8 -*-

__author__ = 'zijian.xu@SmartGiant'
__version__ = '0.1'


class ADG2128EmulatorPlugin(object):
    def __init__(self):
        self._reg = dict()
        self.switch = [0] * 96
        self.xline_readback_addr = [
            0x34, 0x3c, 0x74, 0x7c, 0x35, 0x3d,
            0x75, 0x7d, 0x36, 0x3e, 0x76, 0x7e
        ]
        self.x_line_write_address = {
            0x00: 0x01, 0x01: 0x02,
            0x02: 0x02, 0x03: 0x03,
            0x04: 0x04, 0x05: 0x05,
            0x08: 0x06, 0x09: 0x07,
            0x0A: 0x08, 0x0B: 0x09,
            0x0C: 0x0a, 0x0D: 0x0b
        }

    def dump(self):
        print(self._reg)

    def write(self, addr, wr_data):
        decode_addr = wr_data[0]
        mode = wr_data[1] & 0x01
        x_index = self.x_line_write_address[(decode_addr & ~(1 << 7)) >> 3]
        index = x_index * 8 + (0x07 & decode_addr)
        self.switch[index] = (decode_addr >> 7) & 0x01

    def read(self, addr, wr_data, wr_len):
        raise NotImplementedError('ADG2128 no need to implement this function')

    def write_and_read(self, addr, wr_data, rd_len):
        decode_addr = wr_data[0]
        index = self.xline_readback_addr.index(decode_addr)
        xline_state = 0
        for i in range(8):
            xline_state |= self.switch[index * 8 + i] << i
        rd_data = [0, xline_state]
        return rd_data[:rd_len]
