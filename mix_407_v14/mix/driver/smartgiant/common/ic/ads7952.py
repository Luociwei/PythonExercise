# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator
from mix.driver.core.bus.axi4_lite_def import PLSPIDef

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class ADS7952Def:
    MANU_MODE_OFFSET = 12
    MANU_MODE_REGISTER = (0x01 << MANU_MODE_OFFSET)

    REG_PROGRAM_OFFSET = 11
    REG_EN_PROGRAM = (1 << REG_PROGRAM_OFFSET)

    REG_CHAN_OFFSET = 7
    REG_CHAN_MASK = (0x0F << REG_CHAN_OFFSET)

    REG_REF_OFFSET = 6
    REG_REF_MASK = (1 << REG_REF_OFFSET)
    REG_REF_RANGE_1 = (0 << REG_REF_OFFSET)
    REG_REF_RANGE_2 = (1 << REG_REF_OFFSET)

    REG_POWER_OFFSET = 5
    REG_POWER_MASK = (1 << REG_POWER_OFFSET)
    REG_NORMAL_OPERATION = (0 << REG_POWER_OFFSET)
    REG_POWER_DOWN = (1 << REG_POWER_OFFSET)

    MVREF_2500MV = 2500
    MVREF_5000MV = 5000


class ADS7952(object):
    '''
    ADS7952 function class

    ClassType = ADC

    Args:
        spi_bus:  instance(QSPI)/None,   MIXQSPISG class instance, if not
                                         using, will create emulator.
        mvref:    float, default 2500,   reference voltage.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT1_SPI_0', 256)
        spi_bus = MIXQSPISG(axi4_bus)
        ads7952 = ADS7952(spi_bus, 2500)

    '''

    def __init__(self, spi_bus=None, mvref=ADS7952Def.MVREF_2500MV):
        assert mvref == ADS7952Def.MVREF_2500MV or mvref == ADS7952Def.MVREF_5000MV
        if spi_bus is None:
            self.spi_bus = MIXQSPISGEmulator('ads7952_emulator', PLSPIDef.REG_SIZE)
        else:
            self.spi_bus = spi_bus
        self.mvref = mvref

    def read_volt(self, channel):
        '''
        ADS7952 read input voltage

        Args:
            channel:   int, [0~11], the channel to read voltage.

        Examples:
            data = ads7952.read_volt(0)
            print(data)

        '''
        assert channel >= 0 and channel < 12
        mode_register = ADS7952Def.MANU_MODE_REGISTER
        mode_register |= ADS7952Def.REG_EN_PROGRAM
        mode_register |= (channel << ADS7952Def.REG_CHAN_OFFSET)
        mode_register |= (ADS7952Def.REG_REF_RANGE_1 if self.mvref ==
                          ADS7952Def.MVREF_2500MV else ADS7952Def.REG_REF_RANGE_2)
        mode_register |= ADS7952Def.REG_NORMAL_OPERATION

        self.spi_bus.write([(mode_register >> 8) & 0xFF, mode_register & 0xFF])
        rd_data = self.spi_bus.read(2)

        self.spi_bus.write([(mode_register >> 8) & 0xFF, mode_register & 0xFF])
        rd_data = self.spi_bus.read(2)

        adc_value = (rd_data[0] << 8) | rd_data[1]
        return self.mvref * (adc_value & 0xFFF) / float(4096)
