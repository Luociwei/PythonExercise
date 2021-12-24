# -*- coding: utf-8 -*-
from __future__ import division
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.data_operate import DataOperate

__author__ = 'jiasheng@SmartGiant'
__version__ = '0.2'


class MIXSignalSourceSGDef:
    TEST_REGISTER = 0x00
    CONFIG_REGISTER = 0x10
    SIGNAL_REGISTER = 0x11
    DURATION_REGISTER = 0x40
    FREQUENCY_REGISTER = 0x20
    VPP_SCALE_REGISTER = 0x24
    DUTY_REGISTER = 0x28
    OFFSET_VOLT_REGISTER = 0x2C
    RX_BUF_REGISTER = 0x30
    AWG_START_REGISYER = 0x39
    SET_AWG_REGISTER = 0x3A
    REG_SIZE = 1024


class MIXSignalSourceSGException(Exception):
    def __init__(self, dev_name, err_str):
        self.err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self.err_reason


class MIXSignalSourceSG(object):
    '''
    Mix Signal Source function class

    ClassType = MIXSignalSourceSG

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string/None, AXI4LiteBus class intance or device path
                                                        if None, will create emulator.

    Examples:
        signal_source = MIXSignalSourceSG('/dev/MIX_SignalSource_SG')

    '''

    rpc_public_api = ['open', 'close', 'set_signal_type', 'set_signal_time',
                      'set_swg_paramter', 'output_signal', 'set_awg_step', 'set_awg_parameter',
                      'test_register']

    def __init__(self, axi4_bus=None):
        if isinstance(axi4_bus, basestring):
            # dev path; create axi4lite bus here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXSignalSourceSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.dev_name = self.axi4_bus._dev_name
        self.step_index = 0

    def open(self):
        '''
        Enable mix signal source function class

        Examples:
            signal_source.open()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXSignalSourceSGDef.CONFIG_REGISTER, 1)
        wr_data = (rd_data[0] & 0xFE) | 0x00
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.CONFIG_REGISTER,
                                     [wr_data])
        wr_data = (rd_data[0] & 0xFE) | 0x01
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.CONFIG_REGISTER,
                                     [wr_data])

    def close(self):
        '''
        Disable mix signal source function class

        Examples:
            signal_source.close()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXSignalSourceSGDef.CONFIG_REGISTER, 1)
        wr_data = (rd_data[0] & 0xFE) | 0x00
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.CONFIG_REGISTER, [wr_data])

    def set_signal_type(self, signal_type):
        '''
        Set output signal type

        Args:
            signal_type:    string, ['sine', 'square', 'AWG'], 'sine'--sine wave output
                                                               'square' -- square output
                                                               'AWG' -- arbitrary waveform output.

        Examples:
            signal_source.set_signal_type('sine')

        '''

        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.SIGNAL_REGISTER, [0x00])
        rd_data = self.axi4_bus.read_8bit_inc(MIXSignalSourceSGDef.CONFIG_REGISTER, 1)
        if(signal_type == 'sine'):
            signal_type_flag = 0x10
        elif(signal_type == 'square'):
            signal_type_flag = 0x00
        elif(signal_type == 'AWG'):
            signal_type_flag = 0x40
        else:
            raise MIXSignalSourceSGException(self.dev_name, "signal type set error")
            return False
        wr_data = (rd_data[0] & 0x0F) | signal_type_flag
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.CONFIG_REGISTER, [wr_data])

    def set_signal_time(self, signal_time):
        '''
        Set output signal time

        Args:
            signal_time:    int, unit us, signal time of signal source.

        Examples:
            signalsource.set_signal_time(10000)

        '''

        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.SIGNAL_REGISTER, [0x00])
        wr_data = DataOperate.int_2_list(signal_time, 4)
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.DURATION_REGISTER, wr_data)

    def set_swg_paramter(self, sample_rate, signal_frequency, vpp_scale,
                         square_duty, offset_volt=0):
        '''
        Set swg paramter

        Args:
            sample_rate:       int, unit SPS,             external DAC sample rate.
            signal_frequency:  int, unit Hz,              output signal frequency.
            vpp_scale:         float, [0.000~0.999,       full scale ratio.
            square_duty:       float, [0.001~0.999],      duty of square.
            offset_volt:       float, [-0.99999~0.99999], offset volt.

        Examples:
            signal_source.set_swg_paramter(1000, 1000, 0.5, 0.5, 0.5)

        '''

        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.SIGNAL_REGISTER, [0x00])
        freq_ctrl = int(pow(2, 32) * signal_frequency / sample_rate)
        wr_data = DataOperate.int_2_list(freq_ctrl, 4)
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.FREQUENCY_REGISTER, wr_data)
        vpp_ctrl = int((pow(2, 16) - 1) * vpp_scale)
        wr_data = DataOperate.int_2_list(vpp_ctrl, 2)
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.VPP_SCALE_REGISTER, wr_data)
        duty_ctrl = int((sample_rate / signal_frequency) * square_duty)
        wr_data = DataOperate.int_2_list(duty_ctrl, 4)
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.DUTY_REGISTER, wr_data)
        offset_volt_hex = int(offset_volt * pow(2, 23))
        wr_data = DataOperate.int_2_list(offset_volt_hex, 3)
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.OFFSET_VOLT_REGISTER, wr_data)

    def output_signal(self):
        '''
        Output signal wave

        Examples:
            signal_source.output_signal()

        '''

        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.SIGNAL_REGISTER, [0x01])

    def set_awg_step(self, sample_rate, start_volt, stop_volt, duration_ms):
        '''
        Set awg step

        Args:
            sample_rate:       int,          external DAC sample rate, unit is SPS
            start_volt:        float,        step start volt (-0.99999~0.99999)
            stop_volt:         float,        step start volt (-0.99999~0.99999)
            duration_ms:       float,        duration time

        Examples:
            signal_source.set_awg_step(1000, 0.5, 0.5, 0.5)

        '''
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.SIGNAL_REGISTER,
                                     [0x00])
        sample_cycle = 1000.0 / sample_rate
        duration_step = duration_ms / sample_cycle
        duration_step_cnt = int(duration_step / pow(2, 16)) + 1
        volt_step = (stop_volt - start_volt) / duration_step_cnt
        for i in range(0, duration_step_cnt):
            wr_data = []
            start_volt_temp = i * volt_step + start_volt
            step_duration_temp = int(duration_step / duration_step_cnt)
            step_ovlt_temp = volt_step * pow(2, 16) / step_duration_temp
            start_volt_hex = int(start_volt_temp * pow(2, 15))
            step_ovlt_hex = int(step_ovlt_temp * pow(2, 15))
            wr_list = DataOperate.int_2_list(step_duration_temp - 1, 2)
            wr_data.extend(wr_list)
            wr_list = DataOperate.int_2_list(step_ovlt_hex, 4)
            wr_data.extend(wr_list)
            wr_list = DataOperate.int_2_list(start_volt_hex, 2)
            wr_data.extend(wr_list)
            wr_data.append(self.step_index)
            self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.RX_BUF_REGISTER,
                                         wr_data)
            self.axi4_bus.\
                write_8bit_inc(MIXSignalSourceSGDef.AWG_START_REGISYER,
                               [0x01])
            self.step_index = self.step_index + 1
        return None

    def set_awg_parameter(self, sample_rate, awg_step):
        '''
        Set awg parameter

        Args:
            sample_rate:       int,          external DAC sample rate, unit is SPS
            awg_step:          list,         arbitrary waveform step,
                                                   list unit is (start_volt,stop_volt,duration_ms)
                                                   start_volt(float) -- step start volt (-1 ~ +1)
                                                   stop_volt(float) -- step stop volt (-1 ~ +1)
                                                   duration_ms(float) -- duration time

        Examples:
            signal_source.set_awg_step(1000, [0.5, 0.5, 0.5])

        '''
        self.step_index = 0
        for awg_step_temp in awg_step:
            self.set_awg_step(sample_rate, awg_step_temp[0],
                              awg_step_temp[1], awg_step_temp[2])
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.SET_AWG_REGISTER,
                                     [(self.step_index - 1)])
        return None

    def test_register(self, test_data):
        '''
        Test_register

        Args:
            sample_rate:       int,         test data

        Examples:
            signal_source.test_register(0xffff)

        '''
        wr_data = DataOperate.int_2_list(test_data, 4)
        self.axi4_bus.write_8bit_inc(MIXSignalSourceSGDef.TEST_REGISTER,
                                     wr_data)
        rd_data = self.axi4_bus.read_8bit_inc(MIXSignalSourceSGDef.TEST_REGISTER,
                                              len(wr_data))
        test_out = DataOperate.list_2_int(rd_data)
        return None
