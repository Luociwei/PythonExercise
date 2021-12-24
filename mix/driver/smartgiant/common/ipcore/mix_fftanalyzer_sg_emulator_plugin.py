# -*- coding: utf-8 -*-

__author__ = "Zhangsong Deng"
__version__ = "1.0"


class MIXFftAnalyzerSGEmulatorPlugin(object):
    def __init__(self):
        self.frequency = 10000
        self.vpp_by_freq = 0.899
        self.thdn = 100
        self.thd = 1000
        self.vpp = 0.5

    def enable(self):
        pass

    def disable(self):
        pass

    def data_upload_enable(self):
        pass

    def data_upload_disable(self):
        pass

    def analyze_config(self, sample_rate, decimation_type, bandwidth='auto', harmonic_count=None, freq_point=None):
        pass

    def analyze(self):
        pass
