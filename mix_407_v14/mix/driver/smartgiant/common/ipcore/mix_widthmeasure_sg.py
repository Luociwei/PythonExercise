# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.data_operate import DataOperate

__author__ = 'huanghanyong@SmartGiant'
__version__ = '0.1'


class MIXWidthMeasureSGDef:
    ENABLE = 0x01
    DISABLE = 0x00
    ONE_SECOND = 1000000   # Convert 1 second to microseconds
    REG_SIZE = 256
    MODULE_EN = 0x10
    MEASURE_EN = 0x11
    DATA_BUFFER = 0x1C
    BASE_CLK_FREQUENCY = 0x0C
    START_POINT_SELECT = 0x12
    STOP_POINT_SELECT = 0x13
    DATA_COUNT_BUFFER = 0x24
    READ_FREQUENCY_DATA_LEN = 1
    READ_RESULT_COUNT_LEN = 1
    MEASURE_DATA_COUNT = 2


class TriggarSignalDef:
    '''
    TriggarSignalDef class define 15 kinds of trigger signal way

    :A:     Trigger signal A
    :B:     Trigger signal B
    :AB:    Trigger signal A and B
    :POS:   posedge
    :NEG:   negedge
    :PON:   posedge or negedge
    '''
    SIGNAL_A_POS = 1
    SIGNAL_A_NEG = 2
    SIGNAL_A_PON = 3
    SIGNAL_B_POS = 4
    SIGNAL_AB_POS = 5
    SIGNAL_A_NEG_B_POS = 6
    SIGNAL_A_PON_B_POS = 7
    SIGNAL_B_NEG = 8
    SIGNAL_A_POS_B_NEG = 9
    SIGNAL_AB_NEG = 10
    SIGNAL_A_PON_B_NEG = 11
    SIGNAL_B_PON = 12
    SIGNAL_A_POS_B_PON = 13
    SIGNAL_A_NEG_B_PON = 14
    SIGNAL_AB_PON = 15
    SIGNAL_NUM = 16


class MIXWidthValue():
    '''
    MIXWidthValue class to define measure result

    ClassType = MIXWidthValue

    Args:
        width:   measure result        unit: ns
        start:   start trigger signal  range value: 0-3
        stop:    stop trigger signal   range value: 0-3
                    range value: 0-3\n
                        0: trigger signal is SIGNAL_A_POS\n
                        1: trigger signal is SIGNAL_A_NEG\n
                        2: trigger signal is SIGNAL_B_POS\n
                        3: trigger signal is SIGNAL_B_NEG
    '''
    def __init__(self, width, start, stop):
        self.width = width
        self.start_signal = start
        self.stop_signal = stop


