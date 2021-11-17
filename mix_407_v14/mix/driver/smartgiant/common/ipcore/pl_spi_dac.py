# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.utility.data_operate import DataOperate

__author__ = 'ouyangde@gzseeing.com'
__version__ = '0.1'


class PLSPIDACDef:
    CONFIG_REGISTER = 0x10
    DAC_MODE_SET_REGISTER = 0x11
    FREQUENCY_SET_REGISTER = 0x24
    SAMPLE_DATA_SET_REGISTER = 0x20
    REG_SIZE = 256


class PLSPIDACException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class PLSPIDAC(object):
    '''
    Axi4 spi dac function class to control the spi dac

    ClassType = PLSPIDAC

    Args:
        axi4_bus:   instance(AXI4LiteBus)/None,  Class instance of AXI4 bus,
                                                 If not using this parameter,
                                                 will create Emulator

    Examples:
        spi_dac = PLSPIDAC('/dev/MIX_SPI_DAC')

    '''

    rpc_public_api = ['open', 'close', 'dac_mode_set', 'spi_sclk_frequency_set',
                      'sample_data_set', 'test_register', 'set_axi4_clk_frequency']

    def __init__(self, axi4_bus=None):
        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator(
                "pl_spi_dac_emulator", PLSPIDACDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            # device path passed in; create axi4litebus here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, PLSPIDACDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.dev_name = self.axi4_bus._dev_name
        self.reg_num = 256
        self.axi4_clk_frequency = 125000000
        self.data_deal = DataOperate()
        self.sclk_frequency = 10000000

        self.open()

    def __del__(self):
        self.close()

    def open(self):
        '''
        Axi4 spi dac open

        Examples:
            spi_dac.open()

        '''
        self.axi4_bus.write_8bit_inc(PLSPIDACDef.CONFIG_REGISTER, [0x00])
        self.axi4_bus.write_8bit_inc(PLSPIDACDef.CONFIG_REGISTER, [0x01])

    def close(self):
        '''
        Axi4 spi dac close

        Examples:
            spi_dac.close()

        '''
        self.axi4_bus.write_8bit_inc(PLSPIDACDef.CONFIG_REGISTER, [0x00])

    def dac_mode_set(self, dac_mode):
        '''
        Axi4 spi dac mode set

        Args:
            dac_mode:   int, set dac mode.

        Examples:
            spi_dac.dac_mode_set(0x12)

        '''
        wr_data = [dac_mode]
        self.axi4_bus.write_8bit_inc(
            PLSPIDACDef.DAC_MODE_SET_REGISTER, wr_data)

    def spi_sclk_frequency_set(self, sclk_freq_hz):
        '''
        Axi4 spi dac set sclk frequency

        Args:
            sclk_freq_hz:   int, unit Hz, set sclk frequency.

        Examples:
            spi_dac.spi_sclk_frequency_set(3000)

        '''

        self.sclk_frequency = sclk_freq_hz
        freq_hz_ctrl = int(sclk_freq_hz * pow(2, 32) /
                           self.axi4_clk_frequency)
        wr_data = self.data_deal.int_2_list(freq_hz_ctrl, 4)
        self.axi4_bus.write_8bit_inc(
            PLSPIDACDef.FREQUENCY_SET_REGISTER, wr_data)

    def sample_data_set(self, sample_rate):
        '''
        Axi4 spi dac set sample data

        Args:
            sample_rate:   int, unit Hz, set sample data.

        Examples:
            spi_dac.sample_data_set(3000)

        '''
        freq_hz_ctrl = int(sample_rate * pow(2, 32) / self.sclk_frequency)
        wr_data = self.data_deal.int_2_list(freq_hz_ctrl, 4)
        self.axi4_bus.write_8bit_inc(
            PLSPIDACDef.SAMPLE_DATA_SET_REGISTER, wr_data)

    def test_register(self, test_data):
        '''
        Axi4 spi dac test register

        Args:
            test_data:   int, test data.

        Examples:
            self.test_register(30)

        '''
        wr_data = self.data_deal.int_2_list(test_data, 4)
        self.axi4_bus.write_8bit_inc(PLSPIDACDef.CONFIG_REGISTER, wr_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            PLSPIDACDef.CONFIG_REGISTER, len(wr_data))
        test_out = self.data_deal.list_2_int(rd_data)
        if(test_out != test_data):
            raise PLSPIDACException(
                self.dev_name, 'Test Register read data error. ')
            return False

    def set_axi4_clk_frequency(self, clk_frequency):
        '''
        Axi4 spi dac set axi4 clock frequency

        Args:
            clk_frequency:   int,  clock frequency.

        Examples:
            spi_dac.set_axi4_clk_frequency(50000)

        '''
        self.axi4_clk_frequency = clk_frequency
