# -*- coding: utf-8 -*-
import time
import math
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.utility.data_operate import DataOperate


__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.3'


class MIXSignalMeterSGDef:

    DEFAULT_TIMEOUT = 1000
    DEFAULT_DELAY = 0.001
    CONFIG_REGISTER = 0x10
    VPP_INTERVAL_REGISTER = 0x18
    WAIT_TIME_REGISTER = 0x11
    FREQ_REGISTER = 0x14
    HP_REGISTER = 0x15
    SET_MEASURE_REGISTER = 0x13
    MEASURE_MASK_REGISTER = 0x17
    DUTY_ALL_REGISTER = 0x50
    DUTY_HIGH_REGISTER = 0x58
    DUTY_N_REGISTER = 0x60
    MAX_REGISTER = 0x70
    MIN_REGISTER = 0x78
    VPP_REGISTER = 0x80
    RMS_SQUARE_REGISTER = 0x90
    RMS_SUM_REGISTER = 0x98
    RMS_CNT_REGISTER = 0xA0
    OUTPUT_REGISTERS = 0x00
    FREQ_X_REGISTER = 0x20
    FREQ_Y_REGISTER = 0x28
    FREQ_XY_REGISTER = 0x30
    FREQ_XX_REGISTER = 0x38
    FREQ_N_REGISTER = 0x40
    REGISTER_SIZE = 1024

    MEASURE_MASK_FREQ = (1 << 4)
    MEASURE_MASK_DUTY = (1 << 5)
    MEASURE_MASK_VPP = (1 << 6)
    MEASURE_MASK_RMS = (1 << 7)
    MEASURE_LEVEL_MASK = (1 << 2)


