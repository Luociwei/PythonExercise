# -*- coding: utf-8 -*-

from mix.driver.core.tracer.recorder import *

__author__ = 'ouyangde@gzseeing.com'
__version__ = '0.1'


class MIXSignalSourceSGException(Exception):
    pass


class MIXSignalSourceSGEmulator(object):
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
            raise MIXSignalSourceSGException('%s load plugin failed' % (self.dev_name))

        plugin_lower_name = module_name.replace('_', '').lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self._plugin = getattr(plugin_module, item)()
                break

        if self._plugin is None:
            raise MIXSignalSourceSGException("%s can not find plugin %s" % (self.dev_name, plugin_lower_name))

    def open(self):
        self.recorder.record(self.dev_name + " open")
        self.start_flag = True

    def close(self):
        self.recorder.record(self.dev_name + " close")
        self.start_flag = False

    def set_signal_type(self, signal_type):
        self.recorder.record(self.dev_name + " set_signal_type: %s" %
                             signal_type)

    def set_signal_time(self, signal_time):
        self.recorder.record(self.dev_name + " set_signal_time: %r" %
                             signal_time)

    def set_swg_paramter(self, sample_rate, signal_frequency, vpp_scale,
                         square_duty, offset_volt=0):
        self.recorder.record(self.dev_name + " set_swg_paramter: sample_rate is %r\
, signal_frequency is %r, vpp_scale is %r, square_duty is %r, \
offset_volt is %r" % (sample_rate, signal_frequency, vpp_scale,
                      square_duty, offset_volt))

    def output_signal(self):
        self.recorder.record(self.dev_name + " output_signal")

    def set_awg_step(self, sample_rate, start_volt, stop_volt, duration_ms):
        self.recorder.record(self.dev_name + " _set_awg_step: sample_rate is %r,\
 start_volt is %r, stop_volt is %r, duration_ms is %r" % (sample_rate,
                                                          start_volt,
                                                          stop_volt,
                                                          duration_ms))

    def set_awg_parameter(self, sample_rate, awg_step):
        self.recorder.record(self.dev_name + " set_awg_parameter: sample_rate is %r,\
 awg_step is %r" % (sample_rate, awg_step))
