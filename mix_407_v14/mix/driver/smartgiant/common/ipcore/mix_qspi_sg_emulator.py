# -*- coding: utf-8 -*-
"""
This is a class of the implemention of PL SPI bus for Xavier emulator
"""
from mix.driver.core.tracer.recorder import *
from mix.driver.core.bus.axi4_lite_def import PLSPIDef


class MIXQSPISGException(Exception):
    pass


class MIXQSPISGEmulator(object):

    def __init__(self, dev_name, reg_size):
        self._dev_name = dev_name
        self._reg_size = reg_size
        self._cache_size = 64
        self._mode = 'MODE0'
        self._speed = PLSPIDef.DEFAULT_SPEED
        self._work_mode = PLSPIDef.SPI_MODE
        self._wait_us = 0
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self.open()

    def __del__(self):
        self.close()
        del_recorder(self._recorder)

    def _enable(self):
        pass

    def _disable(self):
        pass

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
            raise MIXQSPISGException('%s load plugin failed' % (self._dev_name))

        plugin_lower_name = module_name.replace('_', '').lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self._plugin = getattr(plugin_module, item)()
                break

        if self._plugin is None:
            raise MIXQSPISGException("%s can not find plugin %s" % (self._dev_name, plugin_lower_name))

    def open(self):
        self._recorder.record(str(self._dev_name) + " open")
        self._load_plugin()

    def close(self):
        self._recorder.record(str(self._dev_name) + " close")

    def get_mode(self):
        self._recorder.record("get mode")
        return self._mode

    def set_mode(self, mode):
        assert mode in PLSPIDef.SPI_MODES.keys()

        self._recorder.record("set mode:" + mode)
        self._mode = mode

    def get_speed(self):
        self._recorder.record("get speed")
        return self._speed

    def set_speed(self, speed):
        self._recorder.record("set mode:" + str(speed))
        self._speed = speed

    def set_work_mode(self, mode):
        self._recorder.record("set work mode:" + str(mode))
        self._work_mode = mode

    def get_work_mode(self):
        self._recorder.record("get work mode")
        return self._work_mode

    def write(self, wr_data):
        record_data = "["
        for i in range(len(wr_data)):
            record_data += "0x%02x" % (wr_data[i])
            if i != len(wr_data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write data " + record_data)

        self._plugin.write(wr_data)

    def read(self, rd_len):
        self._recorder.record("read %d bytes" % rd_len)

        return self._plugin.read(rd_len)

    def transfer(self, wr_data, rd_len, sync=True):
        record_data = "["
        for i in range(len(wr_data)):
            record_data += "0x%02x" % (wr_data[i])
            if i != len(wr_data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write data " + record_data + " and read %d bytes" % rd_len)
        return self._plugin.transfer(wr_data, rd_len, sync)

    def sync_transfer(self, wr_data):
        return self.transfer(wr_data, len(wr_data), sync=True)

    def async_transfer(self, wr_data, rd_len):
        return self.transfer(wr_data, rd_len, False)
