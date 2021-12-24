# -*- coding:utf-8 -*-

__author__ = 'zijian.xu@SmartGiant'
__version__ = '0.1'


class AD57X1REmulatorPlugin(object):
    def __init__(self):
        self._reg = dict()
        self.input_shift_register = 0x0000
        self.dac_register = 0x0000
        self.control_register = 0x0000
        self.current_cmd = 0x0
        self.cmds = [0x1, 0x2, 0x3, 0x4, 0x7, 0xa, 0xb, 0xc, 0xf]

    def write(self, wr_data):
        cmd = wr_data[0]
        data = wr_data[1] << 8 | wr_data[2]
        if cmd not in self.cmds:
            return
        if cmd == 0x1:
            self.input_shift_register = data
        elif cmd == 0x2:
            self.dac_register = self.input_shift_register
        elif cmd == 0x3:
            self.dac_register = data
        elif cmd == 0x4:
            self.control_register = data
        elif cmd == 0x7:
            pass
        elif cmd == 0xf:
            pass
        else:
            self.current_cmd = cmd

    def read(self, rd_len):
        cmd = self.current_cmd
        data = list()
        if cmd == 0xa:
            data = [cmd, self.input_shift_register >> 8,
                    self.input_shift_register & 0x00ff]
        elif cmd == 0xb:
            data = [cmd, self.dac_register >> 8,
                    self.dac_register & 0x00ff]
        elif cmd == 0xc:
            data = [cmd, self.control_register >> 8,
                    self.control_register & 0x00ff]
        else:
            data = [1, 2, 3, 4]
        data1 = data[0:rd_len]
        return data1

    def transfer(self, wr_data, rd_len, sync=True):
        for index in range(len(wr_data)):
            self._reg[index] = wr_data[index]
        result_data = []
        if sync is True:
            for index in range(len(wr_data)):
                if index in self._reg.keys():
                    result_data.append(self._reg[index])
                else:
                    result_data.append(0)
            return result_data
        else:
            for index in range(rd_len):
                if index in self._reg.keys():
                    result_data.append(self._reg[index])
                else:
                    result_data.append(0)
        return result_data