class MIXWidthMeasureSG(object):
    '''
    MIXWidthMeasureSG function class to measure the time difference between edge signals

    ClassType = MIXWidthMeasureSG

    Args:
        axi4_bus: instance(AXI4LiteBus)/string/None,   Class instance or dev path of AXI4 bus.

    Examples:
        width_measure = MIXWidthMeasureSG('/dev/MIX_Signal_Meter_0')

    '''

    rpc_public_api = ['start_measure', 'stop_measure', 'config', 'get_width']

    def __init__(self, axi4_bus=None):
        if isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXWidthMeasureSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.dev_name = self.axi4_bus._dev_name
        self.data_deal = DataOperate()
        rd_data = self.axi4_bus.read_32bit_inc(MIXWidthMeasureSGDef.BASE_CLK_FREQUENCY,
                                               MIXWidthMeasureSGDef.READ_FREQUENCY_DATA_LEN)
        self.clk_frequency = rd_data[0]   # rd_data: type: int unit: KHz

        # disable all register and clear buffer cache,then all registers work
        self.stop_measure()
        # enable all register, then all registers work
        self.axi4_bus.write_8bit_inc(MIXWidthMeasureSGDef.MODULE_EN, [MIXWidthMeasureSGDef.ENABLE])

    def start_measure(self):
        '''
        MIXWidthMeasureSG module enable the corresponding register, then can get result

        Returns:
            None.

        Examples:
            axi4_bus = Axi4LiteBus("/dev/MIX_SIGNAL_METER", 1024)
            width_measure = MIXWidthMeasureSG(axi4_bus)
            width_measure.start_measure()

        '''
        # enable all register, then all registers work
        self.axi4_bus.write_8bit_inc(MIXWidthMeasureSGDef.MODULE_EN, [MIXWidthMeasureSGDef.ENABLE])
        self.axi4_bus.write_8bit_inc(MIXWidthMeasureSGDef.MEASURE_EN, [MIXWidthMeasureSGDef.ENABLE])

    def stop_measure(self):
        '''
        MIXWidthMeasureSG module disable the corresponding register, then can't get result

        Returns:
            None.

        Examples:
            width_measure = MIXWidthMeasureSG(axi4_bus)
            width_measure.stop_measure()

        '''
        self.axi4_bus.write_8bit_inc(MIXWidthMeasureSGDef.MEASURE_EN, [MIXWidthMeasureSGDef.DISABLE])
        # disable all register, then all registers work
        self.axi4_bus.write_8bit_inc(MIXWidthMeasureSGDef.MODULE_EN, [MIXWidthMeasureSGDef.DISABLE])

    def config(self, start_triggar_signal=1, stop_triggar_signal=4):
        '''
        MIXWidthMeasureSG module config start and stop triggar signal state, then can get measure result

        Returns:
            None.

        Args:
            triggar_signal:   int,   start trigger signal, details in class TriggarSignal.

        Examples:
            axi4_bus = Axi4LiteBus("/dev/MIX_SIGNAL_METER", 1024)
            width_measure = MIXWidthMeasureSG(axi4_bus)
            width_measure.config(1,4)

        '''
        assert isinstance(start_triggar_signal, int)
        assert start_triggar_signal > 0
        assert start_triggar_signal < TriggarSignalDef.SIGNAL_NUM
        assert isinstance(stop_triggar_signal, int)
        assert stop_triggar_signal > 0
        assert stop_triggar_signal < TriggarSignalDef.SIGNAL_NUM

        self.axi4_bus.write_8bit_inc(MIXWidthMeasureSGDef.START_POINT_SELECT, [start_triggar_signal])
        self.axi4_bus.write_8bit_inc(MIXWidthMeasureSGDef.STOP_POINT_SELECT, [stop_triggar_signal])

    def get_width(self):
        '''
        MIXWidthMeasureSG module get time measure result

        Returns:
            list,  list of MIXWidthValue.

        Examples:
            axi4_bus = Axi4LiteBus("/dev/MIX_SIGNAL_METER", 1024)
             width_measure = MIXWidthMeasureSG(axi4_bus)
             width_measure.config(1, 4)
             width_measure.start_measure()
             data = width_measure.get_width()
             width_measure.stop_measure()

        '''
        rd_data = self.axi4_bus.read_32bit_inc(MIXWidthMeasureSGDef.DATA_COUNT_BUFFER,
                                               MIXWidthMeasureSGDef.READ_RESULT_COUNT_LEN)
        # rd_data[0] is data count
        width_data_cnt = rd_data[0]
        if 0 == width_data_cnt:
            return []

        rd_data_int = []
        width_data = []
        # width_data_cnt * 8: The length of data displayed in a register
        for i in range(width_data_cnt):
            # rd_data format    type: list     length : 2        content: index [0-1] store little-endian data
            rd_data = self.axi4_bus.read_32bit_inc(MIXWidthMeasureSGDef.DATA_BUFFER,
                                                   MIXWidthMeasureSGDef.MEASURE_DATA_COUNT)
            # little-endian -> big-endian conversion, data width: 64bit
            rd_data_int.append((rd_data[1] << 32) | rd_data[0])

        # Clock period calculation: T(s) = 1 / F(Hz)    clk_period: type: float  unit: ns
        clk_period = MIXWidthMeasureSGDef.ONE_SECOND / self.clk_frequency

        # data format     bit width: 64 bits
        # 0-1 bits: starting trigger signal  2-3 bits: stopping trigger signal  4-63 bits: measure result
        for data in rd_data_int:
            # The lower four bits hold the trigger signal. 'data >> 4' means the measurement results.
            width = (data >> 4) * clk_period
            # The starting trigger signal is stored in the lower 2 bits, 'data % 4' means to get 0-1bits
            start_signal = data % 4
            # 'data % 16' means to get lower four bits result, '>>2' means to get 2-3bits
            stop_signal = data % 16 >> 2
            width_data.append(MIXWidthValue(width, start_signal, stop_signal))
        return width_data
