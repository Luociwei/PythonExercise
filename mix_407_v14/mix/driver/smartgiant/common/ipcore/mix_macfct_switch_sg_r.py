# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG

__author__ = 'shunreng.he@SmartGiant'
__version__ = '0.1'


class MIXMacFCTSwitchSGRDef:
    MIX_GPIO_IPCORE_ADDR = 0x2000
    MIX_SIGNALSOURCE_IPCORE_ADDR = 0x4000
    MIX_SIGNALMETER_IPCORE_ADDR = 0x6000

    MIX_SIGNALMETER_REG_SIZE = 256
    MIX_SIGNALSOURCE_REG_SIZE = 256
    MIX_GPIO_REG_SIZE = 256

    REG_SIZE = 0x8000


class MIXMacFCTSwitchSGR(object):
    '''
    MIXSWITCH aggregated IPcore has 3 child IP, MIXSignalMeterSG, MIXSignalSourceSG, MIXGPIOSG.

    GPIO control as follow:
        gpio bit1 = 1, Output pwm, enable frequency measure
        gpio bit1 = 0, Output pdm
        gpio bit8 = 1, PDM failing edge sample data
        gpio bit8 = 0, PDM rising edge sample data

    ClassType = MIXMacFCTSwitchSGR

    Args:
        axi4_bus:            instance(AXI4LiteBus)/None,  which is used to access IP register.
        use_signal_source:   boolean, signal source use flag.
        use_signal_meter:    boolean, signal meter use flag.
        use_gpio:            boolean, gpio use flag.

    Examples:
        axi4 = AXI4LiteBus('/dev/MIX_MacFCT_Switch_SG_R_0', 0x8000)
        # enable signal source, signal meter and gpio sub IP in MIXMacFCTSwitchSGR
        macfct_switch = MIXMacFCTSwitchSGR(axi4, use_signal_source=True, use_freq_measure=True, use_gpio=True)

    '''

    def __init__(self, axi4_bus, use_signal_source=True, use_signal_meter=True, use_gpio=True):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            axi4_bus = AXI4LiteBus(axi4_bus, MIXMacFCTSwitchSGRDef.REG_SIZE)
        else:
            axi4_bus = axi4_bus

        if use_gpio:
            self._gpio_axi4_bus = AXI4LiteSubBus(axi4_bus, MIXMacFCTSwitchSGRDef.MIX_GPIO_IPCORE_ADDR,
                                                 MIXMacFCTSwitchSGRDef.MIX_GPIO_REG_SIZE)
            self.gpio = MIXGPIOSG(self._gpio_axi4_bus)
        if use_signal_source:
            self._signal_source_axi4_bus = AXI4LiteSubBus(axi4_bus,
                                                          MIXMacFCTSwitchSGRDef.MIX_SIGNALSOURCE_IPCORE_ADDR,
                                                          MIXMacFCTSwitchSGRDef.MIX_SIGNALSOURCE_REG_SIZE)
            self.signal_source = MIXSignalSourceSG(self._signal_source_axi4_bus)
        if use_signal_meter:
            self._signal_meter_axi4_bus = AXI4LiteSubBus(axi4_bus,
                                                         MIXMacFCTSwitchSGRDef.MIX_SIGNALMETER_IPCORE_ADDR,
                                                         MIXMacFCTSwitchSGRDef.MIX_SIGNALMETER_REG_SIZE)
            self.signal_meter = MIXSignalMeterSG(self._signal_meter_axi4_bus)
