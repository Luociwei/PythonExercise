# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class MIXSGT1SGRDef:
    MIX_GPIO_ADDR = 0x2000
    MIX_SIGNAL_SOURCE_ADDR = 0x4000

    MIX_GPIO_REG_SIZE = 256
    MIX_SIGNAL_SOURCE_REG_SIZE = 256
    REG_SIZE = 65536


class MIXSGT1SGR(object):
    '''
    MIXSGT1SGR wrapper IP which include signal source and gpio function.

    ClassType = MIXSGT1SGR

    Args:
        axi4_bus:        instance/string/None, which is used to access MIXSGT1SGR IP register.
        use_gpio:        boolean, [True, False], if True, enable MIXGPIO sub IP, otherwise disable
                                                 MIXGPIO sub IP.

    Examples:
        sgt1 = MIXSGT1SGR('/dev/MIX_SGT1', use_gpio=True)

    '''
    def __init__(self, axi4_bus, use_gpio=True):
        if not axi4_bus:
            self.signal_source = MIXSignalSourceSGEmulator('mix_signal_source_sg_emulator')
            self.gpio = MIXGPIOSGEmulator('mix_gpio_sg_emulator', MIXSGT1SGRDef.MIX_GPIO_REG_SIZE)
        else:
            if isinstance(axi4_bus, basestring):
                axi4_bus = AXI4LiteBus(axi4_bus, MIXSGT1SGRDef.REG_SIZE)
            if use_gpio is True:
                axi4_sub_bus = AXI4LiteSubBus(axi4_bus, MIXSGT1SGRDef.MIX_GPIO_ADDR, MIXSGT1SGRDef.MIX_GPIO_REG_SIZE)
                self.gpio = MIXGPIOSG(axi4_sub_bus)
            axi4_sub_bus = AXI4LiteSubBus(axi4_bus, MIXSGT1SGRDef.MIX_SIGNAL_SOURCE_ADDR,
                                          MIXSGT1SGRDef.MIX_SIGNAL_SOURCE_REG_SIZE)
            self.signal_source = MIXSignalSourceSG(axi4_sub_bus)
