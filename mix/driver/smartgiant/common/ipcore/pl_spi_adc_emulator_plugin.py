# -*- coding: utf-8 -*-

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.1'


class PLSPIADCEmulatorPlugin(object):

    def __init__(self):
        self.sample_rate = 0.0

    def open(self):
        pass

    def close(self):
        pass

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate

    def get_sample_rate(self):
        return self.sample_rate

