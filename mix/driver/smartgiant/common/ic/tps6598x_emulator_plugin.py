# -*- coding: utf-8 -*-


class TPS6598xEmulatorPlugin(object):
    def __init__(self):
        self._reg = dict()

    def read(self, addr, rd_len):
        data = []
        for i in range(rd_len):
            if addr + i in self._reg.keys():
                data.append(self._reg[addr + i])
            else:
                data.append(0)
        return data

    def write(self, addr, wr_data):
        reg_addr = wr_data[0]
        wr_to_reg = [i for i in wr_data[1:]]
        self._reg[reg_addr] = wr_to_reg

    def write_and_read(self, addr, wr_data, rd_len):
        reg_addr = wr_data[0]
        if reg_addr == 0x08 or reg_addr == 0x09:
            data = [0] * rd_len
        elif reg_addr in self._reg:
            data = [self._reg[reg_addr][index] for index in range(rd_len)]
        else:
            data = [0] * rd_len
        return data
