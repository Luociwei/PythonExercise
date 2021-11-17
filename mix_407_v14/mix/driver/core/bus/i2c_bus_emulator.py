# -*- coding: utf-8 -*-
from ..tracer.recorder import *


class I2CBusException(Exception):
    pass


class I2CBusEmulator(object):
    def __init__(self, dev_name, reg_size):
        self._dev_name = dev_name
        self._reg_size = reg_size

        self._reg = dict()
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
            raise I2CBusException('%s load plugin failed' % (self._dev_name))

        plugin_lower_name = module_name.replace('_', '').lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self._plugin = getattr(plugin_module, item)()
                break

        if self._plugin is None:
            raise I2CBusException("%s can not find plugin %s" % (self._dev_name, plugin_lower_name))

    def open(self):
        self._recorder.record(str(self._dev_name) + " open")
        self._load_plugin()

    def close(self):
        self._recorder.record(str(self._dev_name) + " close")

    def read(self, addr, rd_len):
        assert addr >= 0

        self._recorder.record("read from 0x%02x with %d bytes" % (addr, rd_len))

        return self._plugin.read(addr, rd_len)

    def write(self, addr, wr_data):
        assert addr >= 0

        record_data = '['
        for i in range(len(wr_data)):
            record_data += "0x%02x" % wr_data[i]
            if i != len(wr_data) - 1:
                record_data += ', '
        record_data += ']'
        self._recorder.record("write " + record_data + " to 0x%02x" % addr)

        self._plugin.write(addr, wr_data)

    def write_and_read(self, addr, wr_data, rd_len):
        assert addr >= 0
        assert len(wr_data) > 0
        assert rd_len > 0

        record_data = '['
        for i in range(len(wr_data)):
            record_data += "0x%02x" % wr_data[i]
            if i != len(wr_data) - 1:
                record_data += ', '
        record_data += ']'
        self._recorder.record("write_and_read write " + record_data + " to 0x%02x, read %d bytes" % (addr, rd_len))

        return self._plugin.write_and_read(addr, wr_data, rd_len)


class PLI2CBusEmulator(I2CBusEmulator):
    '''
    SG PL I2C emulator
    '''
    pass


class I2CEmulator(I2CBusEmulator):
    '''
    PS/Xilinx PL I2C emulator
    '''
    def __init__(self, dev_name):
        self._dev_name = dev_name

        self._reg = dict()
        self._recorder = Recorder()
        add_recorder(self._recorder)

        self.open()
