# -*- coding: utf-8 -*-
import time
import math
from collections import OrderedDict
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.bus.pin import Pin
from mix.driver.smartgiant.common.ic.ad9106 import AD9106
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.ipcore.mix_bt001_sg_r import MIXBT001SGR


__author__ = 'tufeng.mao@SmartGiant'
__version__ = 'V0.0.3'


karma_range_table = {
    '300mohm_Ix_ch1': 0,
    '300mohm_Ix_ch2': 1,
    '300mohm_Vx_ch1': 2,
    '300mohm_Vx_ch2': 3,
    '3000mohm_Ix_ch1': 4,
    '3000mohm_Ix_ch2': 5,
    '3000mohm_Vx_ch1': 6,
    '3000mohm_Vx_ch2': 7,
    '300mohm': 8,
    '3000mohm': 9
}


class KarmaDef:
    ADC_VREF = 2000  # mV
    AD9106_MCLK = 1000000.0  # Hz
    AD9106_DEFAULT_VREF = 1040  # mV
    IOUT_DEFAULT_VPP = 1977.0  # mVpp
    REG_SIZE = 65536

    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48

    VX_IX_SELECT_PIN = 10
    CUR_SET1_PIN = 12
    CUR_SET2_PIN = 16
    DISCHARGE_PIN = 13
    LPF_SELECT_PIN = 11
    RESET_L_PIN = 14
    TRIGGER_L_PIN = 15
    IO_OUTPUT_DIR = 'output'
    BIT1_VX_IX_SELECT = 'self.vx_ix_select_pin'
    BIT2_CUR_SET1 = 'self.cur_set1_pin'
    BIT3_CUR_SET2 = 'self.cur_set2_pin'
    BIT4_DISCHARGE = 'self.discharge_pin'
    BIT5_LPF_SELECT = 'self.lpf_select_pin'

    ADC_CHANNEL_LIST = (0, 1)
    RANGE_LIST = ('3000mohm', '300mohm')
    FREQ_LIST = ('1kHz', '1Hz')
    CHANNEL_LIST = ('Vx', 'Ix')

    COSINE_PHASE = math.pi / 2
    ADC_DEFAULT_SAMPLE_RATE = 5  # SPS
    DISCHARGE_DEFAULT_TIME = 20  # ms
    CLOSE_DEFAULT_TIME = 0  # ms
    RST_DELAY_MS = 1  # ms
    RELAY_DELAY_MS = 5  # ms
    DEFAULT_TIMEOUT = 6  # s
    AD9106_SAMPLE_RATE = 1000000
    AD9106_SRAM_SINE_START_ADDR = 0x000
    AD9106_SRAM_SINE_ADDR = 0x6000
    AD9106_SRAM_COSINE_START_ADDR = 0x800
    AD9106_SRAM_COSINE_ADDR = 0x6800

    calculation_formula = {
        'calculate_negative_data':
            lambda value: (pow(2, 12) - 1) + (value / KarmaDef.AD9106_DEFAULT_VREF * (pow(2, 11) - 1)) + 1,
        'calculate_positive_data':
            lambda value: value / KarmaDef.AD9106_DEFAULT_VREF * (pow(2, 11) - 1),
    }


CAL_OFFSET_RANGE_1Hz = OrderedDict([
    ('1Hz_300mohm_Ix_ch1', None),
    ('1Hz_300mohm_Ix_ch2', None),
    ('1Hz_300mohm_Vx_ch1', None),
    ('1Hz_300mohm_Vx_ch2', None),
    ('1Hz_3000mohm_Ix_ch1', None),
    ('1Hz_3000mohm_Ix_ch2', None),
    ('1Hz_3000mohm_Vx_ch1', None),
    ('1Hz_3000mohm_Vx_ch2', None)
])

