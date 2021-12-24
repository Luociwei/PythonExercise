# -*- coding: utf-8 -*-

__author__ = 'haite.zhuang@SmartGiant'
__version__ = '0.1'


class MIXTDMSGDef:
    SIGNAL_ALWAYS_OUTPUT = 0xffffffff
    VPP_SCALE_MAX = 0.999
    VPP_SCALE_MIN = 0.000
    SIGNAL_DUTY = 0.5
    SIGNAL_TYPE = 'sine'
    HIGH_LEVEL = 1
    LOW_LEVEL = 0
    INTERNAL_CLOCK = 0
    EXTERNAL_CLOCK = 1
    CHANNEL_MAX = 15
    CHANNEL_MIN = 0

    # These bits are only used for the emulator
    VIRTUAL_MODULE_EN_PIN = 0
    VIRTUAL_MUTE_EN_PIN = 1
    VIRTUAL_CLK_SEL_PIN = 2
    VIRTUAL_CHAN_SEL_BIT0_PIN = 3
    VIRTUAL_CHAN_SEL_BIT1_PIN = 4
    VIRTUAL_CHAN_SEL_BIT2_PIN = 5
    VIRTUAL_CHAN_SEL_BIT3_PIN = 6


class MIXTDMSG(object):
    '''
    The MIXTDMSG class provides a TDM(Time Division Multiplexing) master and slave interface

    which is a digital audio interface. The class provides mute enable function, TDM BCLK&WCLK source optional,
    output TDM signal function and measure audio data from TDM signal.

    Args:
        signal_source:       instance(MIXSignalSourceSG)/None, instance of MIXignalSourceSG, use to output signal.
        module_en:           instance(GPIO)/None,    instance of Pin/GPIO, use to enable or disable tdm module.
        mute_en:             instance(GPIO)/None,    instance of Pin/GPIO, use to enable or disable mute function.
        clk_sel:             instance(GPIO)/None,    instance of Pin/GPIO, use to select the clock source for tdm.
        chan_sel_bit0_pin:   instance(GPIO)/None,    instance of Pin/GPIO, the channel selection bit0.
        chan_sel_bit1_pin:   instance(GPIO)/None,    instance of Pin/GPIO, the channel selection bit1.
        chan_sel_bit2_pin:   instance(GPIO)/None,    instance of Pin/GPIO, the channel selection bit2.
        chan_sel_bit3_pin:   instance(GPIO)/None,    instance of Pin/GPIO, the channel selection bit3.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_SignalSource_SG', 256)
        signal_source = PLAXI4SignalSource(axi4_bus)
        axi4_bus = AXI4LiteBus('/dev/MIX_GPIO_0', 256)
        pl_gpio = PLGPIO(axi4_bus)
        module_en_pin = Pin(pl_gpio, 1)
        mute_en_pin = Pin(pl_gpio, 2)
        clk_sel_pin = Pin(pl_gpio, 3)
        chan_sel_bit0_pin = Pin(gpio, 2)
        chan_sel_bit1_pin = Pin(gpio, 3)
        chan_sel_bit2_pin = Pin(gpio, 4)
        chan_sel_bit3_pin = Pin(gpio, 5)
        tdm = MIXTDMSG(signal_source, module_en_pin, mute_en_pin, clk_sel_pin,
                    chan_sel_bit0_pin, chan_sel_bit1_pin, chan_sel_bit2_pin, chan_sel_bit3_pin)

    '''

    rpc_public_api = ['open', 'close', 'mute_enable', 'mute_disable',
                      'channel_select', 'clock_select', 'enable_output', 'disable_output',
                      'start_measure', 'get_thdn', 'get_frequency', 'get_vpp',
                      'get_thd']

    def __init__(self, signal_source=None, module_en_pin=None, clk_sel_pin=None, mute_en_pin=None,
                 chan_sel_bit0_pin=None, chan_sel_bit1_pin=None, chan_sel_bit2_pin=None, chan_sel_bit3_pin=None):
        self.signal_source = signal_source
        self.mute_en_pin = mute_en_pin
        self.module_en_pin = module_en_pin
        self.clk_sel_pin = clk_sel_pin
        self.chan_sel_bit0_pin = chan_sel_bit0_pin
        self.chan_sel_bit1_pin = chan_sel_bit1_pin
        self.chan_sel_bit2_pin = chan_sel_bit2_pin
        self.chan_sel_bit3_pin = chan_sel_bit3_pin

    def open(self):
        '''
        enable the tdm module.

        Returns:
            string, "done", api execution successful.

        Raises:
            AXI4LiteBusException:    when write axi4 bus error.

        Examples:
            tdm.open()

        '''
        self.module_en_pin.set_level(MIXTDMSGDef.HIGH_LEVEL)

        return "done"

    def close(self):
        '''
        disable the tdm module.

        Returns:
            string, "done", api execution successful.

        Raises:
            AXI4LiteBusException:    when write axi4 bus error.

        Examples:
            tdm.close()

        '''
        self.module_en_pin.set_level(MIXTDMSGDef.LOW_LEVEL)

        return "done"

    def mute_enable(self):
        '''
        enable the mute function for the tdm output

        Returns:
            string, "done", api execution successful.

        Raises:
            AXI4LiteBusException:    when write axi4 bus error.

        Examples:
            tdm.mute_enable()

        '''
        self.mute_en_pin.set_level(MIXTDMSGDef.HIGH_LEVEL)

        return "done"

    def mute_disable(self):
        '''
        disable the mute function for the tdm output

        Returns:
            string, "done", api execution successful.

        Raises:
            AXI4LiteBusException:    when write axi4 bus error.

        Examples:
            tdm.mute_disable()

        '''
        self.mute_en_pin.set_level(MIXTDMSGDef.LOW_LEVEL)

        return "done"

    def channel_select(self, channel):
        '''
        Select the tdm slot channel through set the gpio.

        tdm can support up to 16 slot channels, only one slot channel data can be reveice.

        Args:
            channel:   int, [0~15],   read the data from this channel.

        Returns:
            string, "done", api execution successful.

        Examples:
            tdm.channel_select(10)

        '''
        assert isinstance(channel, int)
        assert channel >= MIXTDMSGDef.CHANNEL_MIN
        assert channel <= MIXTDMSGDef.CHANNEL_MAX

        # The channel selection bits (bit0 to bit3) are used to nominate the channel.
        # For example, channel 10(0b1010) should be writen to bit3 to bit0.
        self.chan_sel_bit0_pin.set_level((channel >> 0) & 0x1)
        self.chan_sel_bit1_pin.set_level((channel >> 1) & 0x1)
        self.chan_sel_bit2_pin.set_level((channel >> 2) & 0x1)
        self.chan_sel_bit3_pin.set_level((channel >> 3) & 0x1)
        return "done"

    def clock_select(self, clock_source):
        '''
        Select the tdm BCLK & WCLK to use internal or external

        Args:
            clock_source:   int, [0, 1],   0 means internal, 1 means external.

        Returns:
            string, "done", api execution successful.

        Examples:
            tdm.clock_select(0)

        '''
        assert isinstance(clock_source, int)
        assert clock_source in [MIXTDMSGDef.INTERNAL_CLOCK, MIXTDMSGDef.EXTERNAL_CLOCK]

        self.clk_sel_pin.set_level(clock_source)
        return "done"

    def enable_output(self, vpp_scale, frequency, sample_rate):
        '''
        tdm open function to output signal.

        Args:
            vpp_scale:   float, [0.000~0.999],     vpp full scale ratio.
            frequency:   int,                      output signal frequency, unit is Hz.
            sample_rate: int,                      the tdm WCLK frequency, unit is SPS.

        Returns:
            string, "done", api execution successful.

        Examples:
            # vpp full scale ratio=0.9,frequency=1000Hz, sample_rate = 48000Hz
            tdm.enable_output(0.9, 1000, 48000)

        '''
        assert isinstance(vpp_scale, (float, int))
        assert vpp_scale >= MIXTDMSGDef.VPP_SCALE_MIN
        assert vpp_scale <= MIXTDMSGDef.VPP_SCALE_MAX
        assert isinstance(frequency, int)
        assert frequency > 0
        assert isinstance(sample_rate, int)
        assert sample_rate > 0

        self.signal_source.open()
        self.signal_source.set_signal_type(MIXTDMSGDef.SIGNAL_TYPE)
        self.signal_source.set_signal_time(MIXTDMSGDef.SIGNAL_ALWAYS_OUTPUT)
        self.signal_source.set_swg_paramter(sample_rate, frequency, vpp_scale, MIXTDMSGDef.SIGNAL_DUTY)
        self.signal_source.output_signal()

        return "done"

    def disable_output(self):
        '''
        tdm close signal output.

        Returns:
            string, "done", api execution successful.

        Raises:
            AXI4LiteBusException:    when write axi4 bus error.

        Examples:
            tdm.disable_output()

        '''
        self.signal_source.close()

        return "done"