class MIXSignalMeterSGException(Exception):

    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class MIXSignalMeterSG(object):

    '''
    mix signal meter function class to control the signal meter

    ClassType = MIXSignalMeterSG

    Args:
        axi4_bus: instance(AXI4LiteBus)/string/None,  AXI4 lite bus instance or device path;
                                                      If None, will create Emulator.

    Examples:
        signal_meter = MIXSignalMeterSG('/dev/MIX_SignalMeter_SG')

        # example for measure DC signal, disable frequency and duty measure function.
        signal_meter.start_measure(100, 1000, 0x30)
        result = signal_meter.vpp()
        # vpp value is invalid, max and min is valid
        print("vpp={}, max={}, min={}".format(result[2], result[0], result[1]))
        result = signal_meter.rms()
        print("rms={}, average={}".format(result[0], result[1]))

        # example for measure AC signal
        signal_meter.start_measure(100, 1000)
        result = signal_meter.vpp()
        print("vpp={}, max={}, min={}".format(result[2], result[0], result[1]))
        result = signal_meter.rms()
        print("rms={}, average={}".format(result[0], result[1]))
        freq = signal_meter.measure_frequency('LP')
        duty = signal_meter.duty()
        print("freq={}, duty={}".format(freq, duty))

    '''

    rpc_public_api = ['open', 'close', 'set_vpp_interval', 'enable_upframe',
                      'disable_upframe', 'start_measure', 'measure_frequency', 'level',
                      'duty', 'vpp', 'rms', 'test_register', 'measure_rising_edge_count',
                      'measure_frequency_hp', 'measure_frequency_lp']

    def __init__(self, axi4_bus=None):
        self._measure_state = 0
        self.__sample_rate = 125000000
        if isinstance(axi4_bus, basestring):
            # device path passed in; create axi4litebus here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXSignalMeterSGDef.REGISTER_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.open()

    def open(self):
        '''
        mix signal meter open

        Examples:
            self.axi4_bus.open()

        '''
        rd_conf_val = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.CONFIG_REGISTER, 1)
        config_data = (rd_conf_val[0] & ~ 0x1)
        self.axi4_bus.write_8bit_inc(
            MIXSignalMeterSGDef.CONFIG_REGISTER, [config_data])
        config_data = config_data | 0x01
        self.axi4_bus.write_8bit_inc(
            MIXSignalMeterSGDef.CONFIG_REGISTER, [config_data])
        return "done"

    def close(self):
        '''
        mix signal meter close

        Examples:
            self.axi4_bus.close()

        '''
        rd_conf_val = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.CONFIG_REGISTER, 1)[0]
        config_data = (rd_conf_val & ~ 0x1)
        self.axi4_bus.write_8bit_inc(
            MIXSignalMeterSGDef.CONFIG_REGISTER, [config_data])
        return "done"

    def set_vpp_interval(self, test_interval_ms):
        '''
        mix signal meter set the vpp interval

        Args:
            test_interval_ms:  int, [1~10000], unit ms.

        Examples:
            self.axi4_bus.set_vpp_interval(1000)

        '''
        assert isinstance(test_interval_ms, int)

        config_data = DataOperate.int_2_list(test_interval_ms, 2)
        self.axi4_bus.write_8bit_inc(
            MIXSignalMeterSGDef.VPP_INTERVAL_REGISTER, config_data)
        return "done"

    def enable_upframe(self, upframe_mode='DEBUG'):
        '''
        mix signal meter enable upframe

        Args:
            upframe_mode: string, ['DEBUG', 'BYPASS'], choose mode.

        Examples:
            self.axi4_bus.enable_upframe('DEBUG')

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.CONFIG_REGISTER, 1)
        config_data = rd_data[0] | (0x1 << 1)
        if(upframe_mode == 'BYPASS'):
            config_data = (config_data | (0x1 << 3))
        elif(upframe_mode == 'DEBUG'):
            config_data = (config_data & ~ (0x1 << 3))
        self.axi4_bus.write_8bit_inc(
            MIXSignalMeterSGDef.CONFIG_REGISTER, [config_data])
        return "done"

    def disable_upframe(self):
        '''
        mix signal meter disable upframe

        Examples:
            self.axi4_bus.disable_upframe()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.CONFIG_REGISTER, 1)
        wr_data = (rd_data[0] & ~ (0x1 << 1))
        self.axi4_bus.write_8bit_inc(
            MIXSignalMeterSGDef.CONFIG_REGISTER, [wr_data])
        return "done"

    def start_measure(self, time_ms, sample_rate, measure_mask=0x00):
        '''
        mix signal meter start measure

        Args:
            time_ms:         int, [1~2000], unit ms.
            sample_rate:     int, [1~125000000], unit SPS.
            measure_mask:    int, [1~0xff], bit set means mask the function.

        Examples:
            self.axi4_bus.start_measure(2000, 150000)

        +---------------+-------------------+
        | measure_mask  |       function    |
        +===============+===================+
        | bit[0:3]      | Reserved          |
        +---------------+-------------------+
        | bit[4]        | Frequency mask    |
        +---------------+-------------------+
        | bit[5]        | Duty mask         |
        +---------------+-------------------+
        | bit[6]        | Vpp mask          |
        +---------------+-------------------+
        | bit[7]        | rms mask          |
        +---------------+-------------------+

        '''
        assert isinstance(time_ms, int)
        assert isinstance(sample_rate, int)
        assert 1 <= sample_rate <= 125000000

        self.axi4_bus.write_8bit_inc(MIXSignalMeterSGDef.MEASURE_MASK_REGISTER, [measure_mask])

        self.__sample_rate = sample_rate
        # fpga count the time from 0, need to minus 1
        wr_data = DataOperate.int_2_list(time_ms - 1, 2)
        self.axi4_bus.write_8bit_inc(
            MIXSignalMeterSGDef.WAIT_TIME_REGISTER, wr_data)
        self.axi4_bus.write_8bit_inc(MIXSignalMeterSGDef.FREQ_REGISTER, [0x00])
        self.axi4_bus.write_8bit_inc(
            MIXSignalMeterSGDef.SET_MEASURE_REGISTER, [0x01])
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.FREQ_REGISTER, 1)

        last_time = time.time()
        # time.time() unit needs to be converted to ms
        while ((rd_data[0] != 0x01) and
               ((time.time() - last_time) * 1000 < (time_ms + MIXSignalMeterSGDef.DEFAULT_TIMEOUT))):
            time.sleep(MIXSignalMeterSGDef.DEFAULT_DELAY)
            rd_data = self.axi4_bus.read_8bit_inc(
                MIXSignalMeterSGDef.FREQ_REGISTER, 1)

        if((time.time() - last_time) * 1000 >= (time_ms + MIXSignalMeterSGDef.DEFAULT_TIMEOUT)):
            raise MIXSignalMeterSGException('SignalMeter Measure time out')
            self._measure_state = 0
        self._measure_state = 1
        return "done"

    def measure_frequency(self, measure_type):
        '''
        mix signal meter measure frequency

        Args:
            measure_type:  string, ['HP', 'LP'], type of measure.

        Returns:
            int, value, unit Hz.

        Examples:
            frequency = self.axi4_bus.measure_frequency('HP')
            frequency = 1000

        '''
        if(self._measure_state == 0):
            return 0
        if(measure_type == 'HP'):
            freq = self.measure_frequency_hp()
        elif(measure_type == 'LP'):
            freq = self.measure_frequency_lp()
        else:
            raise MIXSignalMeterSGException('SignalMeter Measure type error')
        return freq

    def level(self):
        '''
        mix signal meter get current voltage level.

        Returns:
            int, [0, 1],  0 for low level, 1 for high level.

        '''
        value = self.axi4_bus.read_8bit_inc(MIXSignalMeterSGDef.CONFIG_REGISTER, 1)[0]
        return 1 if (value & MIXSignalMeterSGDef.MEASURE_LEVEL_MASK) else 0

    def duty(self):
        '''
        mix signal meter measure duty

        Returns:
            float, [0~100].

        Examples:
            duty = self.axi4_bus.duty
            duty = 10

        '''
        if(self._measure_state == 0):
            rd_data = self.axi4_bus.read_8bit_inc(
                MIXSignalMeterSGDef.CONFIG_REGISTER, 1)
            if(rd_data[0] & 0x04 == 0x04):
                return(100, '%')
            else:
                return(0, '%')
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.DUTY_ALL_REGISTER, 8)
        duty_all = DataOperate.list_2_uint(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.DUTY_HIGH_REGISTER, 8)
        duty_high = DataOperate.list_2_uint(rd_data)

        duty = (float(duty_high) / duty_all) * 100
        return duty

    def vpp(self):
        '''
        mix signal meter measure vpp

        Returns:
            list,  include vpp_data(0 ~ +2), max_data(-1 ~ +1), min_data(-1 ~ +1).

        Examples:
            result = self.axi4_bus.vpp
            result is list

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.MAX_REGISTER, 8)
        vpp_max = DataOperate.list_2_int(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.MIN_REGISTER, 8)
        vpp_min = DataOperate.list_2_int(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.VPP_REGISTER, 4)
        vpp_cnt = DataOperate.list_2_int(rd_data)
        max = float(vpp_max) / (float(vpp_cnt) * pow(2, 15))
        min = float(vpp_min) / (float(vpp_cnt) * pow(2, 15))
        vpp = max - min
        return [max, min, vpp]

    def rms(self):
        '''
        mix signal meter measure rms

        Returns:
            list,  include rms_data(0 ~ +1), avg_data(-1 ~ +1).

        Examples:
            result = self.axi4_bus.rms
            result is list

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.RMS_SQUARE_REGISTER, 8)
        rms_square_sum = DataOperate.list_2_int(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.RMS_SUM_REGISTER, 8)
        rms_sum = DataOperate.list_2_int(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.RMS_CNT_REGISTER, 4)
        rms_cnt = DataOperate.list_2_int(rd_data)
        rms = math.sqrt(rms_square_sum / rms_cnt) / pow(2, 15)
        avg = (float(rms_sum) / rms_cnt) / pow(2, 15)
        return [rms, avg]

    def test_register(self, test_data):
        '''
        mix signal meter test register

        Args:
            test_data:  int, [0x23], test data.

        Examples:
            self.test_register(0x23)

        '''
        wr_data = DataOperate.int_2_list(test_data, 4)
        self.axi4_bus.write_8bit_inc(
            MIXSignalMeterSGDef.OUTPUT_REGISTERS, wr_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.OUTPUT_REGISTERS, len(wr_data))
        test_out = DataOperate.list_2_int(rd_data)
        if(test_out != test_data):
            raise MIXSignalMeterSGException(
                'SignalMeter Test Register read data error')

    def measure_frequency_hp(self):
        '''
        mix signal meter measure frequency in high-precision

        Returns:
            float, value, unit Hz.

        Examples:
            self.measure_frequency_hp()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXSignalMeterSGDef.HP_REGISTER, 2)
        sys_divide = DataOperate.list_2_uint(rd_data)
        if(sys_divide == 0):
            sys_divide = 1
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.FREQ_X_REGISTER, 8)
        freq_x_sum = DataOperate.list_2_uint(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.FREQ_Y_REGISTER, 8)
        freq_y_sum = DataOperate.list_2_uint(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.FREQ_XY_REGISTER, 8)
        freq_xy_sum = DataOperate.list_2_uint(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.FREQ_XX_REGISTER, 8)
        freq_xx_sum = DataOperate.list_2_uint(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.FREQ_N_REGISTER, 4)
        freq_N = DataOperate.list_2_uint(rd_data)
        k_1 = freq_N * freq_xy_sum - freq_y_sum * freq_x_sum
        k_2 = freq_N * freq_xx_sum - freq_x_sum * freq_x_sum
        freq = float(sys_divide) * self.__sample_rate * k_2 / k_1
        return freq

    def measure_frequency_lp(self):
        '''
        mix signal meter measure frequency in low-precision

        Returns:
            float, value, unit Hz.

        Examples:
            self.measure_frequency_lp()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.DUTY_ALL_REGISTER, 8)
        duty_all = DataOperate.list_2_uint(rd_data)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.DUTY_N_REGISTER, 4)
        duty_N = DataOperate.list_2_uint(rd_data)
        freq = float(duty_N) * self.__sample_rate / duty_all
        return freq

    def measure_rising_edge_count(self):
        '''
        mix signal meter measure rising edge count in low-precision
        if want to get accurate count, measure time must minus 1.

        Returns:
            int, value.

        Examples:
            self.measure_rising_edge_count()

        '''
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXSignalMeterSGDef.DUTY_N_REGISTER, 4)
        return DataOperate.list_2_uint(rd_data)
