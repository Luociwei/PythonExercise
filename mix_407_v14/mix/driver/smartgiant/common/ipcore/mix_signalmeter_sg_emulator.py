# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.2'


class MIXSignalMeterSGException(Exception):
    pass


class MIXSignalMeterSGEmulator(object):
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
            raise MIXSignalMeterException('%s load plugin failed' % (self._dev_name))

        plugin_lower_name = module_name.replace('_', '').lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self._plugin = getattr(plugin_module, item)()
                break

        if self._plugin is None:
            raise MIXSignalMeterException("%s can not find plugin %s" % (self._dev_name, plugin_lower_name))

    def open(self):
        self._recorder.record(str(self._dev_name) + " open")
        self._load_plugin()

    def close(self):
        self._recorder.record(str(self._dev_name) + " close")

    def set_vpp_interval(self, test_interval_ms):
        self._recorder.record(
            self._dev_name + " set_vpp_interval: %d"
            % (test_interval_ms))

    def enable_upframe(self, upframe_mode):
        self._recorder.record(
            self._dev_name + " enable_upframe %s" % (upframe_mode))
        return self._plugin.enable_upframe(upframe_mode)

    def disable_upframe(self):
        self._recorder.record(str(self._dev_name) + " disable_upframe")

    def start_measure(self, time_ms, sample_rate, measure_mask=0x00):
        self._recorder.record(
            self._dev_name + " start_measure: %d %d" % (time_ms, sample_rate))
        return True

    def measure_frequency(self, measure_type):
        self._recorder.record(
            self._dev_name + " measure_frequency: %s" % (measure_type))
        return self._plugin.measure_frequency(measure_type)

    def level(self):
        self._recorder.record(self._dev_name + " measure_level")
        return self._plugin.level()

    def duty(self):
        self._recorder.record(self._dev_name + " measure_duty")
        return self._plugin.duty()

    def vpp(self):
        self._recorder.record(self._dev_name + " measure_vpp")
        return self._plugin.vpp()

    def rms(self):
        self._recorder.record(self._dev_name + " measure_rms")
        return self._plugin.rms()
