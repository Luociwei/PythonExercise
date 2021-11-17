# -*- coding: utf-8 -*-
from __future__ import division
from time import sleep, time
import bisect
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.utility.data_operate import DataOperate

__author__ = 'zhuanghaite@SmartGiant'
__version__ = '0.1'


class MIXXADCSGDef:
    SOFT_RESET_REG = 0x00
    XADC_ALARM0_REG = 0x14
    XADC_ALARM1_REG = 0x15
    XADC_ALARM2_REG = 0x16
    XADC_ALARM3_REG = 0x17
    SMP_CHA_SRG_REG = 0x18
    CAPTURE_DATA_REG = 0x1c
    SAMPLE_SET_REG = 0x20

    XADC_TEMP_DATA_REG = 0x200
    XADC_VPVN_DATA_REG = 0x20c
    XADC_CONFIG0_REG = 0x300

    RESET_DATA = 0x0a
    ADC_CLK = 25000000
    CONV_CYCLE = 26
    DEFAULT_SAMPLING_RATE = 1000000
    MAX_SAMPLING_RATE = 1000000
    XADC_TIMEOUT = 3000
    FIFO_LEN = 514
    MIN_CHANNEL = 0
    MAX_CHANNEL = 64
    ALL_CHANNELS = 0xff
    REG_SIZE = 2048
    MAX_COUNT = 512
    SAMPLE_COUNT_LEVEL = [33, 129, 513, 2049, 8193]
    REFER_LEVEL = 1000.0  # mV
    ADC_RESOLUTION = 4096
    DIFFERENCE_LEVEL = 2048
    TEMP_VALUE_BIT = 0xffe0
    TEMP_REFERENCE_LEVEL = 503.975
    TEMP_OFFSET = 273.15
    MEASURE_TIME_OUT_S = 3000
    ALL_CHANNEL_SELECT = 0xfe

    BIPOLAR = 1
    UNIPOLAR = 0

    TEMPERATURE = 0
    VPVN = 3


class MIXXADCSGException(Exception):
    def __init__(self, err_str):
        self.err_reason = "MIXXADCSG {}".format(err_str)

    def __str__(self):
        return self.err_reason


