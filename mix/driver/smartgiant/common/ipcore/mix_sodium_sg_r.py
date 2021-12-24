# -*- coding:utf-8 -*-
from mix.driver.smartgiant.common.ipcore.pl_spi_adc import PLSPIADC
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg import MIXSignalSourceSG
from mix.driver.smartgiant.common.ipcore.pl_spi_dac import PLSPIDAC
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.ipcore.pl_spi_adc_emulator import PLSPIADCEmulator
from mix.driver.smartgiant.common.ipcore. mix_signalmeter_sg_emulator import MIXSignalMeterSGEmulator
from mix.driver.smartgiant.common.ipcore.pl_spi_dac_emulator import PLSPIDACEmulator
from mix.driver.smartgiant.common.ipcore.mix_signalsource_sg_emulator import MIXSignalSourceSGEmulator


__author__ = 'tufeng.Mao@SmartGiant'
__version__ = '0.1'


class MIXSodiumSGRDef:
    MIX_SPIADC_V1_IPCORE_ADDR = 0x2000
    MIX_SIGNAL_METER_V1_IPCORE_ADDR = 0x4000
    MIX_SIGNAL_SOURCE0_V1_IPCORE_ADDR = 0x6000
    MIX_SPIDAC0_V1_IPCORE_ADDR = 0x8000
    MIX_SIGNAL_SOURCE1_V1_IPCORE_ADDR = 0xa000
    MIX_SPIDAC1_V1_IPCORE_ADDR = 0xc000
    SPIADC_REG_SIZE = 256
    SIGNAL_METER_REG_SIZE = 1024
    SIGNAL_SOURCE_REG_SIZE = 1024
    SPIDAC_REG_SIZE = 256
    REG_SIZE = 65536


class MIXSodiumSGRException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXSodiumSGR(object):
    '''
    MIXSodiumSGR aggregated IP includes MIXSPIADC, MIXSignalMeter , MIXSignalSource and MIXSPIDac

    ClassType = MIXSodiumSGR

    Args:
        axi4_bus:        instance(AXI4LiteBus), axi4_lite_bus instance.

    Examples:
        mix_sodium_sg_r = MIXSodiumSGR('/dev/MIX_SODIUM')

    '''

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            # device path; create axi4lite instance
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXSodiumSGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        if self.axi4_bus:
            self.open()
        else:
            self.spi_adc = PLSPIADCEmulator('pl_spi_adc_emulator', 256)
            self.signal_meter = MIXSignalMeterSGEmulator('mix_signalmeter_sg_emulator', 256)
            self.signal_source_0 = MIXSignalSourceSGEmulator('mix_signalsource_sg_emulator')
            self.signal_source_1 = MIXSignalSourceSGEmulator('mix_signalsource_sg_emulator')
            self.spi_dac_0 = PLSPIDACEmulator('pl_spi_dac_emulator')
            self.spi_dac_1 = PLSPIDACEmulator('pl_spi_dac_emulator')

    def open(self):
        '''
        MIXSodiumSGR  open device

        Examples:
            mix_sodium_sg_r.open()

        '''

        self.mix_spi_adc = AXI4LiteSubBus(self.axi4_bus, MIXSodiumSGRDef.MIX_SPIADC_V1_IPCORE_ADDR,
                                          MIXSodiumSGRDef.SPIADC_REG_SIZE)
        self.spi_adc = PLSPIADC(self.mix_spi_adc)

        self.mix_signal_meter = AXI4LiteSubBus(self.axi4_bus, MIXSodiumSGRDef.MIX_SIGNAL_METER_V1_IPCORE_ADDR,
                                               MIXSodiumSGRDef.SIGNAL_METER_REG_SIZE)
        self.signal_meter = MIXSignalMeterSG(self.mix_signal_meter)

        self.mix_signal_source_0 = AXI4LiteSubBus(self.axi4_bus, MIXSodiumSGRDef.MIX_SIGNAL_SOURCE0_V1_IPCORE_ADDR,
                                                  MIXSodiumSGRDef.SIGNAL_SOURCE_REG_SIZE)
        self.signal_source_0 = MIXSignalSourceSG(self.mix_signal_source_0)

        self.mix_signal_source_1 = AXI4LiteSubBus(self.axi4_bus, MIXSodiumSGRDef.MIX_SIGNAL_SOURCE1_V1_IPCORE_ADDR,
                                                  MIXSodiumSGRDef.SIGNAL_SOURCE_REG_SIZE)
        self.signal_source_1 = MIXSignalSourceSG(self.mix_signal_source_1)

        self.mix_spi_dac_0 = AXI4LiteSubBus(self.axi4_bus, MIXSodiumSGRDef.MIX_SPIDAC0_V1_IPCORE_ADDR,
                                            MIXSodiumSGRDef.SPIDAC_REG_SIZE)
        self.spi_dac_0 = PLSPIDAC(self.mix_spi_dac_0)

        self.mix_spi_dac_1 = AXI4LiteSubBus(self.axi4_bus, MIXSodiumSGRDef.MIX_SPIDAC1_V1_IPCORE_ADDR,
                                            MIXSodiumSGRDef.SPIDAC_REG_SIZE)
        self.spi_dac_1 = PLSPIDAC(self.mix_spi_dac_1)
