# -*- coding: utf-8 -*-


class MIXQSPISGEmulatorPlugin(object):
    def __init__(self):
        self._reg = dict()

    def write(self, wr_data):
        for i in range(len(wr_data)):
            self._reg[i] = wr_data[i]

    def read(self, rd_len):
        data = []
        for i in range(rd_len):
            if i in self._reg.keys():
                data.append(self._reg[i])
            else:
                data.append(0)
        return data

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
