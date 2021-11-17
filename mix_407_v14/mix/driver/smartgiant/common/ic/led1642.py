# -*- coding: utf-8 -*-
import copy
from mix.driver.core.bus.axi4_lite_def import AXI4StreadmDef

__author__ = 'yongjiu@SmartGiant'
__version__ = '0.1'


class LED1642Def:
    DATA_WIDTH = 16
    DATA_MIN = 0
    DATA_MAX = 0xFFFF
    BIT_LOW = 0x00
    BIT_HIGH = 0xFF
    SCK_DATA = 0x0F

    CHAN_COUNT = 16
    CHAN_MIN_NUM = 0
    CHAN_MAX_NUM = 15

    WRITE_SWITCH_ENABLE = 0xFFFF
    PWM_COUNTER_ENABLE = 0x0001

    GRAYSCALE_12 = 12
    GRAYSCALE_16 = 16
    GRAYSCALE_12_CODE = 0x8000  # bit15 is 1
    GRAYSCALE_16_CODE = 0x0000  # bit15 is 0

    CURRENT_RANGE_0 = 0
    CURRENT_RANGE_1 = 1
    CURRENT_RANGE_0_CODE = 0x0000        # bit6 is 0
    CURRENT_RANGE_1_CODE = 0x0040        # bit6 is 1
    CURRENT_GAIN_MASK = 0x3F             # bit0 ~ bit5
    CURRENT_GAIN_PERCENTAGE_MIN = 0.0
    CURRENT_GAIN_PERCENTAGE_MAX = 100.0

    DUTY_MIN = 0.0
    DUTY_MAX = 100.0
    DUTY_CODE_LIST = [0x00] * CHAN_COUNT
    DUTY_12BIT_CODE_MASK = 0xFFF
    DUTY_16BIT_CODE_MASK = 0xFFFF

    LE_LOW = 0
    LE_HIGH = 1


class LATCHSDef:
    WRITE_SWITCH = 1
    BRIGHTNESS_DATA_LATCH = 3
    BRIGHTNESS_GLOBAL_LATCH = 5
    WRITE_CONFIG_REGISTER = 7
    READ_CONFIG_REGISTER = 8
    START_OPEN_ERROR_DETECT_MODE = 9
    START_SHORT_ERROR_DETECT_MODE = 10
    START_COMBINED_ERROR_DETECT_MODE = 11
    END_ERROR_DETECT_MODE = 12
    THERMAL_ERROR_READING = 13

    MIN_NUM = 1
    MAX_NUM = 13


class LED1642Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '[LED1642]: %s.' % (err_str)

    def __str__(self):
        return self._err_reason


