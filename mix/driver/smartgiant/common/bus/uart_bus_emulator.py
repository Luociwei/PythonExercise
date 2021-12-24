# -*- coding: utf-8 -*-
"""
This is a class of the implemention of PL UART bus for Xavier emulator
"""
from mix.driver.core.tracer.recorder import *


class UARTBusException(Exception):
    pass


class UARTBusEmulator(object):
    def __init__(self, dev_name, reg_size):
        self._dev_name = dev_name
        self._reg_size = reg_size
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self.open()
        self._baudrate = 115200
        self._databits = 8
        self._stopbits = 1
        self._parity = 'none'

    def __del__(self):
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
            raise UARTBusException('%s load plugin failed' % (self._dev_name))

        plugin_lower_name = module_name.replace('_', '').lower()

        for item in dir(plugin_module):
            if item.lower() == plugin_lower_name:
                self._plugin = getattr(plugin_module, item)()
                break

        if self._plugin is None:
            raise UARTBusException("%s can not find plugin %s" % (self._dev_name, plugin_lower_name))

    def open(self):
        self._recorder.record(self._dev_name + " open")
        self._load_plugin()

    def close(self):
        self._recorder.record(self._dev_name + " close")

    def read(self, rd_len, timeout=0):
        self._recorder.record("read %d bytes" % rd_len)

        return self._plugin.read(rd_len, timeout)

    def write(self, wr_data):
        record_data = "["
        for i in range(len(wr_data)):
            record_data += "0x%02x" % (wr_data[i])
            if i != len(wr_data) - 1:
                record_data += ", "
        record_data += "]"
        self._recorder.record("write data " + record_data)

        self._plugin.write(wr_data)

    def get_baudrate(self):
        return self._baudrate

    def set_baudrate(self, baud_rate):
        self._baudrate = baud_rate

    def get_databits(self):
        return self._databits

    def set_databits(self, data_bits):
        self._databits = data_bits

    def get_parity(self):
        return self._parity

    def set_parity(self, parity):
        self._parity = parity

    def get_stopbits(self):
        return self._stopbits

    def set_stopbits(self, stop_bits):
        self._stopbits = stop_bits

    def get_flowctrl(self):
        return self._flowctrl

    def set_flowctrl(self, flow_ctrl_mode):
        self._flowctrl = flow_ctrl_mode


class PLUARTBus(UARTBusEmulator):
    pass


class PSUARTBus(UARTBusEmulator):
    def __init__(self, dev_name):
        self._dev_name = dev_name
