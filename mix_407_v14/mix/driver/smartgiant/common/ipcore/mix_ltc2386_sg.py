# -*- coding: utf-8 -*-
import math
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.utility.data_operate import DataOperate


__author__ = 'xuboyan@SmartGiant'
__version__ = '0.1'


class MIXLTC2386SGDef:
    MODULE_EN_REG = 0x10
    CHANNEL_SELECT_REG = 0x11
    CLK_NUMBER_CNT_REG = 0x12
    SAMPLE_CTRL_REG = 0x20
    SAMPLE_DATA_REG = 0x24
    REG_SIZE = 8192
    FREQ_MIN = 20000     # 20KSPS
    FREQ_MAX = 10000000  # 10MSPS

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


class MIXLTC2386SGException(Exception):
    def __init__(self, dev_name, err_str):
        self._err_reason = '[%s]: %s.' % (dev_name, err_str)

    def __str__(self):
        return self._err_reason


class MIXLTC2386SG(object):
    '''
    MIXLTC2386SG class provide function to enable, disable.

    MIXLTC2386SG can set sampling rate, select channel and return what data received.

    ClassType = MIXLTC2386SG

    Args:
        axi4_bus: instance(AXI4LiteBus)/string/None, AXI4 lite bus instance or device path.

    Examples:
        mixltc2386sg = MIXLTC2386SG('/dev/MIX_LTC2386_SG')
        mixltc2386sg.enable()
        mixltc2386sg.set_sampling_rate(10000000)
        mixltc2386sg.channel_select('CHAB', '18bit')
        volt = mixltc2386sg.read_volt()
        print(volt)

    '''
    rpc_public_api = ['enable', 'disable', 'set_sampling_rate', 'channel_select', 'read_volt']

    def __init__(self, axi4_bus):
        if isinstance(axi4_bus, basestring):
            # create axi4lite bus from given device path
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXLTC2386SGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self._data_deal = DataOperate()

    def enable(self):
        '''
        MIXLTC2386SG enable function

        Examples:
            mixltc2386sg.enable()

        '''
        self.axi4_bus.write_8bit_inc(MIXLTC2386SGDef.MODULE_EN_REG, [0x00])
        self.axi4_bus.write_8bit_inc(MIXLTC2386SGDef.MODULE_EN_REG, [0x01])

    def disable(self):
        '''
        MIXLTC2386SG disable function

        Examples:
            mixltc2386sg.disable()

        '''
        self.axi4_bus.write_8bit_inc(MIXLTC2386SGDef.MODULE_EN_REG, [0x00])

    def set_sampling_rate(self, sample_rate):
        '''
        Set adc sample rate

        Args:
            sampling_rate:      int, [20000~10000000], unit SPS, ADC sample rate.

        Examples:
            mixltc2386sg.set_sampling_rate(10000000)

        '''
        assert MIXLTC2386SGDef.FREQ_MIN <= sample_rate <= MIXLTC2386SGDef.FREQ_MAX
        freq_hz_ctrl = int(sample_rate * math.pow(2, 32) / 125000000)
        wr_data = self._data_deal.int_2_list(freq_hz_ctrl, 4)
        self.axi4_bus.write_8bit_inc(MIXLTC2386SGDef.SAMPLE_CTRL_REG, wr_data)

    def channel_select(self, channel='CHA', adc_resolution='18bit'):
        '''
        Select adc channel

        Args:
            channel:        string, ['CHA', 'CHAB'], default 'CHA',
                            'CHA' means enable adc channel A, 'CHAB' means enable adc channel A and channel B.
            adc_resolution: string, ['16bit', '18bit'], default '18bit',
                            '16bit' means adc resolution is 16bit, '18bit' means adc resolution is 18bit.

        Examples:
            mixltc2386sg.channel_select('CHAB', '18bit')

        '''
        channel_en = MIXLTC2386SGDef.CHANNEL_SELECT_INFO['channel_en'][channel]
        adc_clk_number = MIXLTC2386SGDef.CHANNEL_SELECT_INFO['adc_clk_number'][channel][adc_resolution]
        self.axi4_bus.write_8bit_inc(MIXLTC2386SGDef.CHANNEL_SELECT_REG, [channel_en])
        self.axi4_bus.write_8bit_inc(MIXLTC2386SGDef.CLK_NUMBER_CNT_REG, [adc_clk_number])

    def read_volt(self):
        '''
        Get sample data

        Returns:
            sample_volt: float, [-1.0~1.0], the reference voltage is not multiplied,
                                            so the return value is only a normalize volt.

        Examples:
            volt = mixltc2386sg.read_volt()
            print(volt)

        '''
        rd_data = self.axi4_bus.read_8bit_inc(MIXLTC2386SGDef.SAMPLE_DATA_REG, 4)
        sample_data = self._data_deal.list_2_int(rd_data)
        sample_volt = sample_data * 1.0 / math.pow(2, 31)
        return sample_volt
