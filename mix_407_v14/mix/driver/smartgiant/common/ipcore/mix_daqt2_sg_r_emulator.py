# -*- coding: utf-8 -*-

from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteSubBusEmulator
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg_emulator import MIXSignalMeterSGEmulator


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
    EMULATOR_REG_SIZE = 256
    GPIO_REG_SIZE = 256


class MIXDAQT2SGRException(Exception):
    def __init__(self, err_str):
        self._err_reason = "%s." % (err_str)

    def __str__(self):
        return self._err_reason


class MIXDAQT2SGREmulator(object):
    def __init__(self, axi4_bus=None, use_signal_meter0=True, use_signal_meter1=True,
                 use_spi=True, use_gpio=True):

        self._dev_name = "MIXDAQT2SGR"
        self.axi4_bus = AXI4LiteBusEmulator("axi4_bus_emulator", 0x8000)

        # pl_signal_meter 0
        if use_signal_meter0 is True:
            self.signal_meter0_axi4_bus = AXI4LiteSubBusEmulator("axi4_bus_emulator",
                                                                 MIXDAQT2SGRDef.SIGNAL_METER_REG_SIZE)
            self.signal_meter0 = MIXSignalMeterSGEmulator(
                "mix_signalmeter_sg_emulator", MIXDAQT2SGRDef.EMULATOR_REG_SIZE)
        # pl_signal_meter 1
        if use_signal_meter1 is True:
            self.signal_meter1_axi4_bus = AXI4LiteSubBusEmulator("axi4_bus_emulator",
                                                                 MIXDAQT2SGRDef.SIGNAL_METER_REG_SIZE)
            self.signal_meter1 = MIXSignalMeterSGEmulator(
                "mix_signalmeter_sg_emulator", MIXDAQT2SGRDef.EMULATOR_REG_SIZE)
        # gpio
        if use_gpio is True:
            self.gpio_axi4_bus = AXI4LiteSubBusEmulator("axi4_bus_emulator", MIXDAQT2SGRDef.GPIO_REG_SIZE)
            self.gpio = MIXGPIOSGEmulator("mix_gpio_sg_emulator", MIXDAQT2SGRDef.EMULATOR_REG_SIZE)
        # spi
        if use_spi is True:
            self.spi_axi4_bus = AXI4LiteSubBusEmulator("axi4_bus_emulator", MIXDAQT2SGRDef.SPI_REG_SIZE)
            self.spi = MIXQSPISGEmulator("mix_qspi_sg_emulator", MIXDAQT2SGRDef.EMULATOR_REG_SIZE)

        self._recorder = Recorder()
        add_recorder(self._recorder)

        self.open(use_signal_meter0, use_signal_meter1, use_spi, use_gpio)

    def __del__(self):
        del_recorder(self._recorder)

    def open(self, use_signal_meter0=True, use_signal_meter1=True, use_spi=True, use_gpio=True):
        self._recorder.record("%s open" % (self._dev_name))
