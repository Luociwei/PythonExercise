# -*- coding:utf-8 -*-
from mix.driver.core.tracer.recorder import *


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class ADS1110Emulator(object):
    def __init__(self, dev_name):
        self.dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def initial(self, data_rate='15SPS', gain_set='GAIN_1'):
        self._recorder.record("initial: sample rate is {}, gain is {}".format(data_rate, gain_set))

    def read_volt(self, channel=0):
        self._recorder.record("read voltage")
        return 100.0
