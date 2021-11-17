# -*- coding: utf-8 -*-

import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.data_operate import DataOperate


__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MIXQIASKLinkEncodeSGDef:
    # register address
    BASE_CLOCK_FREQ_REGISTER = 0x04
    MODULE_EN_REGISTER = 0x10
    TRANSMIT_START_REGISTER = 0x12
    STATE_REGISTER = 0x13
    FREQ_REGISTER = 0x14
    DATA_FIFO_REGISTER = 0x20
    DATA_LEN_REGISTER = 0x21

    # register enable
    MODULE_ENABLE = 0x01
    TRANSMIT_ENABLE = 0x01

    # Dedault Timeout 10s
    DEFAULT_TIMEOUT = 1000
    DELAY_S = 0.01

    MIN_FREQ = 100
    MAX_FREQ = 100000
    STATE_READY = 0x01
    INT_TO_LIST_LEN_3 = 3
    CLK_REGISTER_LEN = 4
    REG_SIZE = 256


class MIXQIASKLinkEncodeSGException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXQIASKLinkEncodeSG(object):
    '''
    MIX_QI_ASKLink_Encode_SG Driver
        Mainly used for wireless charging protocol QI, generating Ask signal
        (square wave).

    ClassType = ASKEncode

    Args:
        xi4_bus:     instance(AXI4LiteBus)/None, axi4_lite_bus instance.

    Examples:
        ask_encode = MIXQIASKLinkCode('/dev/MIX_QI_ASKLink_Encode_SG')

        # Set Ask signal frequency
        ask_encode.set_frequency(2000)

        # Send Ask signal
        wr_data = [1,2,3]
        ask_encode.write_encode_data(wr_data)

    '''

    rpc_public_api = ['get_base_clock', 'set_frequency', 'write_encode_data']

    def __init__(self, axi4_bus=None):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXQIASKLinkEncodeSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.__data_deal = DataOperate()
        self._enable()

    def __del__(self):
        self._disable()

    def _wait_for_ready(self):
        '''
        Waiting for ipcore status to be ready or timeout.

        Returns:
            boolean, [True, False], True is ready,Fasle is timeout.

        '''
        ret = 0
        start = time.time()
        while (time.time() < (start + MIXQIASKLinkEncodeSGDef.DEFAULT_TIMEOUT)):
            ret = self.axi4_bus.read_8bit_inc(MIXQIASKLinkEncodeSGDef.STATE_REGISTER,
                                              MIXQIASKLinkEncodeSGDef.STATE_READY)[0]
            if ret == MIXQIASKLinkEncodeSGDef.STATE_READY:
                return True
            time.sleep(MIXQIASKLinkEncodeSGDef.DELAY_S)
        return False

    def _enable(self):
        '''
        MIXQIASKLinkEncodeSG IP enable function.

        '''
        reg_data = self.axi4_bus.read_8bit_inc(MIXQIASKLinkEncodeSGDef.MODULE_EN_REGISTER, 1)[0]
        reg_data &= ~MIXQIASKLinkEncodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIASKLinkEncodeSGDef.MODULE_EN_REGISTER,
                                     [reg_data])
        reg_data |= MIXQIASKLinkEncodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIASKLinkEncodeSGDef.MODULE_EN_REGISTER, [reg_data])

    def _disable(self):
        '''
        MIXQIASKLinkEncodeSG IP disable function.

        '''
        reg_data = self.axi4_bus.read_8bit_inc(MIXQIASKLinkEncodeSGDef.MODULE_EN_REGISTER, 1)[0]
        reg_data &= ~MIXQIASKLinkEncodeSGDef.MODULE_ENABLE
        self.axi4_bus.write_8bit_inc(MIXQIASKLinkEncodeSGDef.MODULE_EN_REGISTER,
                                     [reg_data])

    def get_base_clock(self):
        '''
        Get the ipcore base clock frequency.

        Returns:
            int, value, unit Hz.

        '''
        base_clk = self.axi4_bus.read_8bit_inc(MIXQIASKLinkEncodeSGDef.BASE_CLOCK_FREQ_REGISTER,
                                               MIXQIASKLinkEncodeSGDef.CLK_REGISTER_LEN)
        return self.__data_deal.list_2_int(base_clk) * 1000

    def set_frequency(self, freq):
        '''
        Set the Ask signal frequency.

        Args:
            freq:  int, [100~100000], unit Hz, 2000 means 2000Hz.

        '''
        assert isinstance(freq, int)
        assert MIXQIASKLinkEncodeSGDef.MIN_FREQ <= freq <= MIXQIASKLinkEncodeSGDef.MAX_FREQ

        # get bace clocek frequency
        base_clk_freq = self.get_base_clock()

        # FREQ_DIV = BASE_CLK_FREQ / (FREQ * 2) - 2
        freq_div = int((base_clk_freq / (freq * 2)) - 2)
        if freq_div < 0:
            freq_div = 0
        wr_data = self.__data_deal.int_2_list(freq_div, MIXQIASKLinkEncodeSGDef.INT_TO_LIST_LEN_3)
        self.axi4_bus.write_8bit_inc(MIXQIASKLinkEncodeSGDef.FREQ_REGISTER, wr_data)

    def write_encode_data(self, wr_data):
        '''
        Write Ask encoded signal data (square wave) to FIFO.

        Args:
            wr_data:      list, Data to write, the list item is byte.

        Raises:
            MIXQIASKLinkEncodeSGException:    Waiting for the ipcore state timeout.

        '''
        assert isinstance(wr_data, list) and len(wr_data) > 0

        # Write data to fifo
        self.axi4_bus.write_8bit_fix(MIXQIASKLinkEncodeSGDef.DATA_FIFO_REGISTER, wr_data)
        # Start Transmt
        self.axi4_bus.write_8bit_inc(MIXQIASKLinkEncodeSGDef.TRANSMIT_START_REGISTER,
                                     [MIXQIASKLinkEncodeSGDef.TRANSMIT_ENABLE])
        if not self._wait_for_ready():
            raise MIXQIASKLinkEncodeSGException("timeout")
