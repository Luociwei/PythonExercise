# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class AD5675Emulator(object):
    def __init__(self, dev_name):
        self.dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def set_mode(self, channel, mode):
        self._recorder.record("set channel{} to mode {}".format(channel, mode))

    def get_gain(self):
        self._recorder.record("get gain")

    def set_gain(self, gain):
        self._recorder.record("set gain to {}".format(gain))

    def output_volt_dc(self, channel, volt):
        self._recorder.record("channel{} output voltage {}mV".format(channel, volt))

    def ldac_pin_disable(self, channel='all'):
        self._recorder.record("ldac pin disable")

    def ldac_pin_enable(self, channel='all'):
        self._recorder.record("ldac pin enable")
