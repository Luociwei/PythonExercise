# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class AD717XEmulator(object):

    def __init__(self, dev_name):
        self._dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self.RATE = {"ch0": 0x00, "ch1": 0x00, "ch2": 0x00, "ch3": 0x00}
        self.set_setup_register("ch0")
        self.set_setup_register("ch1")

    def __del__(self):
        del_recorder(self._recorder)

    def channel_init(self, channel):
        self._recorder.record("%s channel init %s" % (self._dev_name, channel))

    def reset(self):
        self._recorder.record("%s reset" % (self._dev_name))

    def set_setup_register(self, channel, code_polar="bipolar", reference="extern", buffer_flag="enable"):
        self._recorder.record("%s set setup register %s" % (self._dev_name, channel))

    def set_sampling_rate(self, channel, rate):
        self._recorder.record("%s set sampling rate is %d" % (self._dev_name, rate))
        self.RATE[channel] = rate

    def get_sampling_rate(self, channel):
        self._recorder.record("%s get sampling rate" % (self._dev_name))
        return self.RATE[channel]

    def set_channel_state(self, channel, state):
        self._recorder.record("%s set channel state" % (self._dev_name))

    def select_single_channel(self, channel):
        self._recorder.record("%s select single channel" % (self._dev_name))

    def read_volt(self, channel, timeout_sec=1):
        self._recorder.record("%s read volt %s" % (self._dev_name, channel))

    def is_communication_ok(self):
        self._recorder.record("%s is communication ok" % (self._dev_name))
