# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG

__author__ = 'Kun.Yang@SmartGiant'
__version__ = '0.1'


class MIXBMUPWMSGRDef:
    MIX_GPIO_IPCORE_ADDR = 0x2000
    MIX_SS_IPCORE_ADDR = 0x4000
    MIX_DAQT1_IPCORE_VERSION = 0x00
    GPIO_REG_SIZE = 256
    SS_REG_SIZE = 8192
    REG_SIZE = 65536
    CHANNEL_SELECT_BIT0 = 0
    CHANNEL_SELECT_BIT1 = 1
    PWM_OUTPUT_LOW = 0
    PWM_OUTPUT_HIGH = 1


class MIXBMUPWMSGRException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXBMUPWMSGR(object):
    '''
    Mix BMU PWM function class

    ClassType = MIXBMUPWMSGR

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string, AXI4LiteBus class intance or device path.

    Examples:
        bmu_pwm = MIXBMUPWMSGR('/dev/MIX_SignalSource_SG')

    '''

    rpc_public_api = ['signal_output', 'open', 'close']

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXBMUPWMSGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        axi4_gpio = AXI4LiteSubBus(self.axi4_bus, MIXBMUPWMSGRDef.MIX_GPIO_IPCORE_ADDR, MIXBMUPWMSGRDef.GPIO_REG_SIZE)
        axi4_signalsource = AXI4LiteSubBus(self.axi4_bus, MIXBMUPWMSGRDef.MIX_SS_IPCORE_ADDR,
                                           MIXBMUPWMSGRDef.SS_REG_SIZE)

        self.gpio = MIXGPIOSG(axi4_gpio)
        self.signalsource = MIXSignalSourceSG(axi4_signalsource)
        self.gpio.set_pin_dir(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT0, 'output')
        self.gpio.set_pin_dir(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT1, 'output')

    def close(self):
        '''
        Disable mix BMU PWM function class

        Examples:
            bmu_pwm.close()

        '''
        self.signalsource.close()
        self.gpio.set_pin(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT0, 0)
        self.gpio.set_pin(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT1, 0)

    def open(self):
        '''
        Enable mix BMU PWM function class

        Examples:
            bmu_pwm.open()

        '''
        self.signalsource.open()
        self.gpio.set_pin(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT0, 0)
        self.gpio.set_pin(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT1, 0)

    def signal_output(self, signal_frequency, square_duty, signal_time=0xffffffff):
        '''
        Set mix BMU PWM parameters and output.

        Args:
            signal_frequency:   int, unit Hz,              output signal frequency.
            square_duty:        float, [0.001~0.999],      duty of square.
            signal_time:        int, unit us, signal time of signal source.

        Return:
            "done"

        '''
        assert 1 >= square_duty >= 0
        self.signal_time = signal_time
        self.signal_frequency = signal_frequency
        self.square_duty = square_duty

        if square_duty == MIXBMUPWMSGRDef.PWM_OUTPUT_LOW:
            self.gpio.set_pin(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT0, 0)
            self.gpio.set_pin(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT1, 0)
        elif square_duty == MIXBMUPWMSGRDef.PWM_OUTPUT_HIGH:
            self.gpio.set_pin(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT0, 0)
            self.gpio.set_pin(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT1, 1)
        else:
            self.gpio.set_pin(MIXBMUPWMSGRDef.CHANNEL_SELECT_BIT0, 1)
            self.signalsource.set_signal_type('square')
            self.signalsource.set_signal_time(self.signal_time)
            self.signalsource.set_swg_paramter(sample_rate=125000000, signal_frequency=self.signal_frequency,
                                               vpp_scale=0.5, square_duty=self.square_duty)
            self.signalsource.output_signal()
        return "done"
