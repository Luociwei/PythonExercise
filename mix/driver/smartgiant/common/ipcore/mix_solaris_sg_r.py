# -*- coding: utf-8 -*-

from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus

from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.pl_spi_dac import PLSPIDAC
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.pl_spi_adc import PLSPIADC

from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator
from mix.driver.smartgiant.common.ipcore.pl_spi_dac_emulator import PLSPIDACEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg_emulator import MIXSignalMeterSGEmulator
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg_emulator import MIXFftAnalyzerSGEmulator
from mix.driver.smartgiant.common.ipcore.pl_spi_adc_emulator import PLSPIADCEmulator
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg_emulator import MIXGPIOSGEmulator


__author__ = 'Jiasheng.Xie@SmartGiant'
__version__ = '0.1'


class MIXSolarisSGRDef:
    MIX_SPIADC_ADDR = 0x2000
    MIX_SIGNALMETER_ADDR = 0x4000
    MIX_FFTANALYZER_ADDR = 0x6000
    MIX_SPIMASTER_ADDR = 0x8000
    MIX_SIGNALSOURCE_ADDR = 0xA000
    MIX_GPIO_ADDR = 0xC000
    MIX_SPIDAC_ADDR = 0xE000

    SPIADC_REG_SIZE = 8192
    SIGNALMETER_REG_SIZE = 8192
    FFTANALYZER_REG_SIZE = 8192
    SPIMASTER_REG_SIZE = 8192
    SIGNALSOURCE_REG_SIZE = 8192
    GPIO_REG_SIZE = 8192
    SPIDAC_REG_SIZE = 8192
    # wrapper ipcore regsize
    REG_SIZE = 65536


class MIXSolarisSGRException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXSolarisSGR(object):
    '''
    MIXSolarisSGR Driver

    MIXSolarisSGR aggregated IP includes MIX_SignalMeter_SG,MIXGPIOSG,
    MIX_SignalSource_SG,MIX_FftAnalyzer_SG,PLSPIADC,PLSPIDAC,MIX_QSPI_SG.

    ClassType = MIXSolarisSGR

    Args:
        axi4_bus:        instance(AXI4LiteBus), axi4_lite_bus instance.

    Examples:
        ip = MIXSolarisSGR('/dev/MIX_XXXX')

    '''

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXSolarisSGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        if self.axi4_bus is not None:
            self.open()
        else:
            self.meter = MIXSignalMeterSGEmulator("mix_signalmeter_sg_emulator")
            self.spi_adc = PLSPIADCEmulator("pl_spi_adc_emulator", 256)
            self.audio = MIXFftAnalyzerSGEmulator("mix_fftanalyzer_sg_emulator")
            self.spi_bus = MIXQSPISGEmulator("mix_qspi_sg_emulator", 256)
            self.source = MIXSignalSourceSGEmulator("mix_signalsource_sg_emulator")
            self.gpio = MIXGPIOSGEmulator('mix_gpio_sg_emulator', 256)
            self.spi_dac = PLSPIDACEmulator("pl_spi_dac_emulator")

    def open(self):
        '''
        MIXSolarisSGR open device

        Examples:
            ip.open()

        '''

        self.meter_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXSolarisSGRDef.MIX_SIGNALMETER_ADDR,
                                             MIXSolarisSGRDef.SIGNALMETER_REG_SIZE)
        self.meter = MIXSignalMeterSG(self.meter_axi4_bus)

        self.spi_adc_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXSolarisSGRDef.MIX_SPIADC_ADDR,
                                               MIXSolarisSGRDef.SPIADC_REG_SIZE)
        self.spi_adc = PLSPIADC(self.spi_adc_axi4_bus)

        self.audio_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXSolarisSGRDef.MIX_FFTANALYZER_ADDR,
                                             MIXSolarisSGRDef.FFTANALYZER_REG_SIZE)
        self.audio = MIXFftAnalyzerSG(self.audio_axi4_bus)

        self.spi_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXSolarisSGRDef.MIX_SPIMASTER_ADDR,
                                           MIXSolarisSGRDef.SPIMASTER_REG_SIZE)
        self.spi_bus = MIXQSPISG(self.spi_axi4_bus)

        self.source_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXSolarisSGRDef.MIX_SIGNALSOURCE_ADDR,
                                              MIXSolarisSGRDef.SIGNALSOURCE_REG_SIZE)
        self.source = MIXSignalSourceSG(self.source_axi4_bus)

        self.gpio_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXSolarisSGRDef.MIX_GPIO_ADDR,
                                            MIXSolarisSGRDef.GPIO_REG_SIZE)
        self.gpio = MIXGPIOSG(self.gpio_axi4_bus)

        self.spi_dac_axi4_bus = AXI4LiteSubBus(self.axi4_bus, MIXSolarisSGRDef.MIX_SPIDAC_ADDR,
                                               MIXSolarisSGRDef.SPIDAC_REG_SIZE)
        self.spi_dac = PLSPIDAC(self.spi_dac_axi4_bus)
