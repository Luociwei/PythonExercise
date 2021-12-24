# -*- coding: utf-8 -*-

from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG, MIXAd7177SG

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MIXDAQT1SGRDef:
    MIX_AD717X_IPCORE_ADDR = 0x2000
    MIX_SPI_IPCORE_ADDR = 0x4000
    MIX_GPIO_IPCORE_ADDR = 0x6000
    MIX_DAQT1_IPCORE_ID = 0x82
    MIX_DAQT1_IPCORE_MIN_VERSION = 0x10
    MIX_DAQT1_IPCORE_MAX_VERSION = 0x1F
    SPI_REG_SIZE = 8192
    GPIO_REG_SIZE = 256
    AD717X_REG_SIZE = 8192
    REG_SIZE = 65536


class MIXDAQT1SGRException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXDAQT1SGR(object):
    '''
    MIXDAQT1SGR Driver
        MIXDAQT1SGR aggregated IP includes MIXAD717x, MIXQSPI and MIXGPIO,
        MIXAD717x ipcore will be created, and change flags (use_spi, use_gpio)
        to decide which one to be created.

    ClassType = MIXDAQT1SGR

    Args:
        axi4_bus:        instance(AXI4LiteBus)/string/None, axi4lit bus or dev path.
        ad717x_chip:     string, ['AD7175', 'AD7177'], ADC chip type.
        ad717x_mvref:    int, default 5000, ADC reference voltage.
        use_spi:         boolean, spi use flag.
        use_gpio:        boolean, gpio use flag.

    Examples:
        daqt1 = MIXDAQT1SGR(axi4_bus='/dev/MIX_DAQT1_0', ad717x_chip='AD7175', ad717x_mvref=5000,
                        use_spi=True, use_gpio=False)

    '''

    def __init__(self, axi4_bus, ad717x_chip, ad717x_mvref=5000, code_polar="bipolar",
                 reference="extern", buffer_flag="enable", clock="crystal",
                 use_spi=False, use_gpio=False):
        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator('axi4_bus_emulator', MIXDAQT1SGRDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXDAQT1SGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.ad717x_chip = ad717x_chip
        self.ad717x_mvref = ad717x_mvref
        self.code_polar = code_polar
        self.reference = reference
        self.buffer_flag = buffer_flag
        self.clock = clock
        self.open(use_spi, use_gpio)

    def __del__(self):
        self.close()

    def open(self, use_spi, use_gpio):
        '''
        MIXDAQT1SGR open device

        Examples:
            daqt1.open()

        '''

        # AD717x will be created.
        self.ad717x_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXDAQT1SGRDef.MIX_AD717X_IPCORE_ADDR,
                                              MIXDAQT1SGRDef.AD717X_REG_SIZE)

        if self.ad717x_chip == "AD7175":
            self.ad717x = MIXAd7175SG(self.ad717x_axi4_bus, self.ad717x_mvref, self.code_polar, self.reference,
                                      self.buffer_flag, self.clock)
        elif self.ad717x_chip == "AD7177":
            self.ad717x = MIXAd7177SG(self.ad717x_axi4_bus, self.ad717x_mvref, self.code_polar, self.reference,
                                      self.buffer_flag, self.clock)
        else:
            raise MIXDAQT1SGRException("Unsupported AD717x chip type %s." % (self.ad717x_chip))

        # if use_gpio is True, MIXGPIOSG will be created.
        if use_gpio is True:
            self.gpio_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXDAQT1SGRDef.MIX_GPIO_IPCORE_ADDR,
                                                MIXDAQT1SGRDef.GPIO_REG_SIZE)
            self.gpio = MIXGPIOSG(self.gpio_axi4_bus)
        # if use_spi is True, MIXQSPISG will be created.
        if use_spi is True:
            self.spi_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXDAQT1SGRDef.MIX_SPI_IPCORE_ADDR,
                                               MIXDAQT1SGRDef.SPI_REG_SIZE)
            self.spi = MIXQSPISG(self.spi_axi4_bus)

    def close(self):
        '''
        MIXDAQT1SGR close device

        Examples:
            daqt1.close()

        '''

        self.ad717x.reset()
