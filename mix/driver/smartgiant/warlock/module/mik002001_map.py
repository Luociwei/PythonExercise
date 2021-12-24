# -*- coding: utf-8 -*-
import time
import math
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.bus.pin import Pin
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.smartgiant.common.ipcore.mix_fftanalyzer_sg import MIXFftAnalyzerSG
from mix.driver.smartgiant.common.ipcore.mix_mik002_sg_r import MIXMIK002SGR
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver


__author__ = "Jiasheng.Xie@SmartGiant"
__version__ = "V0.0.8"


warlock_function_info = {
    'mode_select': {
        'GB': {
            'bits': [(2, 0)]
        },
        'CH': {
            'bits': [(2, 1)]
        },
    },
    'range_select': {
        'HP_1Vrms': {
            'coefficient': 1.0 / (2.0),
            'unit': 'mV',
            'bits': [(0, 0), (1, 0), (3, 0), (4, 0), (6, 0), (7, 1), (8, 0), (9, 0), (10, 0), (11, 0)]
        },
        'HP_3.5Vrms': {
            'coefficient': 1.0 / (0.564765),
            'unit': 'mV',
            'bits': [(0, 1), (1, 0), (3, 0), (4, 1), (6, 0), (7, 1), (8, 0), (9, 0), (10, 0), (11, 0)]
        },
        'line_out': {
            'coefficient': 1.0 / (2.0),
            'unit': 'mV',
            'bits': [(0, 0), (1, 0), (3, 0), (4, 0), (6, 1), (7, 1), (8, 0), (9, 0), (10, 0), (11, 0)]
        }
    },
    'adc_sample_rate': {
        "192000Hz": {'bits': [(12, 1), (13, 1), (14, 0)]},
        "96000Hz": {'bits': [(12, 1), (13, 0), (14, 1)]},
        "48000Hz": {'bits': [(12, 1), (13, 0), (14, 0)]}
    },
    'mikey_tone': {
        'S1': {'bits': [(0, 0), (1, 1), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 1), (9, 0), (10, 0), (11, 0)]},
        'S2': {'bits': [(0, 0), (1, 1), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 1), (10, 0), (11, 0)]},
        'S3': {'bits': [(0, 0), (1, 1), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 1), (11, 0)]},
        'S0': {'bits': [(0, 0), (1, 1), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 1)]},
        'default': {'bits': [(0, 0), (1, 1), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0)]}
    },
    'ADC_HPF': {
        "enable": {
            'bits': [(15, 0)]
        },
        'disable': {
            'bits': [(15, 1)]
        }

    },
    'extra': {
        'headset_loopback': {
            'bits': [(0, 0), (1, 0), (3, 1), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0)]
        },
        'hp2mic_xtalk': {
            'unit': 'db',
            'bits': [(3, 0), (5, 1), (7, 1), (8, 0), (9, 0), (10, 0), (11, 0)]
        }

    }
}

warlock_range_table = {
    "LEFT_1RMS": 0,
    "LEFT_3.5RMS": 1,
    "RIGHT_1RMS": 2,
    "RIGHT_3.5RMS": 3,
    "LEFT_LINE_OUT": 4,
    "RIGHT_LINE_OUT": 5
}


