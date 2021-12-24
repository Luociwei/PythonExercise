# -*- coding: utf-8 -*-

from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.ipcore.mix_pwm_sg import MIXPWMSGDef

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXPWMSG(object):
    def __init__(self, dev_name, reg_size):
        self._dev_name = dev_name
        self._reg_size = reg_size
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._freq = 0
        self._duty = 0
        self._is_enabled = False
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        self._recorder.record("%s open" % (self._dev_name))

    def close(self):
        self._recorder.record("%s close" % (self._dev_name))

    def config(self, freq, duty, pulse=MIXPWMSGDef.PULSE_ALWAYS_OUTPUT):
        self._recorder.record("%s config pwm" % (self._dev_name))

    def get_frequency(self):
        self._recorder.record("get frequency")
        return self._freq

    def set_frequency(self, freq):
        assert freq > 0
        self._recorder.record("set frequency {:f}".format(freq))
        self._freq = freq

    def get_duty(self):
        self._recorder.record("get duty")
        return self._duty

    def set_duty(self, duty):
        assert duty >= 0 and duty <= 100
        self._recorder.record("set duty {:f}".format(duty))
        self._duty = duty

    def get_pulse(self):
        self._recorder.record("get pulse")
        return self._pulse

    def set_pulse(self, pulse):
        self._recorder.record("set pulse {}".format(pulse))
        self._pulse = pulse

    def get_current_pulse(self):
        self._recorder.record("get current pulse")
        return self._pulse

    def clear_pulse(self):
        self._recorder.record("clear pulse")

    def get_enable(self):
        self._recorder.record("get enable")
        return self._is_enabled

    def set_enable(self, state):
        assert state in [True, False]
        self._recorder.record("set enable state {}".format(state))
        self._is_enabled = state
