# -*- coding: utf-8 -*-
"""
This is a class of the implemention of AXI4Lite bus for Xavier emulator
"""
from mix.driver.core.tracer.recorder import *


class AXI4LiteBusException(Exception):
    pass


class AXI4LiteBusEmulator(object):
    def __init__(self, dev_name, reg_size):
        self._dev_name = dev_name
        self._reg_size = reg_size
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self.open()

    def __del__(self):
        self.close()
        del_recorder(self._recorder)

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
            raise AXI4LiteBusException('%s load plugin failed' % (self._dev_name))

        plugin_lower_name = module_name.replace('_', '').lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self._plugin = getattr(plugin_module, item)()
                break
        if self._plugin is None:
            raise AXI4LiteBusException("%s can not find plugin %s" % (self._dev_name, plugin_lower_name))

    def open(self):
        self._recorder.record("open " + self._dev_name)
        self._load_plugin()

    def close(self):
        self._recorder.record("close " + self._dev_name)

    def read_8bit_fix(self, addr, rd_len):
        assert addr >= 0 and addr < self._reg_size

        self._recorder.record("read_8bit_fix read 0x%02x with %d bytes" % (addr, rd_len))

        return self._plugin.read_8bit_fix(addr, rd_len)

    def write_8bit_fix(self, addr, data):
        assert addr >= 0 and addr < self._reg_size
        record_data = "["
        for i in range(len(data)):
            record_data += "0x%02x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_8bit_fix write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_8bit_fix(addr, data)

    def get_ipcore_id(self):
        self._recorder.record("get ipcore id")
        return self._plugin.get_ipcore_id()

    def get_ipcore_version(self):
        self._recorder.record("get ipcore version")
        return self._plugin.get_ipcore_version()

    def get_ipcore_board_id(self):
        self._recorder.record("get ipcore board id")
        return self._plugin.get_ipcore_board_id()

    def check_ipcore_id(self, ipcore_id):
        value = self.get_ipcore_id()
        if ipcore_id != value:
            raise AXI4LiteBusException(self._dev_name,
                                       "Check ipcore ID failed. ipcore ID is 0x{:02x}\
                                       , expected ipcore ID is {:02x}".format(value, ipcore_id))

    def check_ipcore_version(self, min_version, max_version):
        assert min_version >= 0 and min_version <= 0xFF
        assert max_version >= 0 and max_version <= 0xFF
        assert min_version < max_version
        value = self.get_ipcore_version()
        if (value < min_version) or (value > max_version):
            raise AXI4LiteBusException("Check ipcore version failed. ipcore version is 0x{:02x}.".format(value))

    def check_ipcore_board_id(self, board_id):
        assert board_id >= 0 and board_id <= 0xFF
        value = self.get_ipcore_board_id()
        if board_id != value:
            raise AXI4LiteBusException("Check board ID failed. Board ID is 0x{:02x}".format(value))

    def read_16bit_fix(self, addr, rd_len):
        assert addr >= 0 and addr < self._reg_size

        self._recorder.record("read_16bit_fix read 0x%02x with %d half words" % (addr, rd_len))

        return self._plugin.read_16bit_fix(addr, rd_len)

    def write_16bit_fix(self, addr, data):
        assert addr >= 0 and addr < self._reg_size
        record_data = "["
        for i in range(len(data)):
            record_data += "0x%04x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_16bit_fix write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_16bit_fix(addr, data)

    def read_32bit_fix(self, addr, rd_len):
        assert addr >= 0 and addr < self._reg_size

        self._recorder.record("read_32bit_fix read 0x%02x with %d words" % (addr, rd_len))

        return self._plugin.read_32bit_fix(addr, rd_len)

    def write_32bit_fix(self, addr, data):
        assert addr >= 0 and addr < self._reg_size
        record_data = "["
        for i in range(len(data)):
            record_data += "0x%08x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_32bit_fix write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_32bit_fix(addr, data)

    def read_8bit_inc(self, addr, rd_len):
        assert addr >= 0 and (addr + rd_len <= self._reg_size)

        self._recorder.record("read_8bit_inc read 0x%02x with %d bytes" % (addr, rd_len))
        return self._plugin.read_8bit_inc(addr, rd_len)

    def write_8bit_inc(self, addr, data):
        assert addr >= 0 and (addr + len(data) <= self._reg_size)

        record_data = "["
        for i in range(len(data)):
            record_data += "0x%02x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_8bit_inc write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_8bit_inc(addr, data)

    def read_16bit_inc(self, addr, rd_len):
        assert addr >= 0
        assert addr + rd_len * 2 <= self._reg_size

        self._recorder.record("read_16bit_inc read 0x%02x with %d half words" % (addr, rd_len))

        return self._plugin.read_16bit_inc(addr, rd_len)

    def write_16bit_inc(self, addr, data):
        assert addr >= 0
        assert addr + len(data) * 2 <= self._reg_size

        record_data = "["
        for i in range(len(data)):
            record_data += "0x%04x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_16bit_inc write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_16bit_inc(addr, data)

    def read_32bit_inc(self, addr, rd_len):
        assert addr >= 0
        assert (addr + rd_len * 4 <= self._reg_size)

        self._recorder.record("read_32bit_inc read 0x%02x with %d words" % (addr, rd_len))

        return self._plugin.read_32bit_inc(addr, rd_len)

    def write_32bit_inc(self, addr, data):
        assert addr >= 0
        assert addr + len(data) * 4 <= self._reg_size

        record_data = "["
        for i in range(len(data)):
            record_data += "0x%08x" % (data[i])
            if i != len(data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write_32bit_inc write " + str(record_data) + " to 0x%02x" % addr)

        self._plugin.write_32bit_inc(addr, data)

    def get_ipcore_ver(self):
        return "V0.1"


class AXI4LiteSubBusEmulator(AXI4LiteBusEmulator):
    def __init__(self, dev_name, reg_size):
        self._dev_name = dev_name
        self._reg_size = reg_size
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self.open()
