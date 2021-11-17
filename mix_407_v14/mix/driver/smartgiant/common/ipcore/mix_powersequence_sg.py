# -*- coding: utf-8 -*-
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.data_operate import DataOperate

__author__ = 'ZiCheng.Huang@SmartGiant'
__version__ = '0.1'


class MIXPowerSequenceSGException(Exception):
    '''
    MIXPowerSequenceSGException shows the exception of mix powersequence sg.
    '''

    def __init__(self, err_str):
        self.err_reason = '%s' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXPowerSequenceSGDef:
    REGISTER_SIZE = 1024
    CONFIG_DATA = 0x00
    CONFIG_REGISTER = 0x10
    FREQUENCY_REGISTER = 0x20
    TIME_REGISTER = 0x11
    STATUS_REGISTER = 0x13
    SWITCH_REGISTER_1 = 0x1c
    SWITCH_REGISTER_2 = 0x14
    CHANNEL_COUNT_REGISTER = 0x18
    CHANNEL_BASE_REGISTER = 0x40
    CHANNEL_ATTACHED_BASE_REGISTER = 0x80
    TRIGGER_CHANNEL_NUM_REGISTER = 0x20
    TRIGGER_RISE_TIME_REGISTER = 0x24
    TRIGGER_FALL_TIME_REGISTER = 0x28


