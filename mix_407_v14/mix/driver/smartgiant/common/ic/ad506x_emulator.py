# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *


__author__ = 'tufeng.Mao@SmartGiant'
__version__ = '0.1'


class AD506xDef:
    MODE_NORMAL = 0x00
    MODE_TRI_STATE = 0x01
    MODE_R_100K = 0x10
    MODE_R_1K = 0x11

    AD5061_RESOLUTION = 16
    ALWAYS_OUTPUT = 0xFFFFFF

    AWG_VALUE = 0.99999
    SINE_VALUE_K = 0.999
    SINE_VALUE_B = 0.0
    SINE_OFFSET = 0.9999


class AD506xException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class AD506xEmulator(object):
    '''
    AD506x Emulator class

    '''

    def __init__(self, dev_name='ad506x', dac_volt_min=0, dac_volt_max=2048):
        self.dev_name = dev_name
        self.dac_volt_min = dac_volt_min
        self.dac_volt_max = dac_volt_max
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def disable_output(self):
        '''
        Disable the current waveform output function, not disable the chip

        Examples:
            ad506x.disable_output()

        '''
        self._recorder.record("%s disable the current waveform output function" % (self.dev_name))

    def sine(self, vpp, offset, frequency,
             output_time=AD506xDef.ALWAYS_OUTPUT):
        '''
        Output sine wave

        Args:
            vpp:          float, [0~2048], unit mV, vpp voltage to config sine wave.
            offset:       float, offset to config sine wave.
            frequency:    float, frequency to config sine wave.
            output_time:  int, unit us, default 0xFFFFFF, output time of pulse wave.

        Examples:
            ad506x.sine(2000, 1, 1000, 10000)

        '''
        assert self.dac_volt_min <= vpp <= self.dac_volt_max

        self._recorder.record("%s output sine wave" % (self.dev_name))

    def output_volt_dc(self, channel, volt):
        '''
        Output dc_voltage wave

        Args:
            channel:   int, [0], channel must be 0.
            volt:      float, voltage reference to config dc_voltage wave.

        Examples:
            ad506x.output_volt_dc(0, 2000)

        '''
        assert channel == 0
        self._recorder.record("%s output dc voltage" % (self.dev_name))

    def triangle(self, v1, v2, triangle_width, period,
                 output_time=AD506xDef.ALWAYS_OUTPUT):
        '''
        Output triangle wave

        Args:
            v1:             float, Max voltage or min voltage, if v1>v2, the wave starts at v1 to v2.
            v2:             float, Max voltage or min voltage, if v2>v1, the wave starts at v2 to v1.
            triangle_width: float, Triangle_width to triangle wave.
            period:         float, Triangle_width to triangle wave.
            output_time:    int, unit us, default 0xFFFFFF, output time of pulse wave.

        Examples:
                   ad506x.triangle(1000, 2000, 100, 100, 10000)

        '''

        self._recorder.record("%s output triangle wave" % (self.dev_name))

    def pulse(self, v1, v2, edge_width, pulse_width, period,
              output_time=AD506xDef.ALWAYS_OUTPUT):
        '''
        Output pulse wave

        Args:
            v1:             float, Max voltage or min voltage, if v1>v2, the wave starts at v1 to v2.
            v2:             float, Max voltage or min voltage, if v2>v1, the wave starts at v2 to v1.
            edge_width:     float, Edge width of pulse wave.
            pulse_width:    float, Pulse width of pulse wave.
            period:         float, Period of pulse wave.
            output_time:    int, unit us, default 0xFFFFFF, output time of pulse wave.

        Examples:
                   ad506x.pulse(1000, 2000, 1, 10, 100, 10000)

        '''

        self._recorder.record("%s output pulse wave" % (self.dev_name))


class AD5061Emulator(AD506xEmulator):
    '''
    AD5061 Emulator class

    '''

    def __init__(self, dev_name, dac_volt_min=0, dac_volt_max=2048):
        self.dev_name = dev_name
        super(AD5061Emulator, self).__init__(self.dev_name, dac_volt_min, dac_volt_max)
