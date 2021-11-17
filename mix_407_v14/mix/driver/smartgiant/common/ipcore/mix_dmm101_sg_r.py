# -*- coding: utf-8 -*-
import math
import time
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteSubBus
from mix.driver.smartgiant.common.utility.data_operate import DataOperate
from mix.driver.smartgiant.common.ipcore.mix_signalmeter_sg import MIXSignalMeterSG


__author__ = 'xuboyan@SmartGiant'
__version__ = '0.1'


class MIXDMM101SGRDef:
    MODULE_EN_REG = 0x2010
    CHANNEL_SELECT_REG = 0x2011
    CLK_NUMBER_CNT_REG = 0x2012
    CAPTURE_STATE_REG = 0x2013
    SAMPLE_CTRL_REG = 0x2020
    SAMPLE_DATA_REG = 0x2024
    CAPTURE_CNT_REG = 0x2028
    CAPTURE_DATA_REG = 0x202C
    REG_SIZE = 65535
    FREQ_MIN = 20000     # 20KSPS
    FREQ_MAX = 10000000  # 10MSPS

    SIGNAL_METER_OFFSET_ADDR = 0x4000
    SIGNAL_METER_REG_SIZE = 8192

    CHANNEL_SELECT_INFO = {
        'channel_en': {
            'CHA': 0x00,
            'CHAB': 0x01
        },
        'adc_clk_number': {
            'CHA': {
                '16bit': 0x08,
                '18bit': 0x09
            },
            'CHAB': {
                '16bit': 0x04,
                '18bit': 0x05
            }
        }
    }


