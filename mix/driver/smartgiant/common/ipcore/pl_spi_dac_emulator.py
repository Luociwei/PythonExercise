# -*- coding: utf-8 -*-

from mix.driver.core.tracer.recorder import *

__author__ = 'ouyangde@gzseeing.com'
__version__ = '0.1'


class PLSPIDACException(Exception):
    pass


class PLSPIDACEmulator(object):
    def __init__(self, dev_name):
        self.dev_name = dev_name
        self.recorder = Recorder()
        add_recorder(self.recorder)

    def __del__(self):
        del_recorder(self.recorder)

    def load_plugin(self):
        module_name = self.dev_name + "_plugin"
        import_error = False
        try:
            exec('from ..bus import {} as plugin_module'.format(module_name))
        except ImportError:
            import_error = True

        try:
            if import_error is True:
                import_error = False
                exec('from ..ipcore import {} as plugin_module'.format(module_name))
        except ImportError:
            import_error = True

        try:
            if import_error is True:
                import_error = False
                exec('from ..ic import {} as plugin_module'.format(module_name))
        except ImportError:
            import_error = True

        try:
            if import_error is True:
                exec('from ..module import {} as plugin_module'.format(module_name))
        except ImportError:
            raise PLSPIDACException('%s load plugin failed' % (self._dev_name))

        plugin_lower_name = module_name.replace('_', '').lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self._plugin = getattr(plugin_module, item)()
                break

        if self._plugin is None:
            raise PLSPIDACException("%s can not find plugin %s" % (self._dev_name, plugin_lower_name))

    def open(self):
        self.recorder.record(self.dev_name + " open")
        self.start_flag = True

    def close(self):
        self.recorder.record(self.dev_name + " close")
        self.start_flag = False

    def dac_mode_set(self, dac_mode):
        self.recorder.record(self.dev_name + " dac_mode_set: dac_mode is %s"
                             % dac_mode)

    def spi_sclk_frequency_set(self, sclk_freq_hz):
        self.recorder.record(self.dev_name + " spi_sclk_frequency_set: \
sclk_freq_hz is %r" % sclk_freq_hz)

    def sample_data_set(self, sample_rate):
        self.recorder.record(self.dev_name + " sample_data_set: \
sample_rate is %r" % sample_rate)

    def set_axi4_clk_frequency(self, clk_frequency):
        self.recorder.record(self.dev_name + " set_axi4_clk_frequency: \
clk_frequency is %r" % clk_frequency)

    def test_register(self, test_data):
        self.recorder.record(self.dev_name + " test_register: \
test_data is %r" % test_data)