class WarlockDef():

    MIX_MIK002_REG_SIZE = 65536

    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    CAT9555_DEV_ADDR = 0x20

    RST_DELAY_MS = 1
    RELAY_DELAY_MS = 5
    GPIO_DELAY_MS = 10

    MAX_SAMPLING_RATE = 192000
    RMS_TO_VPP_RATIO = 2.0 * math.sqrt(2)

    # this can be found in HW spec
    # max rms is 2000 mVrms
    AUDIO_ANALYZER_VREF = 2 * math.sqrt(2) * 2000

    RMS_LIST = {"HP_1Vrms": "1RMS", "HP_3.5Vrms": "3.5RMS", "line_out": "LINE_OUT"}

    sampling_rate_select = {0x30: 192000, 0x50: 96000, 0x10: 48000}
    sample_rate_pin_mask = 0x70

    AUDIO_CHANNEL_LIST = ["left", "right"]
    BANDWIDTH_AUTO = "auto"
    BANDWIDTH_MIN = 50
    BANDWIDTH_MAX = 95997
    HARMONIC_CNT_MIN = 1
    HARMONIC_CNT_MAX = 10
    DECIMATION_TYPE_MIN = 1
    DECIMATION_TYPE_MAX = 255

    ADC_HPF_PIN = 15

    IO_OUTPUT_DIR = "output"
    IO_INPUT_DIR = "input"

    ADC_RST_PIN = 0
    I2S_RX_EN_PIN = 1
    I2S_CH_SELECT_PIN = 2
    UPLOAD_CH_SELECT_PIN = 4
    TONE_DETECT_PIN = 5
    ADC_OVFL_L_PIN = 6

    DEFAULT_TIMEOUT = 1  # s


class WarlockException(Exception):
    def __init__(self, err_str):
        self.err_reason = "%s." % (err_str)

    def __str__(self):
        return self.err_reason