class LED1642(object):
    '''
    LED1642 function class.

    ClassType = DAC

    Args:
        axi4_bus:    instance(AXI4LiteBus)/None,  AXI4LiteBus class instance,
                                                  if not using this parameter, will create emulator.
        gpio_pin:    instance(GPIO)/None, GPIO pin number, used to enable write data to bus.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_AxiLiteToStream_0', 256):
        gpio_pin = gpio_pin or GPIOEmulator("gpio_pin")
        led = LED1642(axi4_bus, gpio_pin)

    '''

    def __init__(self, axi4_bus=None, gpio_pin=None):
        self._axi4_bus = axi4_bus
        self._gpio_pin = gpio_pin
        self._gpio_pin.set_dir('output')
        self._duty_code_list = copy.copy(LED1642Def.DUTY_CODE_LIST)

        self._init()

    def _init(self):
        self._gpio_pin.set_level(LED1642Def.LE_LOW)
        self._write_and_latch(LATCHSDef.WRITE_SWITCH, LED1642Def.WRITE_SWITCH_ENABLE)
        self._gpio_pin.set_level(LED1642Def.LE_HIGH)

        self.current_range_code = LED1642Def.CURRENT_RANGE_0_CODE
        self.current_gain_percentage = LED1642Def.CURRENT_GAIN_PERCENTAGE_MIN
        self.grayscale_bits = LED1642Def.GRAYSCALE_12
        self._set_write_config_register()

        self.set_channels_duty([])

    def _write_bus(self, sck, sdi, latch):
        '''
        LED1642 write data to bus

        Args:
            sck:     hexmial, [0~0xFF], generate clock signal.
            sdi:     hexmial, [0~0xFF], generate data SDI signal.
            latch:   hexmial, [0~0xFF], generate latch signal.

        Examples:
            sck = 0x0F
            sdi = 0x00
            latch = 0xFF
            led._write_bus(sck, sdi, latch)

        '''
        assert isinstance(sck, int)
        assert isinstance(sdi, int)
        assert isinstance(latch, int)
        assert sck >= 0
        assert sck <= 0xFF
        assert sdi >= 0
        assert sdi <= 0xFF
        assert latch >= 0
        assert latch <= 0xFF

        tx_buf_count = self._axi4_bus.read_16bit_inc(AXI4StreadmDef.TXBUF_COUNT_REGISTER, 1)[0]
        if tx_buf_count == 0:
            raise LED1642Exception("TX buffer is empty")

        # 32 bits data format: sck in bit[0:7], sdi in bit[8:15], latch in bit[16:23] and bit[24:31] is dummy
        write_32bit_data = sck | (sdi << 8) | (latch << 16)
        self._axi4_bus.write_32bit_fix(AXI4StreadmDef.TXBUF_REGISTER, [write_32bit_data])

    def _write_and_latch(self, latchs, data):
        '''
        LED1642 write latch and data to bus

        Args:
            latchs:  int, [1~13], LED1642 latch count.
            data:    hexmial, [0~0xFFFF], 16bits data to be write.

        Examples:
            led._write_and_latch(4, 0x000a)

        '''
        assert isinstance(latchs, int)
        assert isinstance(data, int)
        assert latchs >= LATCHSDef.MIN_NUM
        assert latchs <= LATCHSDef.MAX_NUM
        assert data >= LED1642Def.DATA_MIN
        assert data <= LED1642Def.DATA_MAX

        # 16 bits latch data,  latchs is the count of 0xFF, other filled with 0x00
        latch_data_bit = [LED1642Def.BIT_LOW] * (LED1642Def.DATA_WIDTH - latchs) + [LED1642Def.BIT_HIGH] * latchs

        # 16 bits sdi data to bin list, as data 0x03 translate to [0,0,0...,0,1,1] then change 1 to 0xFF and 0 to 0x00
        sdi_data_bit = [LED1642Def.BIT_HIGH * int(i) for i in list(bin(data)[2:].zfill(LED1642Def.DATA_WIDTH))]

        for sdi, latch in zip(sdi_data_bit, latch_data_bit):
            self._write_bus(LED1642Def.SCK_DATA, sdi, latch)

    def _set_write_config_register(self):
        '''
        set latch of WRITE_CONFIG_REGISTER
        '''

        write_data = self.current_range_code

        if LED1642Def.GRAYSCALE_12 == self.grayscale_bits:
            write_data |= LED1642Def.GRAYSCALE_12_CODE
        else:
            write_data |= LED1642Def.GRAYSCALE_16_CODE

        # current gain data full scale is 0x3F, code value is percentage of full scale
        write_data |= int(self.current_gain_percentage /
                          LED1642Def.CURRENT_GAIN_PERCENTAGE_MAX * LED1642Def.CURRENT_GAIN_MASK)

        self._gpio_pin.set_level(LED1642Def.LE_LOW)
        self._write_and_latch(LATCHSDef.WRITE_CONFIG_REGISTER, write_data)
        self._gpio_pin.set_level(LED1642Def.LE_HIGH)

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

        self._set_write_config_register()

    def _config_channel_duty(self, channel, duty):
        assert isinstance(channel, int)
        assert isinstance(duty, (int, float))
        assert channel >= LED1642Def.CHAN_MIN_NUM
        assert channel <= LED1642Def.CHAN_MAX_NUM
        assert duty >= LED1642Def.DUTY_MIN
        assert duty <= LED1642Def.DUTY_MAX

        if self.grayscale_bits == LED1642Def.GRAYSCALE_12:
            full_scale = LED1642Def.DUTY_12BIT_CODE_MASK
        else:
            full_scale = LED1642Def.DUTY_16BIT_CODE_MASK

        # translate duty percentage to code with full scale
        self._duty_code_list[channel] = int(duty / LED1642Def.DUTY_MAX * full_scale)

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

        self._gpio_pin.set_level(LED1642Def.LE_LOW)

        for channel, duty in config_list:
            self._config_channel_duty(channel, duty)

        # the max channel duty code sent first, the min last
        for duty_code in self._duty_code_list[1::][::-1]:   # get channel 1~15 and reversal
            self._write_and_latch(LATCHSDef.BRIGHTNESS_DATA_LATCH, duty_code)
        self._write_and_latch(LATCHSDef.BRIGHTNESS_GLOBAL_LATCH, self._duty_code_list[LED1642Def.CHAN_MIN_NUM])

        self._gpio_pin.set_level(LED1642Def.LE_HIGH)

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

        self._set_write_config_register()

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

        self._set_write_config_register()
