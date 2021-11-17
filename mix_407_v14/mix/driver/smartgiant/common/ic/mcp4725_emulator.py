# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *


__author__ = 'Wenjun.Sun@SmartGiant'
__version__ = '0.1'


class MCP4725Exception(Exception):
    def __init__(self, dev_addr, err_str):
        self.err_reason = '[%s]: %s.' % (dev_addr, err_str)

    def __str__(self):
        return self.err_reason


class MCP4725Emulator(object):
    '''
    MCP4725 Emulator class

    '''

    def __init__(self, dev_addr, i2c_bus=None, mvref=3300.0):
        self.dev_addr = dev_addr
        self.i2c_bus = i2c_bus
        self.mvref = mvref
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def output_volt_dc(self, volt):
        '''
        MCP4725 output dc voltage function

        Args:
            volt: float, output voltage.

        Examples:
            mcp4725.output_volt_dc(1000)

        '''
        assert 0 <= volt <= self.mvref
        self._recorder.record("MCP4725 output dc voltage")

    def fast_output_volt_dc(self, volt):
        '''
        MCP4725 output dc voltage and will not wait ready for next output

        Args:
            volt: float, output voltage

        Examples:
            mcp4725.fast_output_volt_dc(1000)

        '''
        assert 0 <= volt <= self.mvref
        self._recorder.record("MCP4725 fast output dc voltage")
