# -*- coding: utf-8 -*-

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.2'


class MIXSignalMeterSGEmulatorPlugin(object):

    def __init__(self):
        self._freq = 1000.0
        self._duty = 60.5
        self.vpp_data = 500.4
        self.max_data = 540.0
        self.min_data = 230.9
        self.rms_data = 400.3
        self.avg_data = 202.0

    def open(self):
        pass

    def close(self):
        pass

    def set_vpp_interval(self, test_interval_ms):
        pass

    def enable_upframe(self, upframe_mode):
        pass

    def disable_upframe(self):
        pass

    def start_measure(self, time_ms, sample_rate):
        return True

    def measure_frequency(self, measure_type):
        return self._freq

    def level(self):
        return 1

    def duty(self):
        return self._duty

    def vpp(self):
        return [0, 0, 0]

    def rms(self):
        return [2000, 2000, 2000]

