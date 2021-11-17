# -*- coding: utf-8 -*-
import ctypes
from mix.driver.core.tracer.recorder import *

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXPWMSGLib(object):
    def __init__(self):
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def pl_pwm_open(self, dev_name, reg_size):
        self._recorder.record('mix_pwm_sg_emulator open')
        return 1

    def pl_pwm_close(self, axi4_bus):
        self._recorder.record('mix_pwm_sg_emulator close')
        return 0

    def pl_pwm_set_frequency(self, axi4_bus, freq):
        self._recorder.record('set frequency')
        self.freq = freq.value
        return 0

    def pl_pwm_get_frequency(self, axi4_bus, freq):
        self._recorder.record('get frequency')
        f = ctypes.cast(freq, ctypes.POINTER(ctypes.c_float))
        f.contents.value = self.freq
        return 0

    def pl_pwm_set_duty(self, axi4_bus, duty):
        self._recorder.record('set duty')
        self.duty = duty.value
        return 0

    def pl_pwm_get_duty(self, axi4_bus, duty):
        self._recorder.record('get duty')
        d = ctypes.cast(duty, ctypes.POINTER(ctypes.c_float))
        d.contents.value = self.duty
        return 0

    def pl_pwm_set_pulse(self, axi4_bus, pulse):
        self.pulse = pulse.value
        self._recorder.record('set pulse')
        return 0

    def pl_pwm_get_pulse(self, axi4_bus, pulse):
        self._recorder.record('get pulse')
        p = ctypes.cast(pulse, ctypes.POINTER(ctypes.c_int))
        p.contents.value = self.pulse
        return 0

    def pl_pwm_get_current_pulse(self, axi4_bus, pulse):
        self._recorder.record('get current pulse')
        p = ctypes.cast(pulse, ctypes.POINTER(ctypes.c_int))
        p.contents.value = self.pulse
        return 0

    def pl_pwm_clear_pulse(self, axi4_bus):
        self._recorder.record('clear pulse')
        self.pulse = 0
        return 0

    def pl_pwm_get_state(self, axi4_bus, state):
        self._recorder.record('get state')
        s = ctypes.cast(state, ctypes.POINTER(ctypes.c_int))
        s.contents.value = self._is_enabled
        return 0

    def pl_pwm_start(self, axi4_bus):
        self._recorder.record('start')
        self._is_enabled = 1
        return 0

    def pl_pwm_stop(self, axi4_bus):
        self._recorder.record('stop')
        self._is_enabled = 0
        return 0
