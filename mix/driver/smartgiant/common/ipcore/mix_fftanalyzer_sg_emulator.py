# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = "Zhangsong Deng"
__version__ = "1.0"


class MIXFftAnalyzerSGException(Exception):
    def __init__(self, err_str):
        self._err_reason = "%s." % (err_str)

    def __str__(self):
        return self._err_reason


class MIXFftAnalyzerSGEmulator(object):
    def __init__(self, dev_name):
        self.dev_name = dev_name
        self.plugin = None

        self.recorder = Recorder()
        add_recorder(self.recorder)

        self.load_plugin()

    def __del__(self):
        del_recorder(self.recorder)

    def load_plugin(self):
        module_name = self.dev_name + "_plugin"
        import_error = False
        try:
            exec("from ..bus import {} as plugin_module".format(module_name))
        except ImportError:
            import_error = True

        try:
            if import_error is True:
                import_error = False
                exec("from ..ipcore import {} as plugin_module".format(module_name))
        except ImportError:
            import_error = True

        try:
            if import_error is True:
                import_error = False
                exec("from ..IC import {} as plugin_module".format(module_name))
        except ImportError:
            import_error = True

        try:
            if import_error is True:
                exec("from ..module import {} as plugin_module".format(module_name))
        except ImportError:
            raise MIXFftAnalyzerSGException("%s load plugin failed" % (self.dev_name))

        plugin_lower_name = module_name.replace("_", "").lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self.plugin = getattr(plugin_module, item)()
                break

        if self.plugin is None:
            raise MIXFftAnalyzerSGException("%s can not find plugin %s" % (self.dev_name, plugin_lower_name))

    def enable(self):
        self.recorder.record("%s module enable" % (self.dev_name))

    def disable(self):
        self.recorder.record("%s module disable" % (self.dev_name))

    def enable_upload(self):
        self.recorder.record("%s data upload enable" % (self.dev_name))

    def disable_upload(self):
        self.recorder.record("%s data upload disable" % (self.dev_name))

    def analyze_config(self, sample_rate, decimation_type, bandwidth='auto', harmonic_count=None, freq_point=None):
        self.recorder.record("%s measure config: bandwidth is %s, sample_rate is %s, decimation_type \
is %s, harmonic_count is %s, freq_point is %s" % (self.dev_name, bandwidth, sample_rate, decimation_type,
                                                  harmonic_count, freq_point))

    def analyze(self):
        self.recorder.record("%s start analyze" % (self.dev_name))

    def get_vpp_by_freq(self):
        return self.plugin.vpp_by_freq

    def get_frequency(self):
        return self.plugin.frequency

    def get_vpp(self):
        return self.plugin.vpp

    def get_thdn(self):
        return self.plugin.thdn

    def get_thd(self):
        return self.plugin.thd
