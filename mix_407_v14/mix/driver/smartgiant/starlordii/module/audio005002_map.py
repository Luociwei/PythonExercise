# -*- coding: utf-8 -*-
import time
import math
import bisect
from mix.driver.core.bus.pin import Pin
from mix.driver.smartgiant.starlordii.module.audio005001_map import Audio005Base
from mix.driver.smartgiant.starlordii.module.audio005001_map import starlordii_range_table
from mix.driver.smartgiant.common.module.mixmoduleerror import (InvalidHardwareChannel, InvalidSampleRate,
                                                                InvalidSampleCount, InvalidTimeout)


__author__ = "dongdong.zhang@SmartGiant"
__version__ = "0.0.2"


audio005002_range_table = {
    "AUDIO_OUTPUT": 0,
    "AUDIO_20mV_left": 1,
    "AUDIO_20mV_right": 2,
    "AUDIO_2V_left": 3,
    "AUDIO_2V_right": 4
}


class Audio005002Def:

    ADCM0_CTL_BIT = 2
    ADCM1_CTL_BIT = 3

    I2S_RX_ENABLE = 1
    I2S_RX_DISABLE = 0

    AUDIO_CHANNEL_LIST = {"left": [0, 0], "right": [1, 0]}
    SELECT_BIT0 = 0
    SELECT_BIT1 = 1

    LNA_RANGE_2V = "2V"
    LNA_SCOPE = ("2V", "20mV")
    ADC_CH_LIST = {"right": 0, "left": 1}
    SEL_GAIN_1 = 1
    SEL_GAIN_100 = 0
    DEF_SAMPLING_RATE = 48000

    SAMPLING_RANGE = [50001, 100001, 192001]
    ADCM_CTL_LIST = ([0, 0], [0, 1], [1, 0])

    # audio measure, which range used to do calibration, unit Hz
    CAL_RANGE = [30, 600, 3000, 5000, 6000, 7000, 8000, 9000, 10000, 11000,
                 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000, 400000]

    VOLT_UNIT_MV = "mV"
    VOLT_UNIT_RMS = "mVrms"
    FREQ_UNIT_HZ = "Hz"
    THD_UNIT_DB = "dB"
    THDN_UNIT_DB = "dB"

    # if scope is '2V', max rms is 2000 mVrms
    AUDIO_ANALYZER_2V_VREF = 2.0 * math.sqrt(2) * 2000
    # if scope is '20mV', max rms is 20 mVrms
    AUDIO_ANALYZER_20mV_VREF = 2.0 * math.sqrt(2) * 20
    RMS_TO_VPP_RATIO = 2.0 * math.sqrt(2)
    MAX_HARMONIC_WIDTH = 20000
    RAM_OUT_PIN = 31
    USE_RAM = 1
    USE_SIGNAL_SOURCE = 0

    IO_DIR_OUTPUT = "output"
    PIN_LEVEL_LOW = 0
    PIN_LEVEL_HIGH = 1

    AUDIO_SAMPLING_RATE = 192000
    OUTPUT_WAVE = "sine"
    SIGNAL_ALWAYS_OUTPUT = 0xffffffff
    # output signal range defined in HW Spec
    OUTPUT_SIGNAL_DUTY = 0.5
    OUTPUT_FREQ_MIN = 5
    OUTPUT_FREQ_MAX = 50000
    OUTPUT_VPP_MIN = 0
    # OUTPUT_RMS_MAX(2300) * 2 * math.sqrt(2)
    OUTPUT_VPP_MAX = 2300 * 2 * math.sqrt(2)
    OUTPUT_CAL_ITEM = "AUDIO_OUTPUT"
    VPP_2_SCALE_RATIO = 0.999 / OUTPUT_VPP_MAX

    AUDIO_OUTPUT_ENABLE = 1
    AUDIO_OUTPUT_DISABLE = 0

    DECIMAT_TYPE = 4
    BANDWIDTH = 40000
    HARMONIC_COUNT = 4
    # unit S
    TIME_OUT = 1

    PIN_RELAY_DELAY_S = 0.03
    RELAY_DELAY_S = 0.01
    ADC_CH_RIGHT_CTL_BIT = 0
    ADC_CH_LEFT_CTL_BIT = 1

    ADC_SAMPLING_RATE_LIST = [48000, 96000, 192000]
    DAC_SAMPLING_RATE_LIST = [192000]

    # max voltage when scope is '2V'
    ANALYZER_2V_VOLT = math.sqrt(2) * 2000.0
    # max voltage when scope is '20mV'
    ANALYZER_20mV_VOLT = math.sqrt(2) * 20.0
    # OUTPUT_RMS_MAX(2300) * math.sqrt(2)
    OUTPUT_VOLT_MAX = 2300 * math.sqrt(2)

    MINI_NUM = 1
    OUTPUT_MAX_NUM = 16384
    # Due to the existence of capacitance, it is necessary to delay
    # the capacitor discharge for more than 32ms after the loss of energy
    OUTPUT_RELAY_DELAY_S = 0.1
    # The board type of hardware configuration
    AUDIO005002_CONFIG = "020"
    CONFIG_ADDR = 0x15


