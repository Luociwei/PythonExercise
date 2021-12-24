# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


class MIXDAQT2SGRDef:
    GPIO_OFFSET_ADDR = 0x2000
    SIGNAL_METER0_OFFSET_ADDR = 0x4000
    SIGNAL_METER1_OFFSET_ADDR = 0x6000
    SPI_OFFSET_ADDR = 0x8000
    MIXDAQT2SGR_IPCORE_ID = 0x83
    MIXDAQT2SGR_IPCORE_MIN_VERSION = 0x10
    MIXDAQT2SGR_IPCORE_MAX_VERSION = 0x1F
    SIGNAL_METER_REG_SIZE = 8192
    SPI_REG_SIZE = 8192
    GPIO_REG_SIZE = 256
    REG_SIZE = 65536


class MIXDAQT2SGRException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class MIXDAQT2SGR(object):
    '''
    MIXDAQT2SGR Driver
         MIXDAQT2SGR aggregated IP includes SignalMeter 0, SignalMeter 1, GPIO and SPI.
         flags (use_signal_meter0, use_signal_meter1, use_spi, use_gpio)to decide which one to be created.

    ClassType = MIXDAQT2SGR

    Args:
        axi4_bus:           instance(AXI4LiteBus)/string/None, AXI4LiteBus class intance,
                                                               if not using, will create emulator.
        use_signal_meter1:  boolean,    signal meter 1 use flag.
        use_spi:            boolean,    spi use flag.
        use_gpio:           boolean,    gpio use flag.

    Examples:
        mixdaqt2 = MIXDAQT2SGR('/dev/MIX_DAQT2_SG_R', use_signal_meter1=True, use_spi=True, use_gpio=True)

    '''

    def __init__(self, axi4_bus=None, use_signal_meter1=True,
                 use_spi=True, use_gpio=True):

        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator('axi4_bus_emulator', MIXDAQT2SGRDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXDAQT2SGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.signal_meter0 = None
        self.signal_meter1 = None
        self.gpio = None
        self.spi = None
        self.open(use_signal_meter1, use_spi, use_gpio)

    def open(self, use_signal_meter1=True, use_spi=True, use_gpio=True):
        '''
        MIXDAQT2SGR open device

        Args:
            use_signal_meter1:  boolean, [True, False], default True, signal meter 1 use flag.
            use_spi:            boolean, [True, False], default True, spi use flag.
            use_gpio:           boolean, [True, False], default True, gpio use flag.

        Examples:
            mixdaqt2.open(use_signal_meter1=True, use_spi=True, use_gpio=True)

        '''

        # pl_signal_meter 0
        self.signal_meter0_axi4_bus = AXI4LiteSubBus(self.axi4_bus,
                                                     MIXDAQT2SGRDef.SIGNAL_METER0_OFFSET_ADDR,
                                                     MIXDAQT2SGRDef.SIGNAL_METER_REG_SIZE)
        self.signal_meter0 = MIXSignalMeterSG(self.signal_meter0_axi4_bus)

        # pl_signal_meter 1
        if use_signal_meter1 is True:
            self.signal_meter1_axi4_bus = AXI4LiteSubBus(self.axi4_bus,
                                                         MIXDAQT2SGRDef.SIGNAL_METER1_OFFSET_ADDR,
                                                         MIXDAQT2SGRDef.SIGNAL_METER_REG_SIZE)
            self.signal_meter1 = MIXSignalMeterSG(self.signal_meter1_axi4_bus)

        # gpio
        if use_gpio is True:
            self.gpio_axi4_bus = AXI4LiteSubBus(self.axi4_bus,
                                                MIXDAQT2SGRDef.GPIO_OFFSET_ADDR,
                                                MIXDAQT2SGRDef.GPIO_REG_SIZE)
            self.gpio = MIXGPIOSG(self.gpio_axi4_bus)

        # spi
        if use_spi is True:
            self.spi_axi4_bus = AXI4LiteSubBus(self.axi4_bus,
                                               MIXDAQT2SGRDef.SPI_OFFSET_ADDR,
                                               MIXDAQT2SGRDef.SPI_REG_SIZE)
            self.spi = MIXQSPISG(self.spi_axi4_bus)
