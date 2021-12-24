# -*- coding: utf-8 -*-

__author__ = 'ouyangde@gzseeing.com'
__version__ = '0.1'


class MIXSignalSourceSGEmulatorPlugin(object):
    def __init__(self):
        self.start_flag = True
        self.signal_type = ""
        self.signal_time = ""
        self.signal_frequency = ""

    def open(self):
        self.start_flag = True

    def close(self):
        self.start_flag = False

    def set_signal_type(self, signal_type):
        self.signal_type = signal_type

    def set_signal_time(self, signal_time):
        self.signal_time = signal_time

    def set_swg_paramter(self, sample_rate, signal_frequency, vpp_scale,
                         square_duty, offset_volt=0):
        pass

    def output_signal(self):
        pass

    def set_awg_step(self, sample_rate, start_volt, stop_volt, duration_ms):
        pass

    def set_awg_parameter(self, sample_rate, awg_step):
        pass
