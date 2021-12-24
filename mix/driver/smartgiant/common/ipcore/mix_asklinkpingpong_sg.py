# -*- coding: utf-8 -*-

from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.data_operate import DataOperate


__author__ = 'wenjun.sun@SmartGiant'
__version__ = '0.1'


class MIXASKLinkPingPongSGDef:
    BASE_CLK_FREQ_REG = 0x04
    MODULE_EN_REG = 0x10
    ASK_ENCODE_START_REG = 0x12
    ASK_FREQ_SET_REG = 0x14
    ASK_ENCODE_DATA_REG = 0x20
    ASK_DATA_CNT_REG = 0x21
    START_SEL_REGISTER = 0x26
    DELAY_TIME_CONTROL_REG = 0x24
    DETECTION_STATUS_REG = 0x27

    MODULE_ENABLE = 0x01
    MODULE_DISABLE = 0x00
    TRANSMIT_ENABLE = 0x01
    TRANSMIT_DISABLE = 0x00

    ASK_START_MANUAL = 0x00
    ASK_START_AUTO = 0x01
    OVER_STATUS_CLEAR = 0x01
    REG_SIZE = 256


class MIXASKLinkPingPongSG(object):
    '''
    MIX_ASKLinkPingPongSG IP function class.

    Args:
        axi4_bus:   string/instance, device name or instance of AXI4LiteBus.

    '''
    def __init__(self, axi4_bus=None):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXASKLinkPingPongSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.__data_deal = DataOperate()

    def __del__(self):
        self.disable()

    def enable(self):
        '''
        IP enable function.
        '''
        self.axi4_bus.write_8bit_inc(MIXASKLinkPingPongSGDef.MODULE_EN_REG,
                                     [MIXASKLinkPingPongSGDef.MODULE_ENABLE])

    def disable(self):
        '''
        IP disable function.
        '''
        self.axi4_bus.write_8bit_inc(MIXASKLinkPingPongSGDef.MODULE_EN_REG,
                                     [MIXASKLinkPingPongSGDef.MODULE_DISABLE])

    def encode_config(self, mode="manual", delay_us=6000):
        '''
        ask encode config

        Args:
            mode:       string, ['manual', 'auto'], select ask encode start mode.
            delay_us:   int, after receiving fsk decoding signal, start to output ask code after
                             delay time setting time in us.
        '''
        assert mode in ['auto', 'manual']
        if mode == "manual":
            self.axi4_bus.write_8bit_inc(MIXASKLinkPingPongSGDef.START_SEL_REGISTER,
                                         [MIXASKLinkPingPongSGDef.ASK_START_MANUAL])
        elif mode == "auto":
            self.axi4_bus.write_8bit_inc(MIXASKLinkPingPongSGDef.START_SEL_REGISTER,
                                         [MIXASKLinkPingPongSGDef.ASK_START_AUTO])
        wr_data = self.__data_deal.int_2_list(delay_us, 2)
        self.axi4_bus.write_8bit_inc(MIXASKLinkPingPongSGDef.DELAY_TIME_CONTROL_REG,
                                     wr_data)

    def ask_over_status_detection(self):
        '''
        detection ask encode over status
        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXASKLinkPingPongSGDef.DETECTION_STATUS_REG, 1)
        return rd_data[0]

    def ask_over_status_clear(self):
        '''
        ask encode over status software clear
        '''
        self.axi4_bus.write_8bit_inc(MIXASKLinkPingPongSGDef.DETECTION_STATUS_REG,
                                     [MIXASKLinkPingPongSGDef.OVER_STATUS_CLEAR])

    def set_ask_data_frequency(self, ask_data_freq):
        '''
        set_ask_date_frequency

        Args:
            set_ask_data_frequency:     int, ask data frequency,100~100000Hz
        '''
        # get bace clocek frequency

        rd_data = self.axi4_bus.read_8bit_inc(MIXASKLinkPingPongSGDef.BASE_CLK_FREQ_REG, 4)
        base_clk_freq = self.__data_deal.list_2_int(rd_data)

        # FREQ_DIV = BASE_CLK_FREQ / (FREQ * 2) - 2
        freq_div = int((base_clk_freq / ask_data_freq / 2) - 2)
        wr_data = self.__data_deal.int_2_list(freq_div, 3)
        self.axi4_bus.write_8bit_inc(MIXASKLinkPingPongSGDef.ASK_FREQ_SET_REG, wr_data)

    def send_ask_decode_data(self, ask_send_data):
        '''
        send_ask_decode_data, include checksum data

        Args:
            send_ask_decode_data(list): ask send data
        '''
        assert len(ask_send_data) > 0

        # send ask data to ask data_fifo
        self.axi4_bus.write_8bit_fix(MIXASKLinkPingPongSGDef.ASK_ENCODE_DATA_REG, ask_send_data)

    def enable_output(self):
        '''
        Enable ASK output.
        '''
        self.axi4_bus.write_8bit_inc(MIXASKLinkPingPongSGDef.ASK_ENCODE_START_REG,
                                     [MIXASKLinkPingPongSGDef.TRANSMIT_ENABLE])

    def disable_output(self):
        '''
        Disable ASK output
        '''
        self.axi4_bus.write_8bit_inc(MIXASKLinkPingPongSGDef.ASK_ENCODE_START_REG,
                                     [MIXASKLinkPingPongSGDef.TRANSMIT_DISABLE])
