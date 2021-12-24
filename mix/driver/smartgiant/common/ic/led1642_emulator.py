# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.ic.led1642 import LED1642Def

__author__ = 'chenfeng@SmartGiant'
__version__ = '0.1'


class LED1642Emulator(object):
    '''
    LED1642 Emulator class
    '''

    def __init__(self, axi4_bus=None, gpio_pin=None):
        self._axi4_bus = axi4_bus
        self.gpio_pin = gpio_pin
        self._duty_code_list = LED1642Def.DUTY_CODE_LIST
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._init()

    def _init(self):
        self.current_range_code = LED1642Def.CURRENT_RANGE_0_CODE
        self.current_gain_percentage = LED1642Def.CURRENT_GAIN_PERCENTAGE_MIN
        self.grayscale_bits = LED1642Def.GRAYSCALE_12

    def set_grayscale(self, bits_wide):
        '''
        set grayscale bits wide to 12-bit or 16-bit

        Args:
            bits_wide:    int, [12, 16], grayscale bits wide.

        Examples:
            # set brightness to 12-bit
            led.set_grayscale(12)

        '''
        assert isinstance(bits_wide, int)
        assert bits_wide in [LED1642Def.GRAYSCALE_12, LED1642Def.GRAYSCALE_16]

        self.grayscale_bits = bits_wide

        self._recorder.record("LED1642 set_grayscale bits_wide:%s" % (self.grayscale_bits))

    def set_channels_duty(self, config_list):
        '''
        LED1642 set channels brightness by setting duty

        Args:
            config_list:  list, [(chn, duty),...], chn is channel number 0~15, duty range is [0 ~ 100].

        Examples:
            # set channel 0 with duty=80%, and channel 1 with duty=50%
            led.set_channels_duty([(0, 80),(1, 50)])

        '''
        assert isinstance(config_list, (list, dict))
        for chn in config_list:
            self._recorder.record("LED1642 set_channel_duty channel:%s, duty:%s" % (chn[0], chn[1]))

    def set_current_range(self, range):
        '''
        set current range to 0 or 1. if 0 current limit is 3.1 mA ~ 12.5 mA, or 8.9 mA ~ 20 mA

        Args:
            range:   int, [0, 1], current range.

        Examples:
            led.set_current_range(1)

        '''
        assert isinstance(range, int)
        assert range in [LED1642Def.CURRENT_RANGE_0, LED1642Def.CURRENT_RANGE_1]
        if (LED1642Def.CURRENT_RANGE_0 == range):
            self.current_range_code = LED1642Def.CURRENT_RANGE_0_CODE
        else:
            self.current_range_code = LED1642Def.CURRENT_RANGE_1_CODE

        self._recorder.record("LED1642 set_current_range ranger:%s" % (self.current_range_code))

    def set_current_gain(self, percentage):
        '''
        set current gain percentage

        Args:
            percentage:  float, [0~100.0], current gain percentage.

        Examples:
            led.set_current_gain(0.0)

        '''
        assert isinstance(percentage, (int, float))
        assert percentage >= 0
        assert percentage <= 100

        self.current_gain_percentage = percentage

        self._recorder.record("LED1642 set_current_gain gain:%s" % (self.current_gain_percentage))