class MIXPowerSequenceSG(object):
    '''
    This IPcore is used to switch channels and upload data to DMA, which can
    support up to 64 channels. Digital signals are collected from beast board's AD5231,
    and then the IPcore is collected and uploaded to DMA.

    ClassType = MIXPowerSequenceSG

    Args:
        axi4_bus: instance(AXI4LiteBus)/string/None, AXI4LiteBus intance or device path

    Examples:
        power_sequence = MIXPowerSequenceSG('/dev/MIX_PowerSequence_SG')

        # use example
        if used for read the trigger time, steps:
            1.self.close()  #  ensure that closed
            2.self.open()
            3.self.measure_time(1000)  # set the ipcore measure time, unit is ms
            4.self.measure()  # start to measure the data
            5.self.get_interrupt_time()  # get the pos edge time and neg edge time

        if used for upload data, steps:
            1.must to set the AD5231 enable pin to low level
            2.self.set_sample_channel([1,2,3,4])  # set the ipcore channel to read the data
            3.self.set_channel_attached([1,1,1,1,1,1,1,])  # set the extra info to the upload data
            4.self.set_sample_parameter(1000, 200, 1)  # set the sample rate,
              channel switch time and the channel sample count.
            5.self.open()
            6.self.measure()  # start to measure, get the data
            7.self.close()

    '''

    rpc_public_api = ['open', 'close', 'measure_time', 'measure_state',
                      'measure', 'set_sample_parameter', 'set_sample_channel', 'set_channel_attached',
                      'get_interrupt_time']

    def __init__(self, axi4_bus=None):
        if isinstance(axi4_bus, basestring):
            # dev path; create axi4lite bus here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXPowerSequenceSGDef.REGISTER_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.dev_name = self.axi4_bus._dev_name
        self.sample_time = None

        self.open()

    def open(self):
        '''
        open power sequence function class

        Returns:
            None.

        Examples:
            power_sequence.open()

        '''
        self.axi4_bus.write_8bit_fix(MIXPowerSequenceSGDef.CONFIG_REGISTER, [MIXPowerSequenceSGDef.CONFIG_DATA])
        self.axi4_bus.write_8bit_fix(MIXPowerSequenceSGDef.CONFIG_REGISTER, [MIXPowerSequenceSGDef.CONFIG_DATA | 0x01])
        return None

    def close(self):
        '''
        close power sequence function class

        Returns:
            None.

        Examples:
            power_sequence.close()

        '''
        self.axi4_bus.write_8bit_fix(MIXPowerSequenceSGDef.CONFIG_REGISTER, [MIXPowerSequenceSGDef.CONFIG_DATA])
        return None

    def measure_time(self, time_ms):
        '''
        power sequence set measure time, Set the ipcore to measure the duration of the trigger voltage

        Args:
            time_ms:     int,[0~65535], unit ms.

        Examples:
            power_sequence.measure_time = 3000

        '''
        assert time_ms > 0 and time_ms <= 65535
        self.sample_time = time_ms
        times = DataOperate.int_2_list(time_ms, 2)
        self.axi4_bus.write_8bit_inc(MIXPowerSequenceSGDef.TIME_REGISTER, times)

    def measure_state(self):
        '''
        power sequence get measure state, read the ipcore status.

        Returns:
            string, ["BUSY", "IDLE"].

        Examples:
            print(power_sequence.measure_state)

        '''
        rd_data = self.axi4_bus.read_8bit_fix(MIXPowerSequenceSGDef.STATUS_REGISTER, 1)
        if rd_data[0] & 0x10 == 0x00:
            return "BUSY"
        else:
            return "IDLE"

    def measure(self):
        '''
        power sequence start sample voltage and upload raw data

        Returns:
            boolean, [True, False],

        Examples:
            power_sequence.measure()

        '''
        if(self.measure_state == 'BUSY'):
            raise MIXPowerSequenceSGException("MIXPowerSequenceSG bus busy.")
        self.axi4_bus.write_8bit_fix(MIXPowerSequenceSGDef.STATUS_REGISTER, [0x01])

    def set_sample_parameter(self, sample_rate, switch_wait_ns, switch_sample_count):
        '''
        Set sample rate, switch wait time, switch sample count

        power sequence set sample prameter, set the ipcore channel sample rate, each channel switch time and
        each channel sample count.

        Args:
            sample_rate:         int, [0~40000000], unit Hz, ADC Chip sample rate.
            switch_wait_ns:      int, (>0), unit ns, The waiting time after switching the sampling channel.
            switch_sample_count: int, (>0), The number of sampled data after switching the sampling channel.

        Returns:
            None.

        Examples:
            power_sequence.set_sample_parameter(40000000,300,1)

        '''
        assert sample_rate > 0 and sample_rate <= 40000000
        assert switch_wait_ns > 0
        assert switch_sample_count > 0
        sample_cycle = 1000000000 / sample_rate
        ch_wait = int(switch_wait_ns / sample_cycle) - 3
        data_temp = ch_wait + switch_sample_count * pow(2, 16)
        self.axi4_bus.write_32bit_fix(MIXPowerSequenceSGDef.SWITCH_REGISTER_1, [data_temp])
        frame_sample_rate = int(1000000 / ((ch_wait + 3) * sample_cycle))
        self.axi4_bus.write_32bit_fix(MIXPowerSequenceSGDef.SWITCH_REGISTER_2, [frame_sample_rate])

    def set_sample_channel(self, ch_sel):
        '''
        power sequence Set sample channel, this function is used for set the ipcore sample channel.

        Args:
            list, select the sample channle.

        Returns:
            None.

        Examples:
            power_sequence.set_sample_channel([1,3,4,5,6,...,40])

        '''
        assert isinstance(ch_sel, list) and len(ch_sel) > 0
        write_data = len(ch_sel) - 1
        self.axi4_bus.write_8bit_fix(MIXPowerSequenceSGDef.CHANNEL_COUNT_REGISTER, [write_data])
        self.axi4_bus.write_8bit_inc(MIXPowerSequenceSGDef.CHANNEL_BASE_REGISTER, ch_sel)

    def set_channel_attached(self, ch_attached):
        '''
        Config channel attached

        power sequence Set extra information for each sample channel. Extra information will upload
        with data of every channel.

        Args:
            list, extra information for each sample channel

        Returns:
            None.

        Examples:
            power_sequence.set_channel_attached([2,2,2,2,2,2,2])

        '''
        assert isinstance(ch_attached, list) and len(ch_attached) > 0
        self.axi4_bus.write_8bit_inc(MIXPowerSequenceSGDef.CHANNEL_ATTACHED_BASE_REGISTER, ch_attached)

    def get_interrupt_time(self, clk_freq, ch_num):
        '''
        power sequence get the pos edge time and neg edge time of trigger signal

        Args:
            clk_freq:    int, unit Hz, the frequency of reference clock.
            ch_num:      int, the channel number of trigger.

        Returns:
            list, [value, value], list include the pos edge time and neg edge time, unit is us.

        Examples:
            power_sequence.get_interrupt_time(12500000,2)

        '''
        assert isinstance(clk_freq, int) and clk_freq > 0
        assert isinstance(ch_num, int) and ch_num > 0 and ch_num <= 64
        clk_cycle = 1000000000 / clk_freq
        self.axi4_bus.write_8bit_fix(MIXPowerSequenceSGDef.TRIGGER_CHANNEL_NUM_REGISTER, [ch_num - 1])
        pos_time = self.axi4_bus.read_32bit_fix(MIXPowerSequenceSGDef.TRIGGER_RISE_TIME_REGISTER, 1)[0] * clk_cycle
        neg_time = self.axi4_bus.read_32bit_fix(MIXPowerSequenceSGDef.TRIGGER_FALL_TIME_REGISTER, 1)[0] * clk_cycle
        return [pos_time, neg_time]