CAL_OFFSET_RANGE_1kHz = OrderedDict([
    ('1kHz_300mohm_Ix_ch1', None),
    ('1kHz_300mohm_Ix_ch2', None),
    ('1kHz_300mohm_Vx_ch1', None),
    ('1kHz_300mohm_Vx_ch2', None),
    ('1kHz_3000mohm_Ix_ch1', None),
    ('1kHz_3000mohm_Ix_ch2', None),
    ('1kHz_3000mohm_Vx_ch1', None),
    ('1kHz_3000mohm_Vx_ch2', None)
])

# range define
karma_line_info = {
    '3000mohm': {
        'bits': [(KarmaDef.BIT2_CUR_SET1, 0), (KarmaDef.BIT3_CUR_SET2, 0)]
    },

    '300mohm': {
        'bits': [(KarmaDef.BIT2_CUR_SET1, 1), (KarmaDef.BIT3_CUR_SET2, 1)]
    },

    '1kHz': {
        'bits': [(KarmaDef.BIT5_LPF_SELECT, 0)]
    },

    '1Hz': {
        'bits': [(KarmaDef.BIT5_LPF_SELECT, 1)]
    },

    'Vx': {
        'bits': [(KarmaDef.BIT1_VX_IX_SELECT, 1)]
    },

    'Ix': {
        'bits': [(KarmaDef.BIT1_VX_IX_SELECT, 0)]
    },

    'open': {
        'bits': [[(KarmaDef.BIT1_VX_IX_SELECT, 0), (KarmaDef.BIT5_LPF_SELECT, 0), (KarmaDef.BIT2_CUR_SET1, 0)],
                 (KarmaDef.BIT3_CUR_SET2, 0),
                 (KarmaDef.BIT4_DISCHARGE, 1)]
    },

    'close': {
        'bits': [[(KarmaDef.BIT1_VX_IX_SELECT, 0), (KarmaDef.BIT5_LPF_SELECT, 0), (KarmaDef.BIT2_CUR_SET1, 0)],
                 (KarmaDef.BIT3_CUR_SET2, 0),
                 (KarmaDef.BIT4_DISCHARGE, 0)]
    }

}


