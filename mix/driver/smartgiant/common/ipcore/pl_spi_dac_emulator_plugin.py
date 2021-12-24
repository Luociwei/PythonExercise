# -*- coding: utf-8 -*-

__author__ = 'ouyangde@gzseeing.com'
__version__ = '0.1'


class PLSPIDACEmulatorPlugin(object):
    def __init__(self):
        self.start_flag = True
        self.dac_mode = None
        self.sclk_freq_hz = None
        self.sample_rate = None
        self.clk_frequency = None
        self.test_data = None

    def open(self):
        self.start_flag = True

    def close(self):
        self.start_flag = False

    def dac_mode_set(self, dac_mode):
        self.dac_mode = dac_mode

    def spi_sclk_frequency_set(self, sclk_freq_hz):
        self.sclk_freq_hz = sclk_freq_hz

    def sample_data_set(self, sample_rate):
        self.sample_rate = sample_rate

    def set_axi4_clk_frequency(self, clk_frequency):
        self.clk_frequency = clk_frequency

    def test_register(self, test_data):
        self.test_data = test_data