class MIXXADCSG(object):
    '''
    MIXXADCSG function class, measure voltage use the interanl adc of zynq.

    measure range is 0-1V when polar is unipolar, -500mV - 500mV when polar is bipolar.

    ClassType = XADC

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string/None,  Class instance or device path of axi4 bus.

    Examples:
        xadc = MIXXADCSG('/dev/MIX_XADC_SG_0')

    '''

    rpc_public_api = ['reset', 'config', 'set_multiplex_channel', 'read_volt', 'get_temperature',
                      'enable_continuous_sampling', 'disable_continuous_sampling', 'get_continuous_sampling_voltage']

    def __init__(self, axi4_bus=None):
        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator('mix_xadc_sg_emulator', MIXXADCSGDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXXADCSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus

        self.reset()
        self.config()
        self.set_multiplex_channel(MIXXADCSGDef.MIN_CHANNEL)

    def reset(self):
        '''
        generate soft reset pulse.
        '''
        self.axi4_bus.write_8bit_fix(MIXXADCSGDef.SOFT_RESET_REG, [MIXXADCSGDef.RESET_DATA])
        # wait for the registor reset
        sleep(0.01)

    def config(self, sample_rate=MIXXADCSGDef.DEFAULT_SAMPLING_RATE, polar=MIXXADCSGDef.UNIPOLAR):
        '''
        config xadc sample rate and polar.

        Args:
            sample_rate:    int, [1~1000000],      Specific sampling rate to set.
            polar:          MIXXADCSGDef(BIPOLAR/UNIPOLAR),   Input polarity.

        Returns:
            None.

        Examples:
            xadc.config(100000,MIXXADCSGDef.UNIPOLAR)

        '''
        assert(sample_rate > 0)
        assert(sample_rate <= MIXXADCSGDef.MAX_SAMPLING_RATE)
        assert((polar == MIXXADCSGDef.UNIPOLAR) or (polar == MIXXADCSGDef.BIPOLAR))

        self.disable_continuous_sampling()
        # read one 16 bits register.
        rd_data = self.axi4_bus.read_16bit_fix(MIXXADCSGDef.XADC_CONFIG0_REG, 1)
        if polar == MIXXADCSGDef.UNIPOLAR:
            # set bit11 as 0 for reading unipolar.
            rd_data[0] &= ~(1 << 10)
        else:
            # set bit11 as 1 for reading bipolar.
            rd_data[0] |= (1 << 10)
        self.axi4_bus.write_16bit_fix(MIXXADCSGDef.XADC_CONFIG0_REG, rd_data)

        sample_cnt = int(MIXXADCSGDef.ADC_CLK / (sample_rate * MIXXADCSGDef.CONV_CYCLE))
        # find the mean count according to sample count.
        mean_count = bisect.bisect(MIXXADCSGDef.SAMPLE_COUNT_LEVEL, sample_cnt)

        wr_data = DataOperate.int_2_list(sample_cnt, 2)
        # the mean_count is start from 1, so the index need add 1.
        wr_data.append(mean_count + 1)
        wr_data.append(polar)
        self.axi4_bus.write_8bit_inc(MIXXADCSGDef.SAMPLE_SET_REG, wr_data)
        self.__adc_polar = polar
        self.__sample_rate = sample_rate

    def set_multiplex_channel(self, multiplex=0):
        '''
        set multiplex channel

        total channel is 64, it mean that enable channel 1-5 when set the multiplex = 5.

        Args:
            multiplex:    int, [0~63],  multiplex channel number.

        Returns:
            None.

        Examples:
            xadc.set_multiplex_channel(0)

        '''
        assert(multiplex >= MIXXADCSGDef.MIN_CHANNEL)
        assert(multiplex < MIXXADCSGDef.MAX_CHANNEL or multiplex == MIXXADCSGDef.ALL_CHANNELS)

        rd_data = self.axi4_bus.read_8bit_fix(MIXXADCSGDef.XADC_ALARM0_REG, 1)
        if multiplex == MIXXADCSGDef.ALL_CHANNELS:
            # enable all the channel.
            rd_data[0] &= ~(MIXXADCSGDef.ALL_CHANNEL_SELECT)
        else:
            # select specified channel,the bit3-bit8 is the channel value,
            # bit2 is if enable all the channel,bit1 is the if enable continous sampling.
            rd_data[0] = (multiplex << 2) | (1 << 1) | (rd_data[0] & 0x01)
        self.axi4_bus.write_8bit_fix(MIXXADCSGDef.XADC_ALARM0_REG, rd_data)

    def _code_to_mvolt(self, value, polar):
        '''
        translate the adc code to voltage value

        Args:
            values:   list,    adc values.
            polar:    MIXXADCSGDef(BIPOLAR/UNIPOLAR),  Input polarity.

        Returns:
            float, value, unit mV, voltage.

        '''
        # bit5-bit16 is the adc code value
        code = (value >> 4)
        # bipolar code: 0x800-0xFFF
        if polar == MIXXADCSGDef.BIPOLAR and code >= 0x800:
            code -= 0x1000

        # calculate the voltage, Volt = Code * Vref / Resolution.
        return code * MIXXADCSGDef.REFER_LEVEL / MIXXADCSGDef.ADC_RESOLUTION

    def read_volt(self):
        '''
        get xadc VPVN channel voltage.

        Returns:
            float, value, unit mV, voltage value has been read.

        Returns:
            volt = xadc.read_volt()

        '''
        self.disable_continuous_sampling()

        rd_data = self.axi4_bus.read_8bit_inc(MIXXADCSGDef.XADC_VPVN_DATA_REG, 2)
        code = rd_data[1] * 256 + rd_data[0]
        volt = self._code_to_mvolt(code, self.__adc_polar)
        return volt

    def get_temperature(self):
        '''
        get adc temperature.

        Returns:
            float, value, unit C, temperature value has been read,unit is degree C.

        Returns:
            temp = xadc.get_temperature()

        '''
        self.disable_continuous_sampling()

        rd_data = self.axi4_bus.read_16bit_fix(MIXXADCSGDef.XADC_CONFIG0_REG, 1)
        rd_data[0] = (rd_data[0] & MIXXADCSGDef.TEMP_VALUE_BIT) | MIXXADCSGDef.TEMPERATURE
        self.axi4_bus.write_16bit_fix(MIXXADCSGDef.XADC_CONFIG0_REG, rd_data)
        # wait for the registor enable
        sleep(0.001)

        data = self.axi4_bus.read_16bit_fix(MIXXADCSGDef.XADC_TEMP_DATA_REG, 1)
        rd_data[0] = (rd_data[0] & MIXXADCSGDef.TEMP_VALUE_BIT) | MIXXADCSGDef.VPVN
        self.axi4_bus.write_16bit_fix(MIXXADCSGDef.XADC_CONFIG0_REG, rd_data)
        # calculate the temperature,the temp valure is bit5-bit16.
        # Temp = Code * Vref / Resolution - Offset.
        temp = ((data[0] >> 4) * MIXXADCSGDef.TEMP_REFERENCE_LEVEL) / MIXXADCSGDef.ADC_RESOLUTION -\
            MIXXADCSGDef.TEMP_OFFSET
        return temp

    def enable_continuous_sampling(self, cycle_counts=0):
        '''
        xadc enable continuous sampling mode.

        Args:
            cycle_counts:    int, [0~63],  Number of cycles in a polling multiplex channel.

        Returns:
            None.

        Examples:
            xadc.enable_continuous_sampling()

        '''
        assert(cycle_counts >= MIXXADCSGDef.MIN_CHANNEL)
        assert(cycle_counts < MIXXADCSGDef.MAX_CHANNEL)

        rd_data = self.axi4_bus.read_8bit_fix(MIXXADCSGDef.XADC_ALARM0_REG, 1)
        # set the bit1 as 1 to enable continue mode.
        rd_data[0] |= 0x01
        self.axi4_bus.write_8bit_fix(MIXXADCSGDef.XADC_ALARM0_REG, [rd_data[0]])
        self.axi4_bus.write_8bit_fix(MIXXADCSGDef.XADC_ALARM1_REG, [cycle_counts])

    def disable_continuous_sampling(self):
        '''
        xadc disable continuous sampling mode.

        Returns:
            None.

        Examples:
            xadc.disable_continuous_sampling()

        '''
        rd_data = self.axi4_bus.read_8bit_fix(MIXXADCSGDef.XADC_ALARM0_REG, 1)
        # set the bit1 as 0 to disable continue mode.
        rd_data[0] &= ~(0x01)
        self.axi4_bus.write_8bit_fix(MIXXADCSGDef.XADC_ALARM0_REG, rd_data)

    def get_continuous_sampling_voltage(self, count, channel=0):
        '''
        xadc get specified number of voltage in continuous mode.

        Args:
            count:         int, [1~512],  Number of voltage to get.
            channel:       the xadc channel.
        Raises:
            MIXXADCSGException:    when get volt data from ADC timeout,
                                or can not get the specific channel volt.

        Returns:
            list    the float voltage value list,unit is mV.

        Examples:
            volt = xadc.get_continuous_sampling_voltage(10)

        '''
        assert(count > 0)
        assert(count <= MIXXADCSGDef.MAX_COUNT)
        assert(channel >= MIXXADCSGDef.MIN_CHANNEL)
        assert(channel < MIXXADCSGDef.MAX_CHANNEL)

        nread = 0
        datas = []
        while nread < count:
            self.axi4_bus.write_8bit_fix(MIXXADCSGDef.XADC_ALARM2_REG, [0x01])
            timeout = 0
            start_time = time()
            while timeout < MIXXADCSGDef.MEASURE_TIME_OUT_S:
                rd_data = self.axi4_bus.read_8bit_fix(MIXXADCSGDef.XADC_ALARM2_REG, 1)
                # if the bit1 is 0 mean that adc had convert ok.
                if (rd_data[0] & 0x01) == 0x00:
                    break
                else:
                    timeout = time() - start_time
                    # wait for some time to retry
                    sleep(0.01)
            if timeout >= MIXXADCSGDef.MEASURE_TIME_OUT_S:
                raise MIXXADCSGException("get voltage time out ")
            capture_list = self.axi4_bus.read_32bit_fix(MIXXADCSGDef.CAPTURE_DATA_REG, MIXXADCSGDef.FIFO_LEN)
            for x in capture_list:
                # bit9-bit14 is the adc channel of current select.
                if ((x >> 8) & 0x3f) == channel:
                    # sample_rate[1-120000] for fpga accumulative operation,need to right shift 3bit
                    # for high alignment,need to left shift 4bit
                    if self.__sample_rate > 120000:
                        code = (x >> 16) << 4
                    else:
                        code = ((x >> 16) >> 3) << 4
                    volt = self._code_to_mvolt(code, self.__adc_polar)
                    datas.append(volt)
                    nread += 1
                    if nread >= count:
                        break
            if nread == 0:
                raise MIXXADCSGException("multiplex channel:%s not set" % (self.channel))

        return datas