class KarmaException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class KarmaBase(SGModuleDriver):
    '''
    Base class of Karma and KarmaCompatible.

    Providing common Karma methods.

    Args:
        i2c:        instance(I2C), instance of I2CBus, which is used to control cat24c32 and nct75.
        ipcore:     instance(MIXBT001SGR)/string, If given, then use MIXBT001SGR's AD7175, MIXQSPI, MIXGPIO.
        eeprom_dev_addr:    int, eeprom device address.
        sensor_dev_addr:    int, NCT75 device address.
        range_table:        dict, which is ICI calibration range table.

    '''

    rpc_public_api = ['dds_reset', 'dds_control', 'discharge_control',
                      'set_line_path', 'get_line_path', 'get_offset_cal_data',
                      'sine_output', 'resistance_measure', 'read_adc_voltage',
                      'set_sampling_rate', 'get_sampling_rate'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, ipcore,
                 eeprom_dev_addr=KarmaDef.EEPROM_DEV_ADDR,
                 sensor_dev_addr=KarmaDef.SENSOR_DEV_ADDR,
                 range_table=karma_range_table):

        if (i2c and ipcore):
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, KarmaDef.REG_SIZE)
                self.ipcore = MIXBT001SGR(axi4_bus=axi4_bus, ad717x_chip='AD7175',
                                          ad717x_mvref=KarmaDef.ADC_VREF,
                                          use_spi=True, use_gpio=True)
            else:
                self.ipcore = ipcore

            self.ad7175 = self.ipcore.ad717x
            self.ad7175.config = {
                'ch0': {'P': 'AIN0', 'N': 'AIN1'},
                'ch1': {'P': 'AIN2', 'N': 'AIN3'}
            }
            self.vx_ix_select_pin = Pin(self.ipcore.gpio, KarmaDef.VX_IX_SELECT_PIN)
            self.cur_set1_pin = Pin(self.ipcore.gpio, KarmaDef.CUR_SET1_PIN)
            self.cur_set2_pin = Pin(self.ipcore.gpio, KarmaDef.CUR_SET2_PIN)
            self.discharge_pin = Pin(self.ipcore.gpio, KarmaDef.DISCHARGE_PIN)
            self.lpf_select_pin = Pin(self.ipcore.gpio, KarmaDef.LPF_SELECT_PIN)
            self.reset_l_pin = Pin(self.ipcore.gpio, KarmaDef.RESET_L_PIN)
            self.trigger_l_pin = Pin(self.ipcore.gpio, KarmaDef.TRIGGER_L_PIN)
            self.ad9106 = AD9106(self.ipcore.spi, KarmaDef.AD9106_MCLK, KarmaDef.AD9106_DEFAULT_VREF)
            self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
            self.sensor = NCT75(sensor_dev_addr, i2c)
            self.line_path = ""
            self.sine_data_length = 0
            self.cosine_data_length = 0
            self.cycle_count = 2
            super(KarmaBase, self).__init__(self.eeprom, self.sensor, range_table=range_table)

        else:
            raise KarmaException('Parameter error')

    def post_power_on_init(self, timeout=KarmaDef.DEFAULT_TIMEOUT):
        '''
        Init Karma module to a know harware state.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def pre_power_down(self, timeout=KarmaDef.DEFAULT_TIMEOUT):
        '''
        Put the hardware in a safe state to be powered down.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.
        '''
        start_time = time.time()

        while True:
            try:
                self.discharge_control('open', KarmaDef.DISCHARGE_DEFAULT_TIME)
                self.discharge_control('close')
                self.dds_reset()
                self.dds_control('close')
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise KarmaException("Timeout: {}".format(e.message))

    def reset(self, timeout=KarmaDef.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 6, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                self.vx_ix_select_pin.set_dir(KarmaDef.IO_OUTPUT_DIR)
                self.cur_set1_pin.set_dir(KarmaDef.IO_OUTPUT_DIR)
                self.cur_set2_pin.set_dir(KarmaDef.IO_OUTPUT_DIR)
                self.discharge_pin.set_dir(KarmaDef.IO_OUTPUT_DIR)
                self.lpf_select_pin.set_dir(KarmaDef.IO_OUTPUT_DIR)
                self.reset_l_pin.set_dir(KarmaDef.IO_OUTPUT_DIR)
                self.trigger_l_pin.set_dir(KarmaDef.IO_OUTPUT_DIR)
                self.discharge_control('open', KarmaDef.DISCHARGE_DEFAULT_TIME)
                self.discharge_control('close')
                self.dds_reset()
                self.dds_control('close')
                self.ad9106.set_ref_voltage(KarmaDef.AD9106_DEFAULT_VREF)
                self.ad7175.channel_init()
                self.set_sampling_rate(0, KarmaDef.ADC_DEFAULT_SAMPLE_RATE)
                self.set_sampling_rate(1, KarmaDef.ADC_DEFAULT_SAMPLE_RATE)
                self.write_sine_pattern(1000, KarmaDef.IOUT_DEFAULT_VPP, self.cycle_count)
                self.write_cosine_pattern(1000, KarmaDef.IOUT_DEFAULT_VPP, self.cycle_count)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise KarmaException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def dds_reset(self):
        '''
        Karma reset ad9106. This is private function.

        Returns:
            string, "done", api execution successful.

        Examples:
            karma.dds_reset()

        '''
        self.reset_l_pin.set_level(0)
        time.sleep(KarmaDef.RST_DELAY_MS / 1000.0)
        self.reset_l_pin.set_level(1)

        return "done"

    def dds_control(self, mode):
        '''
        Pattern trigger input of ad9106. This is private function.

        Args:
            mode:    string, ['open', 'close'], 'open' mean enable pattern trigger input of ad9106,
                                                'close' mean disable pattern trigger input of ad9106.

        Returns:
            string, "done", api execution successful.

        Examples:
            karma.dds_control('open')

        '''
        assert mode in ['open', 'close']

        if mode == 'open':
            self.trigger_l_pin.set_level(0)
        else:
            self.trigger_l_pin.set_level(1)

        return "done"

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        Karma set sampling rate. This is private function.

        Args:
            channel:           int, [0, 1], channel 0 is for the real part of Vx or Ix,
                                            channel 1 is for the imaginary part of Vx or Ix.
            sampling_rate:     float, [5~250000], adc measure sampling rate, which not continuouse,
                                                  please refer ad7175 datasheet.

        Returns:
            string, "done", api execution successful.

        Examples:
           karma.set_sampling_rate(1, 10000)

        '''
        assert channel in KarmaDef.ADC_CHANNEL_LIST
        assert 5 <= sampling_rate <= 250000

        if sampling_rate != self.get_sampling_rate(channel):
            self.ad7175.set_sampling_rate(channel, sampling_rate)

        return "done"

    def get_sampling_rate(self, channel):
        '''
        Karma get sampling rate of adc. This is private function.

        Args:
            channel:     int, [0, 1], channel 0 is for the real part of Vx or Ix,
                                      channel 1 is for the imaginary part of Vx or Ix.

        Returns:
            string, "done", api execution successful.

        Examples:
            sampling_rate = karma.get_sampling_rate(1)
            print(sampling_rate)

        '''
        assert channel in KarmaDef.ADC_CHANNEL_LIST

        return self.ad7175.get_sampling_rate(channel)

    def discharge_control(self, mode, discharge_time=KarmaDef.CLOSE_DEFAULT_TIME):
        '''
        Discharge control. This is private function.

        Args:
            mode:    string, ['open', 'close'], 'open' mean discharge,
                                                     'close' mean charge.
            discharge_time:    float, (>=0), default 0, unit ms, discharge time.

        Returns:
            string, "done", api execution successful.

        Examples:
            karma.discharge_control('open', 20)

        '''
        assert mode in ['open', 'close']

        bits = karma_line_info[mode]['bits']
        for bit in bits:
            if isinstance(bit, list):
                for io_conf in bit:
                    eval(io_conf[0]).set_level(io_conf[1])
                time.sleep(KarmaDef.RST_DELAY_MS / 1000.0)
            else:
                eval(bit[0]).set_level(bit[1])
        time.sleep(discharge_time / 1000.0)
        self.line_path = mode

        return "done"

    def set_line_path(self, channel, scope, freq, delay_time=KarmaDef.RELAY_DELAY_MS):
        '''
        Karma set channel path. This is debug function.

        Args:
            channel:     string, ['Vx', 'Ix'], channel 'Vx' mean the vector voltage of the real part or
                                               the imaginary part of impedance,
                                               channel 'Ix' mean the vector current of the real part or
                                               the imaginary part of impedance.
            scope:       string, ['3000mohm', '300mohm'], impedance measurement range.
            freq:        string, ['1kHz', '1Hz'], impedance measurement frequency.
            delay_time:  int, (>0), default 5, unit ms.

        Returns:
            string, "done", api execution successful.

        Examples:
            karma.set_line_path('Vx', '3000mohm', '1kHz')

        '''
        assert channel in KarmaDef.CHANNEL_LIST
        assert scope in KarmaDef.RANGE_LIST
        assert freq in KarmaDef.FREQ_LIST

        line_path = freq + '_' + scope + '_' + channel
        if line_path != self.line_path:
            bits = karma_line_info[channel]['bits']
            for bit in bits:
                eval(bit[0]).set_level(bit[1])

            bits = karma_line_info[freq]['bits']
            for bit in bits:
                eval(bit[0]).set_level(bit[1])

            bits = karma_line_info[scope]['bits']
            for bit in bits:
                eval(bit[0]).set_level(bit[1])
                time.sleep(delay_time / 1000.0)

            self.line_path = line_path

        return "done"

    def get_line_path(self):
        '''
        Karma get channel path.

        Returns:
            string, value is channel path.

        Examples:
            path = karma.get_line_path()
            print(path)

        '''
        return self.line_path

    def sine_output(self, dac_channel, freq, vpp, offset=0, phase_value=0):
        '''
        AD9106 output sine waveform, this is a private function.

        Args:
            dac_channel:     int, [1, 2, 3], channel for dds output.
            freq:            int, unit Hz, frequency of wavefrom.
            vpp:             float, unit mVpp, vpp of waveform.
            offset:          float, unit mV, default 0, offset of waveform.
            phase_value:     float, (>=0), default 0, phase of waveform.

        Returns:
            string, "done", api execution successful.

        Examples:
            karma.sine_output(0, 1000, 500)

        '''
        assert dac_channel in [1, 2, 3]
        assert 0 <= phase_value

        # IOUTFSx = 32 * VREFIO / xRSET = 32 * VREFIO / 8060, VOUTFS = IOUTFS x Rl = IOUTFS * 249
        vp = 32 * KarmaDef.AD9106_DEFAULT_VREF * 249 / 8060.0
        gain = vpp / (vp * 2)
        self.ad9106.set_phase(dac_channel, phase_value)
        self.ad9106.sine_output(dac_channel, freq, gain, offset)
        return "done"

    def write_sine_pattern(self, freq, vpp, cycle_count=1):
        '''
        Write sine wave data to SRAM.

        Args:
            freq: int/float, unit Hz, frequency value.
            vpp: int/float, unit mVpp, vpp value.
            cycle_count, int/float, (>0), default 1, the number of waveform cycles in SRAM.

        Returns:
            string, "done", api execution successful.

        Examples:
            karma.write_sine_pattern(1000, 1977, 4)

        '''
        sine_data_list = self.calculate_sine_data(freq, vpp)
        sine_data_list = sine_data_list * cycle_count
        if len(sine_data_list) > 4096:
            raise KarmaException("Out of range of per pattern_period")
        self.ad9106.write_pattern(KarmaDef.AD9106_SRAM_SINE_ADDR, sine_data_list)
        self.sine_data_length = len(sine_data_list)

        return "done"

    def calculate_sine_data(self, freq, vpp):
        '''
        Calculate sine data.

        Args:
            freq: int/float, unit Hz, frequency value.
            vpp: int/float, unit mVpp, vpp value.

        Returns:
            list, sine wave data.

        Examples:
            karma.calculate_sine_data(1000, 1977)

        '''

        data_list = list()
        vp = vpp / 2
        freq = freq * 1.0
        total_points = int(KarmaDef.AD9106_SAMPLE_RATE / freq)
        for i in range(total_points):
            point_vp = math.sin(2 * math.pi * (i / (total_points * 1.0))) * vp
            if(point_vp < 0):
                if point_vp < -KarmaDef.AD9106_DEFAULT_VREF:
                    point_vp = -KarmaDef.AD9106_DEFAULT_VREF
                result = int(KarmaDef.calculation_formula['calculate_negative_data'](point_vp)) & 0xfff
            else:
                if point_vp > KarmaDef.AD9106_DEFAULT_VREF:
                    point_vp = KarmaDef.AD9106_DEFAULT_VREF
                result = int(KarmaDef.calculation_formula['calculate_positive_data'](point_vp)) & 0xfff
            data_list.append(result)

        return data_list

    def write_cosine_pattern(self, freq, vpp, cycle_count=1):
        '''
        Write cosine wave data to SRAM.

        Args:
            freq: int/float, unit Hz, frequency value.
            vpp: int/float, unit mVpp, vpp value.
            cycle_count, int/float, (>0), default 1, the number of waveform cycles in SRAM.

        Returns:
            string, "done", api execution successful.

        Examples:
            karma.write_cosine_pattern(1000, 1977, 4)

        '''
        cosine_data_list = self.calculate_cosine_data(freq, vpp)
        cosine_data_list = cosine_data_list * cycle_count
        if len(cosine_data_list) > 4096:
            raise KarmaException("Out of range of per pattern_period")
        self.ad9106.write_pattern(KarmaDef.AD9106_SRAM_COSINE_ADDR, cosine_data_list)
        self.cosine_data_length = len(cosine_data_list)

        return "done"

    def calculate_cosine_data(self, freq, vpp):
        '''
        Calculate cosine data.

        Args:
            freq: int/float, unit Hz, frequency value.
            vpp: int/float, unit mVpp, vpp value.

        Returns:
            list, cosine wave data.

        Examples:
            karma.calculate_cosine_data(1000, 1977)

        '''

        data_list = list()
        vp = vpp / 2
        freq = freq * 1.0
        total_points = int(KarmaDef.AD9106_SAMPLE_RATE / freq)
        for i in range(total_points):
            point_vp = math.cos(2 * math.pi * (i / (total_points * 1.0))) * vp
            if(point_vp < 0):
                if point_vp < -KarmaDef.AD9106_DEFAULT_VREF:
                    point_vp = -KarmaDef.AD9106_DEFAULT_VREF
                result = int(KarmaDef.calculation_formula['calculate_negative_data'](point_vp)) & 0xfff
            else:
                if point_vp > KarmaDef.AD9106_DEFAULT_VREF:
                    point_vp = KarmaDef.AD9106_DEFAULT_VREF
                result = int(KarmaDef.calculation_formula['calculate_positive_data'](point_vp)) & 0xfff
            data_list.append(result)

        return data_list

    def output_sine_pattern(self, freq, vpp, cycle_count, pat_period_base=1, dac_repeat_cycle=255):
        '''
        Output sine wave in pattern period.

        Args:
            freq: int/float, unit Hz, frequency value, it is related to the clock of DAC.
            vpp:    float, unit mVpp, vpp of waveform.
            cycle_count: int/float, (>0), the number of waveform cycles in per pattern_period.
            pat_period_base: int, [0-0xf], default 1, the number of dac clock periods per pattern_period lsb.
            dac_repeat_cycle:    int, [0-255], default 1, Number of DAC pattern repeat cycles + 1,
                                                (0 means repeat 1 pattern).

        Returns:
            string, "done", api execution successful.

        Examples:
            karma.write_sine_pattern(1000, 1977, 4)
            karma.output_sine_pattern(1000, 1977, 4)
        '''
        self.dds_control('close')
        # IOUTFSx = 32 * VREFIO / xRSET = 32 * VREFIO / 8060, VOUTFS = IOUTFS x Rl = IOUTFS * 249
        vp = 32 * KarmaDef.AD9106_DEFAULT_VREF * 249 / 8060.0
        gain = vpp / (vp * 2)
        self.ad9106.play_pattern(1, freq, KarmaDef.AD9106_SRAM_SINE_START_ADDR, self.sine_data_length - 1,
                                 pat_period_base=pat_period_base, dac_repeat_cycle=dac_repeat_cycle,
                                 cycle_value=cycle_count, gain=gain)
        self.ad9106.play_pattern(2, freq, KarmaDef.AD9106_SRAM_COSINE_START_ADDR, self.cosine_data_length - 1,
                                 pat_period_base=pat_period_base, dac_repeat_cycle=dac_repeat_cycle,
                                 cycle_value=cycle_count, gain=gain)
        self.ad9106.play_pattern(3, freq, KarmaDef.AD9106_SRAM_SINE_START_ADDR, self.sine_data_length - 1,
                                 pat_period_base=pat_period_base, dac_repeat_cycle=dac_repeat_cycle,
                                 cycle_value=cycle_count, gain=gain)
        self.ad9106.set_ram_update()
        self.dds_control('open')

        return "done"

    def resistance_measure(self, scope, freq, discharge_time=KarmaDef.DISCHARGE_DEFAULT_TIME,
                           delay_time=KarmaDef.RELAY_DELAY_MS):
        '''
        Karma measure impedance.

        Please notes that the hardware does not support 1Hz measurement temporarily.

        Args:
            scope:    string, ['3000mohm', '300mohm'], impedance measurement range.
            freq:     string, ['1kHz', '1Hz'], impedance measurement frequency,
                                            the hardware does not support '1Hz' measurement temporarily.
            discharge_time:    float, (>=20), default 20, unit ms, discharge time.
            delay_time:    int, (>0), default 5, unit ms.

        Returns:
            dict, {'Rs': (Rs, 'ohm'), 'Xs': (Xs, 'ohm')}, for the real part and imaginary part of impedance.

        Examples:
            result = karma.resistance_measure('3000mohm', '1kHz', 20)
            print(result)

        '''
        assert scope in KarmaDef.RANGE_LIST
        assert freq in KarmaDef.FREQ_LIST
        assert 20 <= discharge_time

        sine_freq_dict = {'1kHz': 1000, '1Hz': 1}
        sine_freq = sine_freq_dict[freq]
        r_sense_dict = {'3000mohm': 200, '300mohm': 20}
        r_sense = r_sense_dict[scope]
        self.discharge_control('close')
        if freq == '1kHz':
            self.output_sine_pattern(sine_freq, KarmaDef.IOUT_DEFAULT_VPP, self.cycle_count)
        else:
            raise KarmaException("Hardware does not support 1Hz measurement temporarily")
        self.set_line_path('Ix', scope, freq, delay_time)
        u_re = self.ad7175.read_volt(0)
        u_im = self.ad7175.read_volt(1)
        u_re = self.calibrate(scope + '_Ix_ch1', u_re, sine_freq)
        u_im = self.calibrate(scope + '_Ix_ch2', u_im, sine_freq)
        self.set_line_path('Vx', scope, freq, delay_time)
        self.output_sine_pattern(sine_freq, KarmaDef.IOUT_DEFAULT_VPP, self.cycle_count)
        v_re = self.ad7175.read_volt(0)
        v_im = self.ad7175.read_volt(1)
        v_re = self.calibrate(scope + '_Vx_ch1', v_re, sine_freq)
        v_im = self.calibrate(scope + '_Vx_ch2', v_im, sine_freq)
        self.discharge_control('open', discharge_time)
        self.discharge_control('close')

        result = dict()
        unit = 'ohm'
        r_s = -(((v_re * u_re) + (v_im * u_im)) * r_sense / ((u_re ** 2 + u_im ** 2) * 65.0))
        x_s = -(((v_im * u_re) - (v_re * u_im)) * r_sense / ((u_re ** 2 + u_im ** 2) * 65.0))
        r_s = self.calibrate(scope, r_s)
        result['Rs'] = (r_s, unit)
        result['Xs'] = (x_s, unit)

        return result

    def read_adc_voltage(self, channel):
        '''
        Read adc voltage, this is a debug function.

        Args:
            channel:    int, [0, 1]. adc channel.

        Returns:
            float, unit is mV.

        Examples:
            result = karma.read_adc_voltage(0)
            print(result)

        '''
        assert channel in KarmaDef.ADC_CHANNEL_LIST
        return self.ad7175.read_volt(channel)

    def get_offset_cal_data(self, frequency):
        '''
        Get offset calibration data, this is a debug function.

        Args:
            frequency:    string, ['1kHz', '1Hz'], frequency.

        Returns:
            dict,
            e.g. {'1kHz_300mohm_Vx_ch1': 37.65133247681454,
                  '1Hz_300mohm_Ix_ch1': 13.997853636613705,
                  '1kHz_300mohm_Ix_ch2': 43.30072065000062,
                  '1kHz_300mohm_Vx_ch2': 43.32542677673262,
                  '1Hz_3000mohm_Ix_ch2': 12.980402289652961,
                  '1kHz_300mohm_Ix_ch1': 37.70277128832169,
                  '1Hz_300mohm_Ix_ch2': 13.53880843751481,
                  '1Hz_3000mohm_Ix_ch1': 13.895274036841037,
                  '1Hz_300mohm_Vx_ch2': 20.317376870952657,
                  '1Hz_3000mohm_Vx_ch2': 28.178902159863846,
                  '1kHz_3000mohm_Vx_ch1': 37.72822247315779,
                  '1kHz_3000mohm_Vx_ch2': 43.30441613819696,
                  '1Hz_3000mohm_Vx_ch1': 27.222545577439405,
                  '1kHz_3000mohm_Ix_ch2': 43.30870767287659,
                  '1Hz_300mohm_Vx_ch1': 27.315230805589607,
                  '1kHz_3000mohm_Ix_ch1': 37.71659956673381}.

        Examples:
            result = karma.get_offset_cal_data()
            print(result)

        '''
        assert frequency in KarmaDef.FREQ_LIST

        cal_offset = OrderedDict()
        adc_channel_dict = {'ch1': 0, 'ch2': 1}
        sine_freq_dict = {'1kHz': 1000, '1Hz': 1}
        if frequency == '1Hz':
            CAL_OFFSET_RANGE = CAL_OFFSET_RANGE_1Hz
        else:
            CAL_OFFSET_RANGE = CAL_OFFSET_RANGE_1kHz

        for offset_range in CAL_OFFSET_RANGE:
            chan = offset_range.split('_')
            freq = chan[0]
            scope = chan[1]
            vi_chan = chan[2]
            adc_chan = chan[3]
            adc_channel = adc_channel_dict[adc_chan]
            sine_freq = sine_freq_dict[freq]
            self.discharge_control('close')
            self.sine_output(1, sine_freq, KarmaDef.IOUT_DEFAULT_VPP)
            self.sine_output(2, sine_freq, KarmaDef.IOUT_DEFAULT_VPP, phase_value=KarmaDef.COSINE_PHASE)
            self.dds_control('open')
            self.set_line_path(vi_chan, scope, freq)

            data_list = []
            for i in range(5):
                data_list.append(self.read_adc_voltage(adc_channel))

            self.dds_control('close')
            self.discharge_control('open', discharge_time=20)
            self.discharge_control('close')

            data_list.sort()
            data_list = data_list[1:-1]
            avg_data = sum(data_list) / len(data_list)

            path = freq + '_' + scope + '_' + vi_chan + '_' + adc_chan
            cal_offset[path] = avg_data

        return cal_offset

    def calibrate(self, range_name, data, frequency=None):
        '''
        This function is used to calibrate data.

        Args:
            range_name:     string, which range used to do calibration
            data:           float, raw data which need to be calibrated.
            frequency:      int/None, default None.

        Returns:
            float:          calibrated data.

        Examples:
            result = karma.calibrate('300mohm_Ix_ch1', 100, 1000)
            print(result)
        '''
        if frequency:

            if self._cal_common_error is not None:
                raise self._cal_common_error

            assert range_name in self._calibration_table

            items = self._calibration_table[range_name]
            if len(items) == 0:
                return data

            if range_name in self._range_err_table:
                raise self._range_err_table[range_name]

            level = 0
            for i in range(len(items)):
                if frequency <= items[i]['threshold']:
                    level = i
                    break
                if not items[i]['is_use']:
                    break
                level = i
            return items[level]['gain'] * data + items[level]['offset']
        else:
            return super(KarmaBase, self).calibrate(range_name, data)


class Karma(KarmaBase):
    '''
    Karma function class

    compatible = ["GQQ-1084-5-010"]

    Args:
        i2c:        instance(I2C), instance of I2CBus, which is used to control cat24c32 and nct75.
        ipcore:     instance(MIXBT001SGR)/string, If given, then use MIXBT001SGR's AD7175, MIXQSPI, MIXGPIO.

    Examples:
        i2c_bus = I2C('/dev/i2c-0')
        karma = Karma(i2c_bus, '/dev/MIX_BT001_SG_R_0')

        # Karma measure impedance
        result = karma.resistance_measure('3000mohm', '1kHz', 20)
        print(result)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-1084-5-010"]

    def __init__(self, i2c, ipcore):
        super(Karma, self).__init__(i2c, ipcore,
                                    KarmaDef.EEPROM_DEV_ADDR,
                                    KarmaDef.SENSOR_DEV_ADDR,
                                    karma_range_table)
