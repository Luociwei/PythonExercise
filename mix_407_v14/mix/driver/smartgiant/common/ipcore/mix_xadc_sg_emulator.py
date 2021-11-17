# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MIXXADCSGDef:
    BIPOLAR = 1
    UNIPOLAR = 0


class MIXXADCSGException(Exception):
    def __init__(self, err_str):
        self.err_reason = "MIXXADCSG {}".format(err_str)

    def __str__(self):
        return self.err_reason


class MIXXADCSGEmulator(object):
    def __init__(self, dev_name=None):
        if dev_name is None:
            self.xadc = "MIXXADCSGEmulator"
        else:
            self.xadc = dev_name

        self._recorder = Recorder()
        add_recorder(self._recorder)

    def config(self, sample_rate=100000, polar=MIXXADCSGDef.UNIPOLAR):
        '''
        config xadc sample rate and polar

        :param sample_rate:    int(1-1000000)                 Specific sampling rate to set.
        :param polar:          MIXXADCSGDef(BIPOLAR/UNIPOLAR)  Input polarity.
        :example
                    xadc.config(100000,MIXXADCSGDef.UNIPOLAR)
        '''
        assert sample_rate > 0
        assert sample_rate <= 1000000
        assert(polar == MIXXADCSGDef.UNIPOLAR) or (polar == MIXXADCSGDef.BIPOLAR)

        self._recorder.record(self.xadc + "." + "config(%d, %d)" % (sample_rate, polar))

    def set_multiplex_channel(self, multiplex=0):
        '''
        set multiplex channel

        :param multiplex: int(0-63|0xff)  multiplex channel number,if set 0xff,open all multiplex channels.
        :example
                xadc.set_multiplex_channel(0)

        '''
        assert(multiplex >= 0)
        assert(multiplex <= 63 or multiplex == 0xff)

        self._recorder.record(self.xadc + "." + "set_multiplex_channel(%d)" % (multiplex))

    def read_volt(self):
        '''
        get xadc VPVN channel voltage

        :returns  float        Voltage value has been read,unit is mV.
        :example
                volt = xadc.read_volt()

        '''
        self._recorder.record(self.xadc + "." + "read_volt()" % ())
        return 100

    def get_temperature(self):
        '''
        get xadc temperature

        :returns   float        temperature value has been read,unit is degree C.
        :example
                temp = xadc.get_temperature()
        '''
        self._recorder.record(self.xadc + "." + "get_temperature()" % ())
        return 100

    def enable_continuous_sampling(self, cycle_counts=64):
        '''
        xadc enable continuous sampling mode

        :param     cycle_counts:    int(1-64)        Number of cycles in a polling multiplex channel
        :example
                xadc.enable_continuous_sampling()

        '''
        assert(cycle_counts > 0)
        assert(cycle_counts <= 64)

        self._recorder.record(self.xadc + "." + "enable_continuous_sampling(%d)" % (cycle_counts))

    def disable_continuous_sampling(self):
        '''
        xadc disable continuous sampling mode

        :example
                xadc.disable_continuous_sampling()
        '''
        self._recorder.record(self.xadc + "." + "disable_continuous_sampling()")

    def get_continuous_sampling_voltage(self, count, multiplex=0):
        '''
        xadc get voltage at continuous mode

        :param count:           int(1-512)        Number of voltage to get.
        :param multiplex:       int(0-63)         Set specific multiplex channel.
        :example
                xadc.get_continuous_sampling_voltage(10)
        '''
        assert(count > 0)
        assert(count <= 512)
        assert(multiplex >= 0)
        assert(multiplex <= 63)

        self._recorder.record(self.xadc + "." + "get_continuous_sampling_voltage()")
        return [100, 110, 120]
