# -*- coding: utf-8 -*-

from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteSubBusEmulator
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator
from mix.driver.smartgiant.common.ipcore.mix_ad7177_sg_emulator import MIXAd7177SGEmulator

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
    EMULATOR_REG_SIZE = 256


class MIXDAQT1SGRException(Exception):
    def __init__(self, err_str):
        self._err_reason = "%s." % (err_str)

    def __str__(self):
        return self._err_reason


class MIXDAQT1SGREmulator(object):
    def __init__(self, axi4_bus, ad717x_chip, ad717x_mvref=5000, use_spi=False, use_gpio=False):

        self._dev_name = "MIXDAQT1SGR"
        self.ad717x_chip = ad717x_chip
        self.ad717x_mvref = ad717x_mvref

        self.axi4_bus = AXI4LiteBusEmulator("axi4_bus_emulator", 0x8000)

        self.ad717x_axi4_bus = AXI4LiteSubBusEmulator("axi4_bus_emulator", MIXDAQT1SGRDef.AD717X_REG_SIZE)
        if self.ad717x_chip is "AD7175":
            self.ad717x = MIXAd7175SGEmulator("mix_ad7175_sg_emulator", self.ad717x_mvref)
        elif self.ad717x_chip is "AD7177":
            self.ad717x = MIXAd7177SGEmulator("mix_ad7177_sg_emulator", self.ad717x_mvref)
        else:
            raise RuntimeError("Unsupported AD717x type %s." % (self.ad717x_chip))

        if use_gpio is True:
            self.gpio_axi4_bus = AXI4LiteSubBusEmulator("axi4_bus_emulator", MIXDAQT1SGRDef.GPIO_REG_SIZE)
            self.gpio = MIXGPIOSGEmulator("mix_gpio_sg_emulator", MIXDAQT1SGRDef.EMULATOR_REG_SIZE)

        if use_spi is True:
            self.spi_axi4_bus = AXI4LiteSubBusEmulator("axi4_bus_emulator", MIXDAQT1SGRDef.SPI_REG_SIZE)
            self.spi = MIXQSPISGEmulator("mix_qspi_sg_emulator", MIXDAQT1SGRDef.EMULATOR_REG_SIZE)

        self._recorder = Recorder()
        add_recorder(self._recorder)

        self.open()

    def __del__(self):
        self.close()
        del_recorder(self._recorder)

    def open(self):
        self._recorder.record("%s open" % (self._dev_name))

    def close(self):
        # ad717x reset
        self.ad717x.reset()
        self._recorder.record("%s close" % (self._dev_name))
