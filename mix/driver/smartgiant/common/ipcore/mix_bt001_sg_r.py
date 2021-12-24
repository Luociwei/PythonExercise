# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG, MIXAd7177SG


__author__ = 'tufeng.mao@SmartGiant'
__version__ = 'V0.0.1'


class MIXBT001SGRDef:
    MIX_AD717X_IPCORE_ADDR = 0x2000
    MIX_SPI_IPCORE_ADDR = 0x4000
    MIX_GPIO_IPCORE_ADDR = 0x6000
    SPI_REG_SIZE = 8192
    GPIO_REG_SIZE = 256
    AD717X_REG_SIZE = 8192
    REG_SIZE = 65536


class MIXBT001SGRException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXBT001SGR(object):
    '''
    MIXBT001SGR Driver
        MIXBT001SGR aggregated IP includes MIXAD717x, MIXQSPI and MIXGPIO,
        MIXAD717x ipcore will be created, and change flags (use_spi, use_gpio)
        to decide which one to be created.

    ClassType = MIXBT001SGR

    Args:
        axi4_bus:        instance(AXI4LiteBus)/string/None, axi4lite bus or dev path.
        ad717x_chip:     string, ['AD7175', 'AD7177'], ADC chip type.
        ad717x_mvref:    int, default 5000, ADC reference voltage.
        use_spi:         boolean, spi use flag.
        use_gpio:        boolean, gpio use flag.

    Examples:
        bt001 = MIXBT001SGR(axi4_bus='/dev/MIX_BT001_SG_R_0', ad717x_chip='AD7175', ad717x_mvref=5000,
                            use_spi=True, use_gpio=True)

    '''

    def __init__(self, axi4_bus, ad717x_chip, ad717x_mvref=5000, code_polar="bipolar",
                 reference="extern", buffer_flag="enable", clock="crystal",
                 use_spi=True, use_gpio=True):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXBT001SGRDef.REG_SIZE)
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
        MIXBT001SGR open device

        Examples:
            bt001.open()

        '''

        # AD717x will be created.
        self.ad717x_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXBT001SGRDef.MIX_AD717X_IPCORE_ADDR,
                                              MIXBT001SGRDef.AD717X_REG_SIZE)

        if self.ad717x_chip == "AD7175":
            self.ad717x = MIXAd7175SG(self.ad717x_axi4_bus, self.ad717x_mvref, self.code_polar, self.reference,
                                      self.buffer_flag, self.clock)
        elif self.ad717x_chip == "AD7177":
            self.ad717x = MIXAd7177SG(self.ad717x_axi4_bus, self.ad717x_mvref, self.code_polar, self.reference,
                                      self.buffer_flag, self.clock)
        else:
            raise MIXBT001SGRException("Unsupported AD717x chip type %s." % (self.ad717x_chip))

        # if use_gpio is True, MIXGPIOSG will be created.
        if use_gpio is True:
            self.gpio_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXBT001SGRDef.MIX_GPIO_IPCORE_ADDR,
                                                MIXBT001SGRDef.GPIO_REG_SIZE)
            self.gpio = MIXGPIOSG(self.gpio_axi4_bus)
        # if use_spi is True, MIXQSPISG will be created.
        if use_spi is True:
            self.spi_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXBT001SGRDef.MIX_SPI_IPCORE_ADDR,
                                               MIXBT001SGRDef.SPI_REG_SIZE)
            self.spi = MIXQSPISG(self.spi_axi4_bus)

    def close(self):
        '''
        MIXBT001SGR close device

        Examples:
            bt001.close()

        '''

        self.ad717x.reset()