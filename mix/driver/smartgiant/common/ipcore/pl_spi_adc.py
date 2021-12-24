# -*- coding: UTF-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.utility.data_operate import DataOperate

__author__ = 'huangzicheng@gzseeing'
__version__ = '0.1'


class PLSPIADCDef:
    CONFIG_REGISTER = 0x10
    SAMPLE_SET_REGISTER = 0x20
    SAMPLE_GET_REGISTER = 0x24
    DISABLE_CMD = 0x00
    REG_SIZE = 256


class PLSPIADCException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class PLSPIADC(object):
    '''
    PLSPIADC class provide function to open close

    ClassType = PLSPIADC

    Args:
        axi4_bus:     instance(AXI4LiteBus)/string/None, axi4lite bus instance
                                                         or device path.

    Examples:
        spi_adc = PLSPIADC('/dev/MIX_PL_SPI_ADC')

    '''

    rpc_public_api = ['open', 'close', 'set_sample_rate', 'get_sample_data',
                      'test_register', 'set_axi4_clk_frequency']

    def __init__(self, axi4_bus=None):
        self.pl_clk_frequency = 125000000
        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator("pl_spi_adc_emulator",
                                                PLSPIADCDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            # create axi4lite bus from given device path
            self.axi4_bus = AXI4LiteBus(axi4_bus, PLSPIADCDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.open()

    def open(self):
        '''
        PLSPIADC open function

        Examples:
            self.axi4_bus.open()

        '''
        self.axi4_bus.write_8bit_inc(PLSPIADCDef.CONFIG_REGISTER, [0x00])
        self.axi4_bus.write_8bit_inc(PLSPIADCDef.CONFIG_REGISTER, [0x01])

    def close(self):
        '''
        PLSPIADC close function

        Examples:
            self.axi4_bus.close()

        '''
        self.axi4_bus.write_8bit_inc(0x10, [0x2B, 0x08, 0x00, 0x00])
        self.axi4_bus.write_8bit_inc(PLSPIADCDef.CONFIG_REGISTER, [0x00])

    def set_sample_rate(self, sample_rate):
        '''
        PLSPIADC set sample rate

        Args:
            sample_rate:    int, [0~15000], unit SPS.

        Examples:
            self.axi4_bus.set_sample_rate(15000)

        '''
        freq_hz_ctrl = int(sample_rate * pow(2, 32) / self.pl_clk_frequency)
        wr_data = DataOperate.int_2_list(freq_hz_ctrl, 4)
        self.axi4_bus.write_8bit_inc(PLSPIADCDef.SAMPLE_SET_REGISTER, wr_data)

    def get_sample_data(self):
        '''
        PLSPIADC get sample rate

        Returns:
            int, value, sample_volt.

        Examples:
            ret = self.axi4_bus.get_sample_data()
            print(ret)

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            PLSPIADCDef.SAMPLE_GET_REGISTER, 4)
        sample_data = DataOperate.list_2_int(rd_data)
        sample_volt = float(sample_data) / pow(2, 31)
        return sample_volt

    def test_register(self, test_data):
        '''
        PLSPIADC test register

        Args:
            test_data:    int, [0x123], test data.

        Examples:
            self.test_register(0x123)

        '''
        wr_data = DataOperate.int_2_list(test_data, 4)
        self.axi4_bus.write_8bit_inc(PLSPIADCDef.DISABLE_CMD, wr_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            PLSPIADCDef.DISABLE_CMD, len(wr_data))
        test_out = DataOperate.list_2_int(rd_data)
        if(test_out != test_data):
            raise PLSPIADCException(
                self._dev_name, "Test Register read data error.")

    def set_axi4_clk_frequency(self, clk_frequency):
        '''
        PLSPIADC set axi4 clock frequency

        Args:
            clk_frequency:    int, [0~125000000], clock frequency.

        Examples:
            self.set_axi4_clk_frequency(1000)

        '''
        self.pl_clk_frequency = clk_frequency