class MIXDMM101SGRException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class MIXDMM101SGR(object):
    '''
    MIXDMM101SGR class provide function to enable, disable.

    MIXDMM101SGR can set sampling rate, select channel and return what data received.

    ClassType = MIXDMM101SGR

    Args:
        axi4_bus: instance(AXI4LiteBus)/string/None, AXI4 lite bus instance or device path.

    Examples:
        mixdmm101sgr = MIXDMM101SGR('/dev/MIX_LTC2386_SG')
        mixdmm101sgr.enable()
        mixdmm101sgr.set_sampling_rate(10000000)
        mixdmm101sgr.channel_select('CHAB', '18bit')
        volt = mixdmm101sgr.read_volt()
        print(volt)

    '''
    rpc_public_api = ['enable', 'disable', 'set_sampling_rate', 'channel_select', 'read_volt',
                      'get_continuous_sampling_voltage']

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            # create axi4lite bus from given device path
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXDMM101SGRDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self._data_deal = DataOperate()

        self.signal_meter = None
        self.sample_rate = MIXDMM101SGRDef.FREQ_MAX
        self.enable()

    def enable(self):
        '''
        MIXDMM101SGR enable function

        Examples:
            mixdmm101sgr.enable()

        '''
        self.axi4_bus.write_8bit_inc(MIXDMM101SGRDef.MODULE_EN_REG, [0x00])
        self.axi4_bus.write_8bit_inc(MIXDMM101SGRDef.MODULE_EN_REG, [0x01])

        self.signal_meter_axi4_bus = AXI4LiteSubBus(self.axi4_bus,
                                                    MIXDMM101SGRDef.SIGNAL_METER_OFFSET_ADDR,
                                                    MIXDMM101SGRDef.SIGNAL_METER_REG_SIZE)
        self.signal_meter = MIXSignalMeterSG(self.signal_meter_axi4_bus)

    def disable(self):
        '''
        MIXDMM101SGR disable function

        Examples:
            mixdmm101sgr.disable()

        '''
        self.axi4_bus.write_8bit_inc(MIXDMM101SGRDef.MODULE_EN_REG, [0x00])

    def set_sampling_rate(self, sample_rate):
        '''
        Set adc sample rate

        Args:
            sampling_rate:      int, [20000~10000000], unit SPS, ADC sample rate.

        Examples:
            mixdmm101sgr.set_sampling_rate(10000000)

        '''
        assert MIXDMM101SGRDef.FREQ_MIN <= sample_rate <= MIXDMM101SGRDef.FREQ_MAX
        self.sample_rate = sample_rate
        freq_hz_ctrl = int(self.sample_rate * math.pow(2, 32) / 125000000)
        wr_data = self._data_deal.int_2_list(freq_hz_ctrl, 4)
        self.axi4_bus.write_8bit_inc(MIXDMM101SGRDef.SAMPLE_CTRL_REG, wr_data)

    def channel_select(self, channel='CHA', adc_resolution='18bit'):
        '''
        Select adc channel

        Args:
            channel:        string, ['CHA', 'CHAB'], default 'CHA',
                            'CHA' means enable adc channel A, 'CHAB' means enable adc channel A and channel B.
            adc_resolution: string, ['16bit', '18bit'], default '18bit',
                            '16bit' means adc resolution is 16bit, '18bit' means adc resolution is 18bit.

        Examples:
            mixdmm101sgr.channel_select('CHAB', '18bit')

        '''
        channel_en = MIXDMM101SGRDef.CHANNEL_SELECT_INFO['channel_en'][channel]
        adc_clk_number = MIXDMM101SGRDef.CHANNEL_SELECT_INFO['adc_clk_number'][channel][adc_resolution]
        self.axi4_bus.write_8bit_inc(MIXDMM101SGRDef.CHANNEL_SELECT_REG, [channel_en])
        self.axi4_bus.write_8bit_inc(MIXDMM101SGRDef.CLK_NUMBER_CNT_REG, [adc_clk_number])

    def read_volt(self):
        '''
        Get sample data

        Returns:
            sample_volt: float, [-1.0~1.0], the reference voltage is not multiplied,
                                            so the return value is only a normalize volt.

        Examples:
            volt = mixdmm101sgr.read_volt()
            print(volt)

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXDMM101SGRDef.SAMPLE_DATA_REG, 4)
        sample_data = self._data_deal.list_2_int(rd_data)
        sample_volt = sample_data * 1.0 / math.pow(2, 31)
        return sample_volt

    def get_continuous_sampling_voltage(self, count):
        '''
        Get continuous sampling voltage

        Args:
            count: int, [1~2048], how many data to get.

        Returns:
            list, [value, ...], the unit of elements in the list is V, range is -1v~1v.

        Examples:
            volt_list = mixdmm101sgr.get_continuous_sampling_voltage(20)
            print(volt_list)

        '''
        assert 1 <= count <= 2048
        wait_steady_count = 10
        timeout = (1.0 / self.sample_rate) * (count + wait_steady_count)
        wr_data = self._data_deal.int_2_list(count, 2)
        self.axi4_bus.write_8bit_inc(MIXDMM101SGRDef.CAPTURE_CNT_REG, wr_data)
        self.axi4_bus.write_8bit_inc(MIXDMM101SGRDef.CAPTURE_STATE_REG, [0x00])
        self.axi4_bus.write_8bit_inc(MIXDMM101SGRDef.CAPTURE_STATE_REG, [0x01])

        start_time = time.time()
        while True:
            rd_data = self.axi4_bus.read_8bit_inc(MIXDMM101SGRDef.CAPTURE_STATE_REG, 1)
            if rd_data[0] == 0x00:
                break
            if time.time() - start_time >= timeout:
                raise MIXDMM101SGRException('capture data time out')
                break
            time.sleep(0.001)

        get_raw_data = []
        get_voltage = []
        get_raw_data = self.axi4_bus.read_32bit_fix(MIXDMM101SGRDef.CAPTURE_DATA_REG, count * 4)
        for i in range(count):
            get_raw_data_temp = self._data_deal.list_2_int(get_raw_data[i * 4:i * 4 + 4])
            get_voltage.append(get_raw_data_temp * 1.0 / math.pow(2, 31))
        return get_voltage
