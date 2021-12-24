# -*- coding: utf-8 -*-
import ctypes
from ..tracer.recorder import *

_MAGIC_NUM = 1


class AXI4LiteLibException(Exception):
    pass


class AXI4LiteBusLibEmulator(object):
    def __init__(self):
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._load_plugin()

    def __del__(self):
        del_recorder(self._recorder)

    def _load_plugin(self):
        module_name = "axi4_bus_emulator_plugin"
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

    def axi4_lite_open(self, dev_name, reg_size):
        self._dev_name = "axi4_bus_emulator"
        self._reg_size = reg_size
        self._recorder.record("open " + self._dev_name)
        return _MAGIC_NUM  # just used for emulator

    def axi4_lite_close(self, ptr):
        self._recorder.record("close " + self._dev_name)

    def axi4_lite_read_8bit_fix(self, ptr, addr, rd_data, rd_len):
        assert isinstance(rd_data, (ctypes.c_ubyte * rd_len))
        assert addr >= 0 and addr < self._reg_size

        if ptr == 0:
            return -1

        self._recorder.record("read_8bit_fix read 0x%02x with %d bytes" % (addr, rd_len))

        result = self._plugin.read_8bit_fix(addr, rd_len)
        for i in range(rd_len):
            rd_data[i] = result[i]
        return 0

    def axi4_lite_write_8bit_fix(self, ptr, addr, data, wr_len):
        assert isinstance(data, (ctypes.c_ubyte * wr_len))
        assert addr >= 0 and addr < self._reg_size

        if ptr == 0:
            return -1

        record_data = "["
        for i in range(len(data)):
            record_data += "0x%02x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_8bit_fix write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_8bit_fix(addr, list(data))
        return 0

    def axi4_lite_read_16bit_fix(self, ptr, addr, rd_data, rd_len):
        assert isinstance(rd_data, (ctypes.c_ushort * rd_len))
        assert addr >= 0 and addr < self._reg_size

        if ptr == 0:
            return -1

        self._recorder.record("read_16bit_fix read 0x%02x with %d half words" % (addr, rd_len))

        result = self._plugin.read_16bit_fix(addr, rd_len)
        for i in range(rd_len):
            rd_data[i] = result[i]
        return 0

    def axi4_lite_write_16bit_fix(self, ptr, addr, data, wr_len):
        assert isinstance(data, (ctypes.c_ushort * wr_len))
        assert addr >= 0 and addr < self._reg_size

        if ptr == 0:
            return -1

        record_data = "["
        for i in range(len(data)):
            record_data += "0x%04x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_16bit_fix write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_16bit_fix(addr, list(data))
        return 0

    def axi4_lite_read_32bit_fix(self, ptr, addr, rd_data, rd_len):
        assert isinstance(rd_data, (ctypes.c_uint * rd_len))
        assert addr >= 0 and addr < self._reg_size

        if ptr == 0:
            return -1

        self._recorder.record("read_32bit_fix read 0x%02x with %d words" % (addr, rd_len))

        result = self._plugin.read_32bit_fix(addr, rd_len)
        for i in range(rd_len):
            rd_data[i] = result[i]
        return 0

    def axi4_lite_write_32bit_fix(self, ptr, addr, data, wr_len):
        assert isinstance(data, (ctypes.c_uint * wr_len))
        assert addr >= 0 and addr < self._reg_size

        if ptr == 0:
            return -1

        record_data = "["
        for i in range(len(data)):
            record_data += "0x%08x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_32bit_fix write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_32bit_fix(addr, list(data))
        return 0

    def axi4_lite_read_8bit_inc(self, ptr, addr, rd_data, rd_len):
        assert isinstance(rd_data, (ctypes.c_ubyte * rd_len))
        assert addr >= 0 and (addr + rd_len <= self._reg_size)

        if ptr == 0:
            return -1

        self._recorder.record("read_8bit_inc read 0x%02x with %d bytes" % (addr, rd_len))
        result = self._plugin.read_8bit_inc(addr, rd_len)
        for i in range(rd_len):
            rd_data[i] = result[i]
        return 0

    def axi4_lite_write_8bit_inc(self, ptr, addr, data, wr_len):
        assert addr >= 0 and (addr + len(data) <= self._reg_size)

        if ptr == 0:
            return -1

        record_data = "["
        for i in range(len(data)):
            record_data += "0x%02x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_8bit_inc write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_8bit_inc(addr, list(data))
        return 0

    def axi4_lite_read_16bit_inc(self, ptr, addr, rd_data, rd_len):
        assert isinstance(rd_data, (ctypes.c_ushort * rd_len))
        assert addr >= 0
        assert addr + rd_len * 2 <= self._reg_size

        if ptr == 0:
            return -1

        self._recorder.record("read_16bit_inc read 0x%02x with %d half words" % (addr, rd_len))

        result = self._plugin.read_16bit_inc(addr, rd_len)
        for i in range(rd_len):
            rd_data[i] = result[i]
        return 0

    def axi4_lite_write_16bit_inc(self, ptr, addr, data, wr_len):
        assert isinstance(data, (ctypes.c_ushort * wr_len))
        assert addr >= 0
        assert addr + len(data) * 2 <= self._reg_size

        if ptr == 0:
            return -1

        record_data = "["
        for i in range(len(data)):
            record_data += "0x%04x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_16bit_inc write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_16bit_inc(addr, list(data))
        return 0

    def axi4_lite_read_32bit_inc(self, ptr, addr, rd_data, rd_len):
        assert isinstance(rd_data, (ctypes.c_uint * rd_len))
        assert addr >= 0
        assert (addr + rd_len * 4 <= self._reg_size)

        if ptr == 0:
            return -1

        self._recorder.record("read_32bit_inc read 0x%02x with %d words" % (addr, rd_len))

        result = self._plugin.read_32bit_inc(addr, rd_len)
        for i in range(rd_len):
            rd_data[i] = result[i]
        return 0

    def axi4_lite_write_32bit_inc(self, ptr, addr, data, wr_len):
        assert isinstance(data, (ctypes.c_uint * wr_len))
        assert addr >= 0
        assert addr + len(data) * 4 <= self._reg_size

        if ptr == 0:
            return -1

        record_data = "["
        for i in range(len(data)):
            record_data += "0x%08x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_32bit_inc write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_32bit_inc(addr, list(data))
        return 0

    def axi4_lite_get_ipcore_ver(self, ptr):
        return "V0.1"
