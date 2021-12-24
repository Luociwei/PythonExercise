# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.1'


class ADCBusException(Exception):
    pass


class PLSPIADCEmulator(object):
    def __init__(self, dev_name, reg_size):
        self._dev_name = dev_name
        self._reg_size = reg_size

        self._reg = dict()
        self._recorder = Recorder()
        add_recorder(self._recorder)

        self.open()

    def __del__(self):
        del_recorder(self._recorder)
        self.close()

    def _load_plugin(self):
        module_name = self._dev_name + "_plugin"
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
            raise ADCBusException('%s load plugin failed' % (self._dev_name))

        plugin_lower_name = module_name.replace('_', '').lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self._plugin = getattr(plugin_module, item)()
                break

        if self._plugin is None:
            raise ADCBusException("%s can not find plugin %s" % (self._dev_name, plugin_lower_name))

    def open(self):
        self._recorder.record(self._dev_name + " open")
        self._load_plugin()

    def close(self):
        self._recorder.record(self._dev_name + " close")

    def set_sample_rate(self, sample_rate):
        self._recorder.record(self._dev_name + " set_sample_rate: %d" % sample_rate)
        self._plugin.set_sample_rate(sample_rate)

    def get_sample_data(self):
        self._recorder.record(self._dev_name + " get_sample_rate")
        return self._plugin.get_sample_rate()

