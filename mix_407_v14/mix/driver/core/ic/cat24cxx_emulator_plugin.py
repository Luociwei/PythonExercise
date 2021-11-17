# -*- coding: utf-8 -*-


class CAT24CXXEmulatorPlugin(object):
    def __init__(self):
        self.reg = dict()
        self.address_byte = 2
        self.current_addr = 0x00

    def read(self, addr, rd_len):
        addr = _self.current_addr
        data = []
        for i in range(rd_len):
            if addr + i in self.reg.keys():
                data.append(self.reg[addr + i])
            else:
                data.append(0)
        return data

    def write(self, addr, wr_data):
        addr = wr_data[0] if self.address_byte == 1 else wr_data[0] << 8 | wr_data[1]
        self.current_addr = addr
        for i, data in enumerate(wr_data[self.address_byte:]):
            self.reg[addr + i] = data

    def write_and_read(self, addr, wr_data, rd_len):
        addr = wr_data[0] if self.address_byte == 1 else wr_data[0] << 8 | wr_data[1]
        self.current_addr = addr
        for i, data in enumerate(wr_data[self.address_byte:]):
            self.reg[addr + i] = data

        data = []
        for i in xrange(rd_len):
            if addr + i in self.reg.keys():
                data.append(self.reg[addr + i])
            else:
                data.append(0)
        return data