class Audio005002Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Audio005002(Audio005Base):
    '''
    Audio005002 is a high resolution differential input/output digital audio module.

    Args:
        i2c:             instance(I2C), the instance of I2C bus. which will be used to used
                                        to control eeprom, sensor and io expander.
        ipcore:          instance(MIXAudio005SGR), the instance of MIXAudio005SGR, which include
                                                   AD717x, FFT Analyzer, Signal Source, RAM Signal,
                                                   Audio Cache  and gpio function.
                                                   If device name string is passed to the parameter,
                                                   the ipcore can be instanced in the module.
        dma:             instance(MIXDMASG)/None, the instance of MIXDMASG. which will be used to used
        left_ch_id:      int/None, [0~15], Id of the left channel to be configured.
        right_ch_id:     int/None, [0~15], Id of the right channel to be configured.
        dma_mem_size:    int/None, [0~MIXDMASG_MEM_SIZE], default 1M, unit M, MIX_DMA_SG channel size.
                                   1M=1024*1024 Byte and a point is 32 bit, which is 4 Byte,
                                   so 1M=1024*1024/4=262144 points.

    Examples:
        i2c = I2C('/dev/i2c-0')
        audio005002 = Audio005002(i2c, '/dev/MIX_Audio005002_SG_R')
        audio005002.post_power_on_init()
        # measure left channel input
        LEFT_CHANNEL = 1
        audio005002.configure_input_channel(LEFT_CHANNEL, True, False, 48000)
        # start recording
        # wait for 1 s
        # collect samples
        # stop recording
        audio005002.configure_input_channel(LEFT_CHANNEL, False)
        data = audio005002.read(LEFT_CHANNEl, 8192)
        print data
    '''
    rpc_public_api = ['configure_input_channel', 'get_input_channel_configuration',
                      'configure_output_channel', 'get_output_channel_configuration',
                      'read', 'write', 'get_noisefloor'] + Audio005Base.rpc_public_api

    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-03C6-5-020", "GQQ-03C6-5-02A"]

    def __init__(self, i2c, ipcore, dma=None, left_ch_id=None, right_ch_id=None, dma_mem_size=1):
        super(Audio005002, self).__init__(i2c, ipcore)

        self.ram_signal = self.ipcore.ram_signal
        self.audio_cache = self.ipcore.audio_cache
        self.ram_out_pin = Pin(self.ipcore.gpio, Audio005002Def.RAM_OUT_PIN)

        self.adc_sample_rate = Audio005002Def.DEF_SAMPLING_RATE
        self.dac_sample_rate = Audio005002Def.AUDIO_SAMPLING_RATE
        self.vref = [Audio005002Def.ANALYZER_2V_VOLT, Audio005002Def.ANALYZER_2V_VOLT]
        self.input_enable = [False, False]
        self.output_enable = False
        self.model = Audio005002Def.AUDIO005002_CONFIG

        self.dma = dma
        if self.dma is not None:
            self.left_ch_id = left_ch_id
            self.right_ch_id = right_ch_id
            self.dma_mem_size = dma_mem_size
            if self.left_ch_id is None or self.right_ch_id is None or self.dma_mem_size is None:
                raise Audio005002Exception("dma parameter error")

    def read_hardware_config(self):
        '''
        returns a string that represents the config
        '''
        return "".join([chr(c) for c in self.read_nvmem(Audio005002Def.CONFIG_ADDR, 3)])

    def load_calibration(self):
        '''
        Load calibration data. If GQQ is defined in eeprom, this function will load calibration defined.
        '''
        self.model = self.read_hardware_config()
        if self.model == Audio005002Def.AUDIO005002_CONFIG:
            self._range_table = starlordii_range_table
        else:
            # Compatible with 02A model
            self._range_table = audio005002_range_table
        super(Audio005002, self).load_calibration()

    def post_power_on_init(self, timeout=Audio005002Def.TIME_OUT):
        '''
        Init audio005 module to a know harware state.

        This function will reset reset dac/adc and i2s module.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        self.reset(timeout)
        if self.dma is not None:
            self.dma.config_channel(self.left_ch_id, self.dma_mem_size * 0X100000)
            self.dma.config_channel(self.right_ch_id, self.dma_mem_size * 0X100000)

    def reset(self, timeout=Audio005002Def.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()
        while True:
            try:
                self.adc_rst_pin.set_dir(Audio005002Def.IO_DIR_OUTPUT)
                self.dac_rst_pin.set_dir(Audio005002Def.IO_DIR_OUTPUT)
                self.i2s_rx_en_pin.set_dir(Audio005002Def.IO_DIR_OUTPUT)
                self.i2s_tx_en_pin.set_dir(Audio005002Def.IO_DIR_OUTPUT)
                self.ram_out_pin.set_dir(Audio005002Def.IO_DIR_OUTPUT)

                # reset ADC
                self.adc_rst_pin.set_level(Audio005002Def.PIN_LEVEL_LOW)
                time.sleep(Audio005002Def.RELAY_DELAY_S)
                self.adc_rst_pin.set_level(Audio005002Def.PIN_LEVEL_HIGH)

                # reset DAC
                self.dac_rst_pin.set_level(Audio005002Def.PIN_LEVEL_LOW)
                time.sleep(Audio005002Def.RELAY_DELAY_S)
                self.dac_rst_pin.set_level(Audio005002Def.PIN_LEVEL_HIGH)

                # reset i2s rx
                self.i2s_rx_en_pin.set_level(Audio005002Def.PIN_LEVEL_LOW)

                # reset i2s tx
                self.i2s_tx_en_pin.set_level(Audio005002Def.PIN_LEVEL_LOW)

                self.ram_out_pin.set_level(Audio005002Def.PIN_LEVEL_LOW)
                # io init
                self.pca9536.set_pin_dir(Audio005002Def.ADC_CH_RIGHT_CTL_BIT, Audio005002Def.IO_DIR_OUTPUT)
                self.pca9536.set_pin_dir(Audio005002Def.ADC_CH_LEFT_CTL_BIT, Audio005002Def.IO_DIR_OUTPUT)
                self.pca9536.set_pin_dir(Audio005002Def.ADCM0_CTL_BIT, Audio005002Def.IO_DIR_OUTPUT)
                self.pca9536.set_pin_dir(Audio005002Def.ADCM1_CTL_BIT, Audio005002Def.IO_DIR_OUTPUT)

                self.pca9536.set_pin(Audio005002Def.ADC_CH_RIGHT_CTL_BIT, Audio005002Def.PIN_LEVEL_HIGH)
                self.pca9536.set_pin(Audio005002Def.ADC_CH_LEFT_CTL_BIT, Audio005002Def.PIN_LEVEL_HIGH)
                self.pca9536.set_pin(Audio005002Def.ADCM0_CTL_BIT, Audio005002Def.PIN_LEVEL_LOW)
                self.pca9536.set_pin(Audio005002Def.ADCM1_CTL_BIT, Audio005002Def.PIN_LEVEL_LOW)

                self.model = self.read_hardware_config()
                if self.model == Audio005002Def.AUDIO005002_CONFIG:
                    self._range_table = starlordii_range_table
                else:
                    # Compatible with 02A model
                    self._range_table = audio005002_range_table

                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise Audio005002Exception("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get audio005 driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def measure(self, channel, scope, bandwidth_hz, decimation_type=0xFF,
                sampling_rate=Audio005002Def.DEF_SAMPLING_RATE):
        '''
        Measure audio input signal, which captures data using CS5361.

        Args:
            channel:         string, ['left', 'right'], select input signal channel.
            scope:           string, ['2V', '20mV'], AD7175 measurement range.
            bandwidth_hz:    int/string, [42~48000], unit Hz, the signal bandwidth.
                             In theory the bandwidth must smaller than half the sampling rate.
                             eg, if sampling_rate = 192000, so bandwidth_hz  < 96000.
                             The bandwidth must be greater than the frequency of the input signal.
            decimation_type: int, [1~255], default 0xFF, sample data decimation.
                             decimation_type is 1 means not to decimate.
                             The smaller the input frequency, the larger the value should be.
            sampling_rate:   int, [0~192000], default 48000, unit Hz, ADC sampling rate.

        Returns:
            dict, {'vpp': value, 'freq': value, 'thd': value, 'thdn': value, 'rms': value, 'noisefloor': value},
            measurement result.
        '''
        assert channel in Audio005002Def.AUDIO_CHANNEL_LIST
        assert scope in Audio005002Def.LNA_SCOPE

        if self.is_enable_upload is False:
            self.i2s_rx_en_pin.set_level(Audio005002Def.I2S_RX_ENABLE)

        pin = self.i2s_ch_select[Audio005002Def.SELECT_BIT0]
        pin.set_level(Audio005002Def.AUDIO_CHANNEL_LIST[channel][Audio005002Def.SELECT_BIT0])
        pin = self.i2s_ch_select[Audio005002Def.SELECT_BIT1]
        pin.set_level(Audio005002Def.AUDIO_CHANNEL_LIST[channel][Audio005002Def.SELECT_BIT1])

        if scope == Audio005002Def.LNA_RANGE_2V:
            self.pca9536.set_pin(Audio005002Def.ADC_CH_LIST[channel], Audio005002Def.SEL_GAIN_1)
            gain = Audio005002Def.AUDIO_ANALYZER_2V_VREF
        else:
            self.pca9536.set_pin(Audio005002Def.ADC_CH_LIST[channel], Audio005002Def.SEL_GAIN_100)
            gain = Audio005002Def.AUDIO_ANALYZER_20mV_VREF

        index = bisect.bisect(Audio005002Def.SAMPLING_RANGE, sampling_rate)

        pin_level = Audio005002Def.ADCM_CTL_LIST[index][Audio005002Def.SELECT_BIT0]
        self.pca9536.set_pin(Audio005002Def.ADCM0_CTL_BIT, pin_level)
        pin_level = Audio005002Def.ADCM_CTL_LIST[index][Audio005002Def.SELECT_BIT1]
        self.pca9536.set_pin(Audio005002Def.ADCM1_CTL_BIT, pin_level)

        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(sampling_rate, decimation_type, bandwidth_hz)
        self.analyzer.analyze()

        freq = self.analyzer.get_frequency()

        harmonic_count = int(Audio005002Def.MAX_HARMONIC_WIDTH / freq)
        harmonic_count = 10 if harmonic_count > 10 else harmonic_count
        harmonic_count = 2 if harmonic_count <= 1 else harmonic_count

        self.analyzer.set_harmonic_count(harmonic_count)

        vpp = self.analyzer.get_vpp() * gain
        rms = vpp / Audio005002Def.RMS_TO_VPP_RATIO

        if scope == Audio005002Def.LNA_RANGE_2V:
            # Since the calibration range is within 20000Hz, the actual measurement result may be slightly
            # greater than 20000Hz when the input signal frequency is 20000Hz.
            # Therefore, the calibration frequency is appropriately increased to 20010Hz.
            if self.model == Audio005002Def.AUDIO005002_CONFIG:
                if freq > 20000:
                    index = bisect.bisect(Audio005002Def.CAL_RANGE, freq - 10)
                else:
                    index = bisect.bisect(Audio005002Def.CAL_RANGE, freq)
                range_name = "AUDIO_2V_" + str(Audio005002Def.CAL_RANGE[index]) + "Hz_" + channel
            else:
                # Compatible with 02A model
                range_name = "AUDIO_2V_" + channel
        else:
            range_name = "AUDIO_20mV_" + channel

        rms = self.calibrate(range_name, rms)
        vpp = rms * Audio005002Def.RMS_TO_VPP_RATIO
        thdn_value = self.analyzer.get_thdn()

        result = dict()
        result["vpp"] = (vpp, Audio005002Def.VOLT_UNIT_MV)
        result["freq"] = (freq, Audio005002Def.FREQ_UNIT_HZ)
        result["thd"] = (self.analyzer.get_thd(), Audio005002Def.THD_UNIT_DB)
        result["thdn"] = (thdn_value, Audio005002Def.THDN_UNIT_DB)
        result["rms"] = (rms, Audio005002Def.VOLT_UNIT_RMS)
        result["noisefloor"] = (10 ** (thdn_value / 20) * rms, Audio005002Def.VOLT_UNIT_RMS)

        if self.is_enable_upload is False:
            self.i2s_rx_en_pin.set_level(Audio005002Def.I2S_RX_DISABLE)

        return result

    def get_noisefloor(self, channel, scope, bandwidth_hz, decimation_type=0xFF,
                       sampling_rate=192000):
        '''
        Measure audio input signal, which captures data using CS5361.

        Args:
            channel:         string, ['left', 'right'], select input signal channel.
            scope:           string, ['2V', '20mV'], AD7175 measurement range.
            bandwidth_hz:    int/string, [42~48000], unit Hz, the signal bandwidth.
                             In theory the bandwidth must smaller than half the sampling rate.
                             eg, if sampling_rate = 192000, so bandwidth_hz  < 96000.
                             The bandwidth must be greater than the frequency of the input signal.
            decimation_type: int, [1~255], default 0xFF, sample data decimation.
                             decimation_type is 1 means not to decimate.
                             The smaller the input frequency, the larger the value should be.
            sampling_rate:   int, [0~192000], default 192000, unit Hz, ADC sampling rate.

        Returns:
            float, value, unit mVrms,  Result of signal's noisefloor.

        '''
        if self.is_enable_upload is False:
            self.i2s_rx_en_pin.set_level(Audio005002Def.I2S_RX_ENABLE)

        pin = self.i2s_ch_select[Audio005002Def.SELECT_BIT0]
        pin.set_level(Audio005002Def.AUDIO_CHANNEL_LIST[channel][Audio005002Def.SELECT_BIT0])
        pin = self.i2s_ch_select[Audio005002Def.SELECT_BIT1]
        pin.set_level(Audio005002Def.AUDIO_CHANNEL_LIST[channel][Audio005002Def.SELECT_BIT1])

        if scope == Audio005002Def.LNA_RANGE_2V:
            self.pca9536.set_pin(Audio005002Def.ADC_CH_LIST[channel], Audio005002Def.SEL_GAIN_1)
            gain = Audio005002Def.AUDIO_ANALYZER_2V_VREF
        else:
            self.pca9536.set_pin(Audio005002Def.ADC_CH_LIST[channel], Audio005002Def.SEL_GAIN_100)
            gain = Audio005002Def.AUDIO_ANALYZER_20mV_VREF

        index = bisect.bisect(Audio005002Def.SAMPLING_RANGE, sampling_rate)

        pin_level = Audio005002Def.ADCM_CTL_LIST[index][Audio005002Def.SELECT_BIT0]
        self.pca9536.set_pin(Audio005002Def.ADCM0_CTL_BIT, pin_level)
        pin_level = Audio005002Def.ADCM_CTL_LIST[index][Audio005002Def.SELECT_BIT1]
        self.pca9536.set_pin(Audio005002Def.ADCM1_CTL_BIT, pin_level)

        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(sampling_rate, decimation_type, bandwidth_hz)
        self.analyzer.analyze()

        noisefloor = self.analyzer.get_noisefloor() * gain

        if self.is_enable_upload is False:
            self.i2s_rx_en_pin.set_level(Audio005002Def.I2S_RX_DISABLE)

        return noisefloor

    def enable_output(self, freq, vpp):
        '''
        Audio005 CS5361 output audio sine waveform.

        Args:
            freq:       int, [5~50000], unit Hz, output signal's frequency.
            vpp:        float, [0~6504], unit mV, output signal's vpp.

        Returns:
            string, "done", execution successful.
        '''
        assert Audio005002Def.OUTPUT_FREQ_MIN <= freq
        assert freq <= Audio005002Def.OUTPUT_FREQ_MAX
        assert Audio005002Def.OUTPUT_VPP_MIN <= vpp
        assert vpp <= Audio005002Def.OUTPUT_VPP_MAX

        vpp = self.calibrate(Audio005002Def.OUTPUT_CAL_ITEM, vpp)
        vpp = 0 if vpp < 0 else vpp
        # enable I2S tx module
        self.i2s_tx_en_pin.set_level(Audio005002Def.AUDIO_OUTPUT_ENABLE)
        self.ram_out_pin.set_level(Audio005002Def.USE_SIGNAL_SOURCE)

        self.signal_source.close()
        self.signal_source.open()
        # calculate vpp to vpp scale for FPGA
        vpp_scale = vpp * Audio005002Def.VPP_2_SCALE_RATIO
        self.signal_source.set_swg_paramter(Audio005002Def.AUDIO_SAMPLING_RATE, freq,
                                            vpp_scale, Audio005002Def.OUTPUT_SIGNAL_DUTY)
        self.signal_source.set_signal_type(Audio005002Def.OUTPUT_WAVE)
        self.signal_source.set_signal_time(Audio005002Def.SIGNAL_ALWAYS_OUTPUT)
        self.signal_source.output_signal()

        return "done"

    def configure_input_channel(self, channel, enable, enable_lna=False, sample_rate=Audio005002Def.DEF_SAMPLING_RATE):
        '''
        Configure input channel based on given parameters.

        Args:
            channel:      int, [1, 2], currently defined are 1(left), 2(right).
            enable:       boolean, indicating if given path should be enabled.
            enable_lna:   boolean, true if LNA should be enabled for given input path.
            sample_rate:  int, [48000, 96000, 192000], Sample rate to use for given channel.

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2.
            InvalidSampleRate() if sample_rate is bad.

        Return:
            dict, { "channel" : 1, "sample_rate" : 48000, "enable" : True, "enable_lna" : True,
                    "supported_sample_rates" : [48000, 96000, 192000] }, Actual channel configuration.
        '''
        if channel not in [1, 2]:
            raise InvalidHardwareChannel("channel is not 1 or 2")

        if sample_rate not in [48000, 96000, 192000]:
            raise InvalidSampleRate("sample_rate is bad")

        ADC_CH_LIST = {1: 1, 2: 0}
        CHANNEL_LIST = {1: self.left_ch_id, 2: self.right_ch_id}
        code = channel - 1

        if enable is True:
            self.i2s_rx_en_pin.set_level(Audio005002Def.I2S_RX_ENABLE)

        if enable_lna is True:
            self.pca9536.set_pin(ADC_CH_LIST[channel], Audio005002Def.SEL_GAIN_100)
            self.vref[code] = Audio005002Def.ANALYZER_20mV_VOLT
        else:
            self.pca9536.set_pin(ADC_CH_LIST[channel], Audio005002Def.SEL_GAIN_1)
            self.vref[code] = Audio005002Def.ANALYZER_2V_VOLT

        index = bisect.bisect(Audio005002Def.SAMPLING_RANGE, sample_rate)
        pin_level = Audio005002Def.ADCM_CTL_LIST[index][Audio005002Def.SELECT_BIT0]
        self.pca9536.set_pin(Audio005002Def.ADCM0_CTL_BIT, pin_level)
        pin_level = Audio005002Def.ADCM_CTL_LIST[index][Audio005002Def.SELECT_BIT1]
        self.pca9536.set_pin(Audio005002Def.ADCM1_CTL_BIT, pin_level)
        self.adc_sample_rate = sample_rate

        if enable is True:
            time.sleep(Audio005002Def.PIN_RELAY_DELAY_S)
            self.dma.enable_channel(CHANNEL_LIST[channel])
            self.dma.reset_channel(CHANNEL_LIST[channel])
            self.input_enable[code] = True
        else:
            self.i2s_rx_en_pin.set_level(Audio005002Def.I2S_RX_DISABLE)
            self.dma.disable_channel(CHANNEL_LIST[channel])
            self.input_enable[code] = False

        result = dict()
        result["channel"] = channel
        result["sample_rate"] = self.adc_sample_rate
        result["enable"] = enable
        result["enable_lna"] = enable_lna
        result["supported_sample_rates"] = [48000, 96000, 192000]

        return result

    def get_input_channel_configuration(self, channel):
        '''
        Returns the configuration of the specified channel.

        Args:
            channel: int, [1, 2], the desired channel.

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2.

         Returns:
            dict, { "channel" : 1, "sample_rate" : 48000, "enable" : True, "enable_lna" : True,
                    "supported_sample_rates" : [48000, 96000, 192000] }.
        '''
        if channel not in [1, 2]:
            raise InvalidHardwareChannel("channel is not 1 or 2")
        code = channel - 1

        if self.input_enable[code] is True:
            enable = True
        else:
            enable = False

        if self.vref[code] == Audio005002Def.ANALYZER_20mV_VOLT:
            enable_lna = True
        else:
            enable_lna = False

        result = dict()
        result["channel"] = channel
        result["sample_rate"] = self.adc_sample_rate
        result["enable"] = enable
        result["enable_lna"] = enable_lna
        result["supported_sample_rates"] = [48000, 96000, 192000]

        return result

    def configure_output_channel(self, channel, enable, sample_rate=Audio005002Def.AUDIO_SAMPLING_RATE):
        '''
        Configure output channel based on given parameters.

        Args:
            channel:      int, [1, 2], currently defined are 1(left), 2(right).
            enable:       boolean, indicating if given path should be enabled.
            sample_rate:  int, [192000], Sample rate to use for given channel.

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2.
            InvalidSampleRate() if sample_rate is bad.

        Return:
            dict, { "channel" : 1, "sample_rate" : 192000, "enable" : True,
                    "supported_sample_rates" : [192000] }
        '''
        if channel not in [1, 2]:
            raise InvalidHardwareChannel("channel is not 1 or 2")

        if sample_rate != Audio005002Def.AUDIO_SAMPLING_RATE:
            raise InvalidSampleRate("sample_rate is bad")

        if enable is True:
            self.i2s_tx_en_pin.set_level(Audio005002Def.AUDIO_OUTPUT_ENABLE)
            self.ram_out_pin.set_level(Audio005002Def.USE_RAM)
            self.output_enable = True
        else:
            self.i2s_tx_en_pin.set_level(Audio005002Def.AUDIO_OUTPUT_DISABLE)
            self.output_enable = False

        result = dict()
        result["channel"] = channel
        result["sample_rate"] = sample_rate
        result["enable"] = enable
        result["supported_sample_rates"] = [192000]

        return result

    def get_output_channel_configuration(self, channel):
        '''
        Returns the configuration of the specified channel.

        Args:
            channel: int, [1, 2], the desired channel.

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2

         Returns:
            dict, { "channel" : 1, "sample_rate" : 192000, "enable" : True,
                    "supported_sample_rates" : [192000] }
        '''
        if channel not in [1, 2]:
            raise InvalidHardwareChannel("channel is not 1 or 2")

        if self.output_enable is True:
            enable = True
        else:
            enable = False

        result = dict()
        result["channel"] = channel
        result["sample_rate"] = self.dac_sample_rate
        result["enable"] = enable
        result["supported_sample_rates"] = [192000]

        return result

    def _conversion_voltage_value(self, vref, data):
        '''
        Converts 32-bit data to voltage values.

        Args:
            vref:        float, unit mV.
            data:        list.

        Returns:
            list, voltage, unit mV.
        '''
        data >>= 8
        value = data & 0xffffff
        if(value >= pow(2, 23)):
            volt = value - pow(2, 24)
        else:
            volt = value

        volt = float(volt) / pow(2, 23)
        volt = volt * vref

        return volt

    def _read_voltage_points(self, channel, samples_per_channel, timeout=1000):
        '''
        Args:
            channel:             int, [1, 2].
            samples_per_channel: int. number of points read.
            timeout:             int, (>=0), default 1000, unit ms, execute timeout.

        Returns:
            list, unit mV, voltage.
        '''

        CHANNEL_LIST = {1: self.left_ch_id, 2: self.right_ch_id}
        code = channel - 1

        result, data, num, overflow = self.dma.read_channel_data(CHANNEL_LIST[channel],
                                                                 samples_per_channel * 4, timeout)
        if result == 0:
            data_list = data[:num]
        else:
            raise Audio005002Exception("get dma data error:{}".format(result))

        data_info = []
        data_len = len(data_list)
        for one_payload in range(0, data_len, 4):
            data = data_list[one_payload + 0] | data_list[one_payload + 1] << 8 | \
                data_list[one_payload + 2] << 16 | data_list[one_payload + 3] << 24

            if data & 0x05 != 0x00:
                continue
            data = self._conversion_voltage_value(self.vref[code], data)
            data_info.append(data)

        return data_info

    def read(self, channels, samples_per_channel, timeout=10.0):
        '''
        Args:
            channels:            int/list, [1, 2], the desired channel(s).
            samples_per_channel: int. number of points read.
            timeout:             float, (>=0), default 10.0, unit Second, execute timeout.

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2
            InvalidSampleCount() if samples_per_channel is of bad value
            InvalidTimeout() if invalid timeout value

        Returns:
            list, unit mv, ADC measurement data.
        '''
        if isinstance(channels, int) and channels not in [1, 2]:
            raise InvalidHardwareChannel("channel is not 1 or 2")
        if isinstance(channels, list) and (0 == len(channels) or len(channels) > 2):
            raise InvalidHardwareChannel("channel is not 1 or 2")
        if isinstance(channels, list) and 1 == len(channels) and channels[0] not in [1, 2]:
            raise InvalidHardwareChannel("channel is not 1 or 2")
        if isinstance(channels, list) and 2 == len(channels) and channels[0] not in [1, 2]:
            raise InvalidHardwareChannel("channel is not 1 or 2")
        if isinstance(channels, list) and 2 == len(channels) and channels[1] not in [1, 2]:
            raise InvalidHardwareChannel("channel is not 1 or 2")
        if samples_per_channel < Audio005002Def.MINI_NUM:
            raise InvalidSampleCount("samples_per_channel is of bad value")
        if timeout < 0 or timeout > 10.0:
            raise InvalidTimeout("invalid timeout value")

        data_info = []
        start_time = time.time()
        while True:
            try:
                if isinstance(channels, list):
                    for i in range(len(channels)):
                        data = self._read_voltage_points(channels[i], samples_per_channel, int(timeout * 1000))
                        if len(channels) == 2:
                            data_info.append(data)
                        else:
                            data_info = data
                else:
                    data_info = self._read_voltage_points(channels, samples_per_channel, int(timeout * 1000))
                return data_info
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise InvalidTimeout("Timeout")
                if e.__class__.__name__ == 'Audio005002Exception':
                    raise Audio005002Exception("{}".format(str(e)))

    def write(self, channel, data, repeat):
        '''
        Playback a waveform defined by data array for "repeat" times. Output sample_rate must be setup by means
        configure_output_channel.

        Args:
            channel:  int,  [1, 2], currently defined are 1(playback).
            data:     list, unit mv, list of data samples in volt.
            repeat:   int,  number of repeats.

        Returns:
            string, "done", execution successful.
        '''
        assert len(data) >= Audio005002Def.MINI_NUM
        assert len(data) <= Audio005002Def.OUTPUT_MAX_NUM
        assert repeat >= Audio005002Def.MINI_NUM

        w_data = []
        for volt in data:
            volt = int(volt / Audio005002Def.OUTPUT_VOLT_MAX * pow(2, 23))
            if volt < 0:
                volt = pow(2, 24) + volt

            volt = volt << 8
            w_data.append(volt)

        ram_addr = 0
        self.ram_signal.read_disable()
        self.ram_signal.set_number_of_repeats([repeat])
        start_time = time.time()
        while ram_addr != (len(w_data) - 1):
            self.ram_signal.disable()
            # Due to the existence of capacitance, it is necessary to delay
            # the capacitor discharge for more than 32ms after the loss of energy
            time.sleep(Audio005002Def.OUTPUT_RELAY_DELAY_S)
            self.ram_signal.enable()

            self.ram_signal.set_read_ramend_addr(len(w_data) - 1)
            self.ram_signal.set_tx_data(w_data)
            ram_addr = self.ram_signal.get_write_ramend_addr()

            if time.time() - start_time > Audio005002Def.TIME_OUT:
                raise Audio005002Exception("write timeout")

        self.ram_signal.read_enable()

        return "done"