class Warlock(SGModuleDriver):
    '''
    Warlock is a high-pressure differential input digital audio module.

    compatible = ["GQQ-Q58K-5-010", "GQQ-Q58K-5-020"]

    Args:
        i2c:                  instance(I2C), the instance of I2C bus. which will be used to used
                              to control eeprom, sensor and io expander.
        ipcore:               instance(MIXMIK002SGR)/string, the instance of Ipcore, which has 2 child IP,
                              MIXFftAnalyzerSG, MIXGPIOSG.
        analyzer:             instance(PLFFTAnalyzer)/string, if not given, will create emulator.
        adc_rst_pin:          instance(GPIO), used to reset IIS of the CS5381.
        adc_ovfl_l_pin:       instance(GPIO), used to get state of the ovfl_l pin for CS5381.
        i2s_rx_en_pin:        instance(GPIO), used to enable fft analyzer module.
        i2s_ch_select_pin:    instance(GPIO), used to select measure channel for CS5381.
        tone_detect_pin:      instance(GPIO), used to get state of the tone detect pin.
        upload_ch_select_pin: instance(GPIO), used to select fft measuring or upload to DMA directly.
        sample_rate:          int, unit Hz, default 48000, used to configure the CS5381.

    Examples:
        # use non-aggregated IP
        i2c_bus = I2C('/dev/i2c-1')
        axi4 = AXI4LiteBus(analyzer_dev, 256)
        analyzer = MIXFftAnalyzerSG(axi4)
        adc_rst_pin = GPIO(88, 'output')
        adc_ovfl_l_pin = GPIO(93, 'output')
        i2s_rx_en_pin = GPIO(87, 'output')
        i2s_ch_select_pin = GPIO(95, 'output')
        tone_detect_pin = GPIO(94, 'output')
        upload_ch_select_pin = GPIO(97, 'output')
        warlock = Warlock(i2c=i2c_bus, ipcore=None,
                          analyzer=analyzer, adc_rst_pin=adc_rst_pin,
                          adc_ovfl_l_pin=adc_ovfl_l_pin, i2s_rx_en_pin=i2s_rx_en_pin,
                          i2s_ch_select_pin=i2s_ch_select_pin, tone_detect_pin=tone_detect_pin,
                          upload_ch_select_pin=upload_ch_select_pin, sample_rate=48000)

        # use MIXMIK002SGR aggregated IP
        i2c_bus = I2C('/dev/i2c-1')
        ipcore = MIXMIK002SGR('/dev/MIX_MIK002_SG_R')
        warlock = Warlock(i2c=i2c_bus, ipcore=ipcore)

        # measure left channel input in china mode.
        warlock.headphone_out('1Vrms', 'CH')
        warlock.measure('left', 20000, 5)

        # measure xtalk signal in china mode.
        warlock.hp2mic_xtalk('CH')
        warlock.xtalk_measure('hp2mic')
    '''

    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-Q58K-5-010", "GQQ-Q58K-5-020"]

    rpc_public_api = ['enable_upload', 'disable_upload', 'measure', 'xtalk_measure',
                      'mikey_tone', 'get_tone_detect_state', 'set_sampling_rate', 'get_sampling_rate',
                      'adc_hpf_state', 'headset_loopback', 'line_out', 'headphone_out', 'hp2mic_xtalk',
                      'io_set', 'io_dir_set', 'adc_reset', 'get_overflow_state', 'io_dir_read', 'io_read',
                      'start_record_data', 'stop_record_data'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, ipcore=None, analyzer=None, adc_rst_pin=None, adc_ovfl_l_pin=None, i2s_rx_en_pin=None,
                 i2s_ch_select_pin=None, tone_detect_pin=None, upload_ch_select_pin=None, sample_rate=48000):

        assert sample_rate > 0 and sample_rate <= WarlockDef.MAX_SAMPLING_RATE

        if (i2c and analyzer and adc_rst_pin and adc_ovfl_l_pin and i2s_rx_en_pin and
                i2s_ch_select_pin and tone_detect_pin and upload_ch_select_pin):
            self.i2c = i2c

            if isinstance(analyzer, basestring):
                self.analyzer = MIXFftAnalyzerSG(analyzer)
            else:
                self.analyzer = analyzer

            self.adc_rst_pin = adc_rst_pin
            self.adc_ovfl_l_pin = adc_ovfl_l_pin
            self.i2s_rx_en_pin = i2s_rx_en_pin
            self.i2s_ch_select_pin = i2s_ch_select_pin
            self.tone_detect_pin = tone_detect_pin
            self.upload_ch_select_pin = upload_ch_select_pin
        elif (ipcore and i2c):
            self.i2c = i2c
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, WarlockDef.MIX_MIK002_REG_SIZE)
                self.ipcore = MIXMIK002SGR(axi4_bus)
            else:
                self.ipcore = ipcore
            self.analyzer = self.ipcore.analyzer
            self.adc_rst_pin = Pin(self.ipcore.gpio, WarlockDef.ADC_RST_PIN)
            self.adc_ovfl_l_pin = Pin(self.ipcore.gpio, WarlockDef.ADC_OVFL_L_PIN)
            self.i2s_rx_en_pin = Pin(self.ipcore.gpio, WarlockDef.I2S_RX_EN_PIN)
            self.i2s_ch_select_pin = Pin(self.ipcore.gpio, WarlockDef.I2S_CH_SELECT_PIN)
            self.tone_detect_pin = Pin(self.ipcore.gpio, WarlockDef.TONE_DETECT_PIN)
            self.upload_ch_select_pin = Pin(self.ipcore.gpio, WarlockDef.UPLOAD_CH_SELECT_PIN)
        else:
            raise WarlockException("Parameter error")

        self.eeprom = CAT24C32(WarlockDef.EEPROM_DEV_ADDR, i2c)
        self.nct75 = NCT75(WarlockDef.SENSOR_DEV_ADDR, i2c)
        self.cat9555 = CAT9555(WarlockDef.CAT9555_DEV_ADDR, i2c)

        super(Warlock, self).__init__(self.eeprom, self.nct75, range_table=warlock_range_table)

        self.sampling_rate = sample_rate
        self.scope = ""
        self.mode = ""

    def post_power_on_init(self, timeout=WarlockDef.DEFAULT_TIMEOUT):
        '''
        Init Warlock module to a know harware state.

        This function will reset adc and i2s module.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=WarlockDef.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.


        Returns:
            string, "done", if execute successfully.

        '''
        start_time = time.time()

        while True:
            try:
                self.cat9555.set_pins_dir([0x00, 0xf0])
                self.adc_rst_pin.set_dir(WarlockDef.IO_OUTPUT_DIR)
                self.i2s_rx_en_pin.set_dir(WarlockDef.IO_OUTPUT_DIR)
                self.i2s_ch_select_pin.set_dir(WarlockDef.IO_OUTPUT_DIR)
                self.upload_ch_select_pin.set_dir(WarlockDef.IO_OUTPUT_DIR)
                self.tone_detect_pin.set_dir(WarlockDef.IO_INPUT_DIR)
                self.adc_ovfl_l_pin.set_dir(WarlockDef.IO_INPUT_DIR)

                # reset ADC
                self.adc_reset()

                self.i2s_rx_en_pin.set_level(1)

                io_states = self.cat9555.get_ports()
                self.cat9555.set_ports([0x00, io_states[1] & 0xf0])

                self._get_default_sampling_rate()
                return "done"
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise WarlockException("Timeout: {}".format(e.message))
        return "done"

    def pre_power_down(self, timeout=WarlockDef.DEFAULT_TIMEOUT):
        '''
        Put the hardware in a safe state to be powered down.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()

        while True:
            try:
                self.adc_rst_pin.set_level(0)
                self.i2s_rx_en_pin.set_level(0)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise WarlockException("Timeout: {}".format(e.message))

    def start_record_data(self, channel):
        '''
        Warlock start collect the data and upload to DMA directly.

        Args:
            channel:         string, ['left', 'right'].

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.start_record_data('left')

        '''
        assert channel in WarlockDef.AUDIO_CHANNEL_LIST
        self._audio_channel_select(channel)
        self.i2s_rx_en_pin.set_level(0)
        self.upload_ch_select_pin.set_level(1)
        time.sleep(WarlockDef.GPIO_DELAY_MS / 1000.0)
        self.i2s_rx_en_pin.set_level(1)
        return "done"

    def stop_record_data(self):
        '''
        Warlock stop collect the data.

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.stop_record_data()

        '''
        self.i2s_rx_en_pin.set_level(0)
        self.upload_ch_select_pin.set_level(0)
        self.i2s_rx_en_pin.set_level(1)
        time.sleep(WarlockDef.GPIO_DELAY_MS / 1000.0)
        return "done"

    def _get_default_sampling_rate(self):
        io_states = self.cat9555.get_ports()
        target_pin = io_states[1] & WarlockDef.sample_rate_pin_mask
        if target_pin in WarlockDef.sampling_rate_select:
            self.sampling_rate = WarlockDef.sampling_rate_select[target_pin]
        else:
            self.set_sampling_rate(self.sampling_rate)

    def _set_function_path(self, config, scope):
        '''
        Warlock set function path

        Args:
            config:     string, ['mode_select', 'range_select','mikey_tone',
                                 'short_circuit_detect', 'extra'].
            scope:       string, ['GB','CH','HP_1Vrms','HP_3.5Vrms','line_out','s1_enable',
                                 's2_enable','s3_enable','all_disable','MIC_S0_enable',
                                 'MIC_S0_disable','enable','disable','hp2mic_xtalk'].

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock._set_function_path('mode_select', 'GB')

        '''
        assert config in warlock_function_info
        assert scope in warlock_function_info[config]

        bits = warlock_function_info[config][scope]['bits']
        for bit in bits:
            self.cat9555.set_pin(bit[0], bit[1])

        time.sleep(WarlockDef.RELAY_DELAY_MS / 1000.0)

    def _volt_to_target_unit(self, scope, volt):
        '''
        Warlock get target unit value from measured voltage.

        Args:
            scope:      string, the range of channel measure.
            volt:       float, the measured voltage.

        Returns:
            float, value.

        '''
        assert scope in warlock_function_info['range_select']

        return volt * warlock_function_info['range_select'][scope]['coefficient']

    def _audio_channel_select(self, channel):
        '''
        Warlock cs5381 chip channel select.

        Args:
            channel:  string, ['left','right'], Use for select which channel to measure.

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock._audio_channel_select('left')

        '''
        if channel == 'left':
            self.i2s_ch_select_pin.set_level(0)
        else:
            self.i2s_ch_select_pin.set_level(1)

        return "done"

    def enable_upload(self):
        '''
        Warlock upoad mode open.

        Control audio upload data of ADC when doing measurement. It's not necessary
        enable upload when doing measurement. Note that data transfered into DMA is 32bit each data,
        but high 24bit data is valid. Low 8bit data is invalid. The data format is twos complement.

        Returns:
            string, 'done', api execution successful.

        '''
        self.analyzer.enable_upload()
        return "done"

    def disable_upload(self):
        '''
        Warlock upoad mode close. Close data upload doesn't influence to measure.

        Returns:
            string, 'done', api execution successful.

        '''
        self.analyzer.disable_upload()
        return "done"

    def set_sampling_rate(self, sampling_rate):
        '''
        Warlock set sampling rate.

        Args:
            sampling_rate:     int, [192000, 96000, 48000], unit Hz, adc measure sampling rate.

        Returns:
            string, 'done', api execution successful.

        Examples:
           warlock.set_sampling_rate(96000)

        '''
        assert str(sampling_rate) + "Hz" in warlock_function_info["adc_sample_rate"]
        io_dir_state = self.cat9555.get_pins_dir()
        if io_dir_state[1] & WarlockDef.sample_rate_pin_mask != 0:
            self.cat9555.set_pins_dir([io_dir_state[0], io_dir_state[1] & ~WarlockDef.sample_rate_pin_mask])
        self._set_function_path("adc_sample_rate", str(sampling_rate) + "Hz")
        self.sampling_rate = sampling_rate if isinstance(sampling_rate, int) else int(sampling_rate)
        return "done"

    def get_sampling_rate(self):
        '''
        Warlock get sampling rate.

        Returns:
            int, unit Hz.

        Examples:
           warlock.get_sampling_rate()

        '''
        return self.sampling_rate

    def headset_loopback(self, mode):
        '''
        Warlock set headset_loopback function.

        Args:
            mode:      string, ['GB', 'CH'], GB mean global mode, CH mean china mode.

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.headset_loopback('CH')

        '''
        assert mode in warlock_function_info["mode_select"]
        self._set_function_path("extra", "headset_loopback")
        self._set_function_path("mode_select", mode)
        return "done"

    def headphone_out(self, range_name, mode):
        '''
        Warlock set headphone_out function.

        Args:
            range_name: string, ['1Vrms', '3.5Vrms'].
            mode:       string, ['GB', 'CH'], GB mean global mode, CH mean china mode.

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.headphone_out('1Vrms', 'CH')

        '''
        assert ("HP_" + range_name) in warlock_function_info["range_select"]
        assert mode in warlock_function_info["mode_select"]
        self._set_function_path("range_select", "HP_" + range_name)
        self._set_function_path("mode_select", mode)
        self.mode = mode
        self.scope = "HP_" + range_name
        return "done"

    def line_out(self):
        '''
        Warlock set line_out function.

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.line_out()

        '''
        self._set_function_path("range_select", "line_out")
        self.scope = "line_out"
        return "done"

    def hp2mic_xtalk(self, mode):
        '''
        Warlock set hp2mic_xtalk function.

        Args:
            mode:       string, ['GB', 'CH'], GB mean global mode, CH mean china mode.

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.hp2mic_xtalk('CH')

        '''
        assert mode in warlock_function_info["mode_select"]
        self._set_function_path("extra", "hp2mic_xtalk")
        self._set_function_path("range_select", "HP_1Vrms")
        self._set_function_path("mode_select", mode)
        self.mode = mode
        self.scope = "HP_1Vrms"
        return "done"

    def io_set(self, io_list):
        '''
        Warlock set io state, this is a debug function.

        Args:
            io_list:   list, [[pin,state],[pin,state]], pin [0~15], state [0,1].

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.io_set([[0,1],[1,1]])

        '''
        assert isinstance(io_list, list)
        assert all([isinstance(io, list) and len(io) == 2 for io in io_list])
        assert all([io[0] in xrange(16) and io[1] in xrange(2) for io in io_list])
        for io in io_list:
            self.cat9555.set_pin(io[0], io[1])
        return "done"

    def io_dir_set(self, io_list):
        '''
        Warlock set io direction, this is a debug function.

        Args:
            io_list:   list, [[pin,state],[pin,state]], pin [0~15], state ['input','output'].

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.io_dir_set([[0,'output'],[1,'output']])

        '''
        assert isinstance(io_list, list)
        assert all([isinstance(io, list) and len(io) == 2 for io in io_list])
        assert all([io[0] in xrange(16) and io[1] in ['output', 'input'] for io in io_list])
        for io in io_list:
            self.cat9555.set_pin_dir(io[0], io[1])
        return 'done'

    def io_read(self, io_list):
        '''
        Warlock set io state, this is a debug function.

        Args:
            io_list:   list, [pinx,pinx,… ,pinx], pin x mean [0~15].

        Returns:
            list, [[pin,state],[pin,state]], pin [0~15], state [0,1].

        Examples:
            warlock.read_pin([0,1,2,7])

        '''
        assert isinstance(io_list, list)
        assert all([isinstance(io, int) for io in io_list])
        assert all([0 <= io <= 15 for io in io_list])
        data_list = []
        for io in io_list:
            data_list.append([io, self.cat9555.get_pin(io)])

        return data_list

    def io_dir_read(self, io_list):
        '''
        Warlock set io direction, this is a debug function.

        Args:
            io_list:   list, [pinx,pinx,… ,pinx], pin x mean [0~15].

        Returns:
            list, [[pin,state],[pin,state]], pin [0~15], state ['input','output'].

        Examples:
            warlock.read_pin_dir([0,1])

        '''
        assert isinstance(io_list, list)
        assert all([isinstance(io, int) for io in io_list])
        assert all([0 <= io <= 15 for io in io_list])
        data_list = []
        for io in io_list:
            data_list.append([io, self.cat9555.get_pin_dir(io)])
        return data_list

    def adc_reset(self):
        '''
        Warlock reset adc.

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.adc_reset()

        '''
        self.adc_rst_pin.set_level(0)
        time.sleep(WarlockDef.RST_DELAY_MS / 1000.0)
        self.adc_rst_pin.set_level(1)
        return "done"

    def measure(self, channel, bandwidth_hz=20000, harmonic_num=5, decimation_type=1):
        '''
        Warlock measure signal's Vpp, RMS, THD+N, THD.

        Args:
            channel:         string, ['left', 'right'].
            bandwidth_hz:    int, [50~95977], default 20000,  unit Hz, Measure signal's limit bandwidth,
                             The frequency of the signal should not be greater than half of the bandwidth.
            harmonic_num:    int, [2~10], default 5, Use for measuring signal's THD.
            decimation_type: int, [1~255], default 1, Decimation for FPGA to get datas,
                             If decimation is 0xFF, FPGA will choose one suitable number.

        Returns:
            dict, {'vpp': value, 'freq': value, 'thd': value, 'thdn': value, 'rms': value),
                  dict with vpp, freq, thd, thdn, rms.

        Examples:
            result = warlock.measure('left', 20000, 5)
            print result.frequency, result.vpp, result.thdn, result.thd, result.rms

        '''
        assert channel in WarlockDef.AUDIO_CHANNEL_LIST

        assert bandwidth_hz == WarlockDef.BANDWIDTH_AUTO or isinstance(bandwidth_hz, int)
        assert WarlockDef.BANDWIDTH_MIN <= bandwidth_hz <= WarlockDef.BANDWIDTH_MAX
        assert isinstance(harmonic_num, int) and\
            WarlockDef.HARMONIC_CNT_MIN <= harmonic_num <= WarlockDef.HARMONIC_CNT_MAX
        assert isinstance(decimation_type, int) and\
            WarlockDef.DECIMATION_TYPE_MIN <= decimation_type <= WarlockDef.DECIMATION_TYPE_MAX
        self._audio_channel_select(channel)
        self.stop_record_data()

        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(self.sampling_rate, decimation_type, bandwidth_hz, harmonic_num)
        self.analyzer.analyze()

        # calculate the actual vpp of HW by VREF
        vpp = self.analyzer.get_vpp() * WarlockDef.AUDIO_ANALYZER_VREF
        vpp = self._volt_to_target_unit(self.scope, vpp)
        # vpp = RMS * 2 * sqrt(2)
        rms = vpp / WarlockDef.RMS_TO_VPP_RATIO
        range_name = (channel + "_" + WarlockDef.RMS_LIST[self.scope]).upper()
        rms = self.calibrate(range_name, rms)

        # rms = self.calibrate(WarlockDef.MEASURE_CAL_ITEM, rms)
        vpp = rms * WarlockDef.RMS_TO_VPP_RATIO

        result = dict()
        result["vpp"] = vpp
        result["freq"] = self.analyzer.get_frequency()
        result["thd"] = self.analyzer.get_thd()
        result["thdn"] = self.analyzer.get_thdn()
        result["snr"] = -1 * result["thdn"]
        result["rms"] = rms
        return result

    def xtalk_measure(self, channel, bandwidth_hz=50000, harmonic_num=5, decimation_type=1):
        '''
        Warlock Crosstalk mode measure.

        Args:
            channel:    string, ['hp2mic', 'hpl2r', 'hpr2l'].
            bandwidth_hz:    int, [50~95977], default 50000,  unit Hz, Measure signal's limit bandwidth,
                             The frequency of the signal should not be greater than half of the bandwidth.
            harmonic_num:    int, [2~10],     default 5, Use for measuring signal's THD.
            decimation_type: int, [1~255], default 1, Decimation for FPGA to get data,
                             If decimation is 0xFF, FPGA will choose one suitable number.

        Returns:
            list, [value, db].

        Examples:
            warlock.xtalk_measure('hp2mic')

        '''
        assert channel in ["hp2mic", "hpl2r", "hpr2l"]
        Va = self.measure("left", bandwidth_hz, harmonic_num, decimation_type)["rms"]
        Vb = self.measure("right", bandwidth_hz, harmonic_num, decimation_type)["rms"]
        if channel == "hpr2l":
            return [20 * math.log(Vb / Va, 10), "db"]
        else:
            return [20 * math.log(Va / Vb, 10), "db"]

    def mikey_tone(self, freq="default", mode="GB"):
        '''
        Warlock set signal output.

        Args:
            freq:      string, ['S1', 'S2', 'S3', 'S0', 'default'], default 'default' mean (S0, S1, S2, S3)=0.
            mode:      string, ['GB', 'CH'], default 'GB', GB mean global mode, CH mean china mode.

        Returns:
            string, 'done', api execution successful.

        Examples:
            warlock.mikey_tone('S1', 'CH')

        '''
        assert freq in warlock_function_info["mikey_tone"]
        assert mode in warlock_function_info["mode_select"]

        self._set_function_path("mode_select", mode)
        self._set_function_path("mikey_tone", freq)
        return "done"

    def get_tone_detect_state(self):
        '''
        Warlock get tone detect state.

        Returns:
            int, [1,0], 1 mean high level, 0 mean low level.

        Examples:
            warlock.get_tone_detect_state()

        '''
        return self.tone_detect_pin.get_level()

    def get_overflow_state(self):
        '''
        Warlock get overflow pin state.

        Returns:
            int, [1,0], 1 mean high level, 0 mean low level.

        Examples:
            warlock.get_overflow_state()

        '''
        return self.adc_ovfl_l_pin.get_level()

    def adc_hpf_state(self, state):
        '''
        Warlock set adc hpf pin.

        Args:
            state:     string, ['enable', 'disable'].

        Returns:
            string, 'done', api execution successful.

        Examples:
           warlock.adc_hpf_state('enable')

        '''
        assert state in ["enable", "disable"]
        if self.cat9555.get_pin_dir(WarlockDef.ADC_HPF_PIN) != WarlockDef.IO_OUTPUT_DIR:
            self.cat9555.set_pin_dir(WarlockDef.ADC_HPF_PIN, WarlockDef.IO_OUTPUT_DIR)

        self._set_function_path("ADC_HPF", state)
        return "done"

    def get_driver_version(self):
        '''
        Get Warlock driver version.

        Returns:
            string, current driver version.
        '''
        return __version__
