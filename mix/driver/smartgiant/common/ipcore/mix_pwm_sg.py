# -*- coding: utf-8 -*-

import ctypes


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXPWMSGDef:
    PULSE_ALWAYS_OUTPUT = 0
    REG_SIZE = 256


class MIXPWMSGException(Exception):

    def __init__(self, dev_name, err_code):
        reason = (128 * ctypes.c_char)()
        base_lib = ctypes.cdll.LoadLibrary('liblynx-core-driver.so')
        base_lib.get_error_reason(err_code, reason, len(reason))
        self._err_reason = '[%s]: %s.' % (
            dev_name, ctypes.string_at(reason, -1).decode("utf-8"))

    def __str__(self):
        return self._err_reason


class MIXPWMSG(object):
    '''
    MIXPWMSG function class.

    ClassType = PWM

    Args:
        dev_name:    string, Pwm device name.
        reg_size:    int, Fpga register memory size.

    Examples:
        pwm = MIXPWMSG('/dev/MIX_DUT1_PWM', 1024)

    '''
    def __init__(self, dev_name, reg_size=MIXPWMSGDef.REG_SIZE):
        self._dev_name = dev_name
        self._reg_size = reg_size
        self.base_lib = ctypes.cdll.LoadLibrary('libmix-pwm-sg-driver.so')
        self.open()

    def __del__(self):
        self.close()

    def open(self):
        '''
        MIXPWMSG open device, inti has called once

        Examples:
            pwm.open()

        '''
        self._axi4_bus = self.base_lib.pl_pwm_open(self._dev_name, self._reg_size)
        if self._axi4_bus == 0:
            raise RuntimeError('Open PWM device %s failure.' % (self._dev_name))

    def close(self):
        '''
        MIXPWMSG close device

        Examples:
            pwm.close()

        '''
        self.base_lib.pl_pwm_close(self._axi4_bus)

    def config(self, freq, duty, pulse=MIXPWMSGDef.PULSE_ALWAYS_OUTPUT):
        '''
        Config pwm output

        Args:
            freq:       float, pwm output frequency
            duty:       float, pwm output duty
            pulse:      int, default 0, pwm output pulse. If not given,
                             pwm will output always
        '''
        self.set_frequency(freq)
        self.set_duty(duty)
        self.set_pulse(pulse)

    def get_frequency(self):
        '''
        MIXPWMSG get frequency

        Returns:
            float, value, PWM frequency.

        Examples:
            freq = pwm.get_frequency()
            print(freq)

        '''
        freq = ctypes.c_float()
        result = self.base_lib.pl_pwm_get_frequency(self._axi4_bus, ctypes.byref(freq))
        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)
        return freq.value

    def set_frequency(self, freq):
        '''
        MIXPWMSG set frequency. `set_frequency` must be called before `set_duty`

        Args:
            freq:    float, Pwm frequency.

        Examples:
            pwm.set_frequency(freq)

        '''
        assert freq > 0
        c_freq = ctypes.c_float(freq)
        result = self.base_lib.pl_pwm_set_frequency(self._axi4_bus, c_freq)

        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)

    def get_duty(self):
        '''
        MIXPWMSG get duty cycle

        Returns:
            float, value, PWM duty cycle.

        Examples:
            duty = pwm.get_duty()
            print(duty)

        '''
        duty = ctypes.c_float()
        result = self.base_lib.pl_pwm_get_duty(self._axi4_bus, ctypes.byref(duty))
        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)
        return duty.value

    def set_duty(self, duty):
        '''
        MIXPWMSG set duty cycle. `set_duty` must be called after `set_frequency`

        Args:
            duty:    float, [0~100], Pwm duty cycle.

        Examples:
            pwm.set_duty(50)

        '''
        assert duty >= 0 and duty <= 100
        c_duty = ctypes.c_float(duty)
        result = self.base_lib.pl_pwm_set_duty(self._axi4_bus, c_duty)
        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)

    def get_pulse(self):
        '''
        MIXPWMSG get pulse number

        Returns:
            float, value, PWM pulse number.

        Examples:
            pulses = pwm.get_pulse()
            print(pulses)

        '''
        c_pulse = ctypes.c_int()
        result = self.base_lib.pl_pwm_get_pulse(self._axi4_bus, ctypes.byref(c_pulse))
        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)
        return c_pulse.value

    def set_pulse(self, pulses):
        '''
        MIXPWMSG set pulse number. `set_pulse` must be called after `set_frequency`

        Args:
            pulses:    int, Pwm pulse number.

        Examples:
            pwm.set_pulses(10)

        '''
        assert pulses >= 0

        c_pulse = ctypes.c_int(pulses)
        result = self.base_lib.pl_pwm_set_pulse(self._axi4_bus, c_pulse)
        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)

    def get_current_pulse(self):
        '''
        MIXPWMSG get current number of pulse which has been output

        Returns:
            int, value, current pulse has been output.

        Examples:
            pwm.get_current_pulse()

        '''
        c_pulse = ctypes.c_ulonglong()
        result = self.base_lib.pl_pwm_get_current_pulse(self._axi4_bus, ctypes.byref(c_pulse))
        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)
        return c_pulse.value

    def clear_pulse(self):
        '''
        MIXPWMSG clear pulse counter

        Examples:
            pwm.get_current_pulse()

        '''
        result = self.base_lib.pl_pwm_clear_pulse(self._axi4_bus)
        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)

    def get_enable(self):
        '''
        MIXPWMSG get output state

        Returns:
            boolean, [True, False], True for enable output, False for disable output.

        Examples:
            state = pwm.get_enable()
            print(state)

        '''
        state = ctypes.c_int()
        result = self.base_lib.pl_pwm_get_state(self._axi4_bus, ctypes.byref(state))
        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)

        if state.value == 1:
            return True
        else:
            return False

    def set_enable(self, state):
        '''
        MIXPWMSG set output state

        Args:
            state:  boolean, [True, False], True for enable output, False for disable output.

        Examples:
            pwm.set_enable(True)

        '''
        assert state in [True, False]

        if state is True:
            result = self.base_lib.pl_pwm_start(self._axi4_bus)
        else:
            result = self.base_lib.pl_pwm_stop(self._axi4_bus)

        if result != 0:
            raise MIXPWMSGException(self._dev_name, result)
