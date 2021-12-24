# -*- coding: utf-8 -*-
from mix.driver.smartgiant.common.utility.data_operate import DataOperate
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'huangjianxuan@SmartGiant'
__version__ = '1.0'


class MIXADS9224RSGDef:
    ENABLE_REGISTER = 0x10
    SAMPLE_SET_REGISTER = 0x11
    SCLK_SET_REGISTER = 0x14
    SAMPLE_TIME_REGISTER = 0x18
    BUS_BUSY = 0x1C
    READY_LEVEL = 0x1F
    TX_DATA_REGISTER = 0x20
    SAMPLE_GET_REGISTER = 0x24
    CNT_FIFO_REGISTER = 0x28
    REG_SIZE = 256
    CLK_FREQ = 125000000
    SPI_TYPE = 0x00
    DEFAULT_COMMAND = 0x020000
    ENABLE = 0x01
    DISABLE = 0x00
    OPCORE_BIT = 12
    OPCORE_NOP0 = 0x0
    OPCORE_NOP1 = 0xF
    OPCORE_READ = 0x2
    WRITE_COMMAND = 0x040000
    READ_COMMAND = 0x060000
    SINGLE_COMMAND = 0x070000
    MULTIPLE_COMMAND = 0x0f0000


class MIXADS9224RSGException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class MIXADS9224RSG(object):
    '''
    The MIXADS9224RSG class provides an interface to the MIX ADS9224R IPcore.

    ClassType = MIXADS9224RSG

    Args:
        axi4_bus:   instance(AXI4LiteBus)/None, Class instance of axi4 bus
    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 8192)
        ad9224r = MIXADS9224RSG(axi4_bus)

    '''

    def __init__(self, axi4_bus=None):
        self.clk_frequency = MIXADS9224RSGDef.CLK_FREQ
        self.spi_type = MIXADS9224RSGDef.SPI_TYPE
        self.command = MIXADS9224RSGDef.DEFAULT_COMMAND

        if isinstance(axi4_bus, basestring):
            # create axi4lite bus from given device path
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXADS9224RSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.open()

    def open(self):
        '''
        MIXADS9224RSG open device

        Examples:
            ad9224r.open()

        '''
        self.axi4_bus.write_8bit_inc(MIXADS9224RSGDef.ENABLE_REGISTER, [MIXADS9224RSGDef.DISABLE | self.spi_type])
        self.axi4_bus.write_8bit_inc(MIXADS9224RSGDef.ENABLE_REGISTER, [MIXADS9224RSGDef.ENABLE | self.spi_type])

    def close(self):
        '''
        MIXADS9224RSG close device

        Examples:
            ad9224r.close()

        '''
        while 1:
            ret = self.get_bus_busy()
            if(ret[0] & 0x01):
                continue
            else:
                break
        self.axi4_bus.write_8bit_inc(MIXADS9224RSGDef.ENABLE_REGISTER, [MIXADS9224RSGDef.DISABLE | self.spi_type])

    def set_sample_rate(self, sample_rate):
        '''
        Set the ADS9224R chip sampling rate
        Args:
            sample_rate:int,[0-1500000],sampling rate.
        Examples:
            ad9224r.set_sample_rate(1500000)

        '''
        sample_fre = int(pow(10, 9) / (sample_rate * 8))
        wr_data = DataOperate.int_2_list(sample_fre, 3)
        self.axi4_bus.write_8bit_inc(MIXADS9224RSGDef.SAMPLE_SET_REGISTER, wr_data)

    def set_spi_type(self, CPOL=0, CPHA=0):
        '''
        Set spi type.
        Args:
            CPOL:int,[0, 1], clock polarity.
            CPHA:int, [0, 1], clock phase.
        Examples:
            ad9224r.set_spi_type(0, 1)

        '''
        if(CPOL):
            self.spi_type = self.spi_type | 0x20
        if(CPHA):
            self.spi_type = self.spi_type | 0x10

    def set_spi_sclk(self, fre_ctrl):
        '''
        Set spi sclk.
        Args:
            fre_ctrl:int, spi clock frequency.
        Examples:
            ad9224r.set_spi_sclk(20000000)

        '''
        sclk_fre = int(fre_ctrl * pow(2, 32) / self.clk_frequency)
        wr_data = DataOperate.int_2_list(sclk_fre, 4)
        self.axi4_bus.write_8bit_inc(MIXADS9224RSGDef.SCLK_SET_REGISTER, wr_data)

    def set_continu_sample_time(self, time):
        '''
        Set spi sclk.
        Args:
            time:int, unit ms,sample time.
        Examples:
            ad9224r.set_continu_sample_time(1000)
        '''
        cnt_ns = int(time * pow(10, 6) / 8)
        wr_data = DataOperate.int_2_list(cnt_ns, 4)
        self.axi4_bus.write_8bit_inc(MIXADS9224RSGDef.SAMPLE_TIME_REGISTER, wr_data)

    def set_tx_data(self, tx_data, single_sample=1):
        '''
        Set command data.
        Args:
            tx_data:hex,[0x0000~0xffff], command data.
            single_sample:int,[0,1],1 is single sample,0 is multiple sampling.
        Examples:
            ad9224r.set_tx_data(0x0000, 0)
        '''
        opcore = tx_data >> MIXADS9224RSGDef.OPCORE_BIT
        if(single_sample):
            if(opcore == MIXADS9224RSGDef.OPCORE_NOP0 or opcore == MIXADS9224RSGDef.OPCORE_NOP1):
                self.command = MIXADS9224RSGDef.SINGLE_COMMAND
            elif(opcore == MIXADS9224RSGDef.OPCORE_READ):
                self.command = MIXADS9224RSGDef.READ_COMMAND
            else:
                self.command = MIXADS9224RSGDef.WRITE_COMMAND
        else:
            if(opcore == MIXADS9224RSGDef.OPCORE_NOP0 or opcore == MIXADS9224RSGDef.OPCORE_NOP1):
                self.command = MIXADS9224RSGDef.MULTIPLE_COMMAND
        wr_data = tx_data | self.command
        self.axi4_bus.write_32bit_inc(MIXADS9224RSGDef.TX_DATA_REGISTER, [wr_data])

    def get_ready_level(self):
        '''
        Get spi ready signal.
        Returns:
            list.
        Examples:
            ad9224r.get_ready_level()
        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXADS9224RSGDef.READY_LEVEL, 1)
        return rd_data

    def get_bus_busy(self):
        '''
        Get spi bus busy signal.
        Returns:
            list.
        Examples:
            ad9224r.get_bus_busy()
        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXADS9224RSGDef.BUS_BUSY, 1)
        return rd_data
