# -*- coding: utf-8 -*-
import ctypes
from ..tracer.recorder import *


_MAGIC_NUM = 1


class I2CLibEmulator(object):
    def __init__(self):
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._load_plugin()

    def __del__(self):
        del_recorder(self._recorder)

    def _load_plugin(self):
        module_name = "i2c_emulator_plugin"
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
            raise AXI4LiteLibException('%s load plugin failed' % (self._dev_name))

        plugin_lower_name = module_name.replace('_', '').lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self._plugin = getattr(plugin_module, item)()
                break
        if self._plugin is None:
            raise AXI4LiteLibException("%s can not find plugin %s" % (self._dev_name, plugin_lower_name))

    def i2c_open(self, dev_name):
        self._dev_name = "i2c_bus_emulator"
        self._recorder.record("open " + self._dev_name)
        return _MAGIC_NUM

    def i2c_close(self, ptr):
        self._recorder.record("close " + self._dev_name)

    def i2c_write(self, ptr, addr, wr_data, wr_len):
        assert isinstance(wr_data, (ctypes.c_ubyte * wr_len))

        if ptr == 0:
            return -1
        record_data = '['
        for i in range(len(wr_data)):
            record_data += "0x%02x" % wr_data[i]
            if i != len(wr_data) - 1:
                record_data += ', '
        record_data += ']'
        self._recorder.record("write " + record_data + " to 0x%02x" % addr)

        self._plugin.write(addr, wr_data)

        return 0

    def i2c_read(self, ptr, addr, rd_data, rd_len):
        assert isinstance(rd_data, (ctypes.c_ubyte * rd_len))
        if ptr == 0:
            return -1
        self._recorder.record("read from 0x%02x with %d bytes" % (addr, rd_len))

        result = self._plugin.read(addr, rd_len)
        for i in range(rd_len):
            rd_data[i] = result[i]
        return 0

    def i2c_write_and_read(self, ptr, addr, wr_data, wr_len, rd_data, rd_len):
        assert isinstance(wr_data, (ctypes.c_ubyte * wr_len))
        assert isinstance(rd_data, (ctypes.c_ubyte * rd_len))

        if ptr == 0:
            return -1

        record_data = '['
        for i in range(len(wr_data)):
            record_data += "0x%02x" % wr_data[i]
            if i != len(wr_data) - 1:
                record_data += ', '
        record_data += ']'
        self._recorder.record("write_and_read write " + record_data + " to 0x%02x, read %d bytes" % (addr, rd_len))

        result = self._plugin.write_and_read(addr, wr_data, rd_len)
        for i in range(rd_len):
            rd_data[i] = result[i]
        return 0
