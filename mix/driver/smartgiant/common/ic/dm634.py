# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.core.bus.axi4_lite_def import PLGPIODef

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class DM634Def:
    DATA_WIDTH = 4
    TXBUF_COUNT_REGISTER = 0x10
    TXBUF_REGISTER = 0x14
    MAX_CHAN_NUM = 16

    REG_SIZE = 256

    ch_wave_4bit_tab = [0x00, 0x03, 0x0C, 0x0F, 0x30, 0x33,
                        0x3C, 0x3F, 0xC0, 0xC3, 0xCC, 0xCF,
                        0xF0, 0xF3, 0xFC, 0xFF]


class DM634Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class DM634(object):
    '''
    DM634 function class

    ClassType = DAC

    Args:
        axi4_bus:     instance(AXI4LiteBus)/string/None,  AXI4LiteBus class intance or device name;
                                                          if None, will create emulator
        gpio_device:  instance(GPIO)/string/None,  MIXGPIOSG device to control data and clock output;
                                                   if None, will create emulator.
        gpio_id:      int, gpio pin id to control data and clock output.

    Examples:
        dm634 = DM634('/dev/MIX_DM634_CTRL', '/dev/MIX_DUT1_GPIO0', 0)

    '''
    def __init__(self, axi4_bus=None, gpio=None, gpio_id=0):
        if gpio is None:
            self.gpio = MIXGPIOSGEmulator('dm634_gpio_emulator', PLGPIODef.REG_SIZE)
        elif isinstance(gpio, basestring):
            # device path; create MIXGPIOSG instance here.
            self.gpio = MIXGPIOSG(gpio)
        else:
            self.gpio = gpio

        self.gpio_id = gpio_id

        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator('dm634_axi4_emulator', DM634Def.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            # device path; create axi4litebus instance here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, DM634Def.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.channel_value_list = [[i, 0] for i in range(0, DM634Def.MAX_CHAN_NUM)]

        self.set_mode('normal')

    def write(self, wr_data):
        '''
        DM634 internal function to write data

        Args:
            wr_data:   list,   data format [sck, dai, latch, 0x00].

        Examples:
            dm634.write([0x55, 0x01, 0x01, 0x00])

        '''
        assert len(wr_data) > 0
        assert len(wr_data) % 4 == 0

        sent = 0
        while sent < len(wr_data):
            tx_buf_count = self.axi4_bus.read_16bit_inc(DM634Def.TXBUF_COUNT_REGISTER, 1)[0]
            if len(wr_data) - sent > tx_buf_count * DM634Def.DATA_WIDTH:
                wr_len = tx_buf_count * DM634Def.DATA_WIDTH
            else:
                wr_len = len(wr_data) - sent

            send_data = [wr_data[i] | (wr_data[i + 1] << 8) | (wr_data[i + 2] << 16) | (wr_data[i + 3] << 24)
                         for i in range(sent, sent + wr_len, 4)]
            self.axi4_bus.write_32bit_fix(DM634Def.TXBUF_REGISTER, send_data)
            sent += wr_len

    def _shift_channel(self, ch_value):
        '''
        DM634 shift channel value to port

        Args:
            ch_value:    hexmial, [0~0xffff], channel output value.

        Examples:
            dm634._shift_channel(0x01)

        '''
        # ch_value is 16 bit data, send 4 bits every write cycle
        assert ch_value >= 0 and ch_value <= 0xFFFF
        for i in range(4):
            ch_4bit_index = (ch_value >> (12 - i * 4)) & 0x0F
            dai = DM634Def.ch_wave_4bit_tab[ch_4bit_index]
            self.write([0x55, dai, 0x00, 0x00])

    def get_mode(self):
        '''
        DM634 get mode function

        Examples:
            mode = dm634.get_mode()
            print(mode)

        '''
        return self._mode

    def set_mode(self, mode):
        '''
        DM634 set mode function

        Args:
            mode:   string, ['normal', 'gck'], normal mode use internal clock,
                                               gck mode use external clock.

        Examples:
            dm634.set_mode('normal')

        '''
        assert mode in ['normal', 'gck']
        self._mode = mode
        self.gpio.set_pin(self.gpio_id, 0)

        if mode == 'normal':
            # set DCK high and LAT low
            self.write([0xFF, 0x00, 0x00, 0x00])

            # give 4 LAT
            self.write([0xFF, 0x00, 0x55, 0x00])

            # set DCK and LAT high
            self.write([0xFF, 0x00, 0xFF, 0x00])

            # give 3 DCK
            self.write([0x2A, 0x00, 0xFF, 0x00])

            # set LAT high and DCK low
            self.write([0x00, 0x00, 0xFF, 0x00])

            # set LAT and DCK low
            self.write([0x00, 0x00, 0x00, 0x00])
        else:
            # set DCK high and LAT low
            self.write([0xFF, 0x00, 0x00, 0x00])

            # give 2 LAT and then set LAT high
            self.write([0xFF, 0x00, 0x57, 0x00])

            # LAT high and give 2 DCK then set DCK low
            self.write([0x0A, 0x00, 0xFF, 0x00])

            # set LAT high
            self.write([0x00, 0x00, 0xFF, 0x00])

            # set DCK and LAT low
            self.write([0x00, 0x00, 0x00, 0x00])

        self.gpio.set_pin(self.gpio_id, 1)

    def set_channels(self, ch_list):
        '''
        DM634 set channels output value

        Args:
            ch_list:   list,    channel value list to output,eg
                                [(chX, valueY),...], X in [0,...,15].

        Examples:
            set channel 0 value 0xfff and channel 1 value 0xffff
            dm634.set_channels([(0, 0xfff), (1, 0xffff)])

        '''
        assert isinstance(ch_list, list)
        assert len(ch_list) > 0 and len(ch_list) <= DM634Def.MAX_CHAN_NUM

        for ch in ch_list:
            if ch[0] < 0 or ch[0] >= DM634Def.MAX_CHAN_NUM:
                raise DM634Exception("Channel index %d not in [0-15]." % (ch[0]))
            self.channel_value_list[ch[0]][1] = ch[1]

        self.gpio.set_pin(self.gpio_id, 0)

        # write data to DAI
        for i in range(16):
            self._shift_channel(self.channel_value_list[15 - i][1])

        # latch data
        self.write([0x00, 0x00, 0x01, 0x00])

        self.write([0x00, 0x00, 0x00, 0x00])

        self.gpio.set_pin(self.gpio_id, 1)

    def set_all_channel_brightness(self, value):
        '''
        DM634 set all channel brightness

        Args:
            value:   int, [0~127], global brightness.

        Examples:
            dm634.set_all_channel_brightness(100)

        '''
        assert value >= 0 and value <= 127

        self.gpio.set_pin(self.gpio_id, 0)

        # set DCK high and LAT low
        self.write([0xFF, 0x00, 0x00, 0x00])

        # give 4 LAT when DCK is high
        self.write([0xFF, 0x00, 0x55, 0x00])

        # set LAT and DCK low
        self.write([0x00, 0x00, 0x00, 0x00])

        # write brightness data
        brightness = value << 1
        dai = DM634Def.ch_wave_4bit_tab[(brightness >> 4) & 0x0F]
        self.write([0x55, dai, 0x00, 0x00])
        dai = DM634Def.ch_wave_4bit_tab[(brightness & 0x0F)]
        self.write([0x55, dai, 0x00, 0x00])

        # latch data
        self.write([0x00, 0x00, 0x01, 0x00])

        self.write([0x00, 0x00, 0x00, 0x00])

        self.gpio.set_pin(self.gpio_id, 1)
