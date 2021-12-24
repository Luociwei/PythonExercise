# -*- coding: utf-8 -*-
import time
import math
import functools
from mix.driver.core.bus.pin import Pin
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.common.ic.pca9536 import PCA9536
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.ipcore.mix_aut5_sg_r import MIXAUT5SGR


__author__ = "dongdong.zhang@SmartGiant"
__version__ = "0.1.4"


starlord_table = {
    "AUDIO_OUTPUT": 0,
    "AUDIO_CS5361_RMS_left": 1,
    "AUDIO_CS5361_RMS_right": 2,
    "LNA_50mV_left": 3,
    "LNA_50mV_right": 4,
    "LNA_5V_left": 5,
    "LNA_5V_right": 6
}


class StarLordDef:
    # the definition can be found in Driver ERS
    EEPROM_I2C_ADDR = 0x50
    TEMP_I2C_ADDR = 0x48
    PCA9536_DEV_ADDR = 0x41

    AD7175_CH_LIST = {"right": 0, "left": 1}
    CH_LEFT = "left"
    LNA_SCOPE = ("5V", "50mV")
    LNA_RANGE_5V = "5V"

    AD7175_CH_LEFT_CTL_BIT = 1
    AD7175_CH_RIGHT_CTL_BIT = 0
    SEL_GAIN_1 = 0
    SEL_GAIN_100 = 1

    IO_DIR_OUTPUT = "output"

    AUDIO_OUTPUT_ENABLE = 1
    AUDIO_OUTPUT_DISABLE = 0

    AUDIO_CHANNEL_LIST = {"left": [0, 0], "right": [1, 0]}
    AUDIO_CHANNEL_SELECT_BIT0 = 0
    AUDIO_CHANNEL_SELECT_BIT1 = 1
    RELAY_DELAY_S = 0.01
    EMULATOR_REG_SIZE = 256
    VOLT_UNIT_MV = "mV"
    VOLT_UNIT_RMS = "mVrms"
    FREQ_UNIT_HZ = "Hz"
    THD_UNIT_DB = "dB"
    THDN_UNIT_DB = "dB"

    AUDIO_SAMPLING_RATE = 192000
    LNA_SAMPLING_RATE = 250000
    SIGNAL_ALWAYS_OUTPUT = 0xffffffff
    # output signal range defined in HW Spec
    OUTPUT_SIGNAL_DUTY = 0.5
    OUTPUT_FREQ_MIN = 5
    OUTPUT_FREQ_MAX = 50000
    OUTPUT_VPP_MIN = 0
    # OUTPUT_RMS_MAX(2300) * 2 * math.sqrt(2)
    OUTPUT_VPP_MAX = 2300 * 2 * math.sqrt(2)
    # this can be found in HW spec
    # max rms is 2000 mVrms
    AUDIO_ANALYZER_VREF = 2 * math.sqrt(2) * 2000
    RMS_TO_VPP_RATIO = 2.0 * math.sqrt(2)

    OUTPUT_WAVE = "sine"
    VPP_2_SCALE_RATIO = 0.999 / OUTPUT_VPP_MAX
    OUTPUT_CAL_ITEM = "AUDIO_OUTPUT"
    FFT_SOURCE_FROM_CS5361 = 0
    FFT_SOURCE_FROM_AD7175 = 1

    AD7175_UPLOAD_TO_FFT = "fft"
    AD7175_UPLOAD_CH = {"dma": 0, "fft": 1}
    I2S_RX_ENABLE = 1
    I2S_RX_DISABLE = 0

    ADC_RESET_PIN = 0
    I2S_RX_EN_PIN = 1
    DAC_RESET_PIN = 8
    I2S_TX_EN_PIN = 9
    # audio measure, us pin2 and pin3 to select channel
    I2S_CH_SELECT_2 = 2
    I2S_CH_SELECT_3 = 3
    FFT_SOURCE_SELECT = 4
    AD7175_TO_FFT_OR_NOT = 5
    # gain is 1 or 100 is fpga defined
    GAIN_VALUE = {"5V": 10000 / 1, "50mV": 10000 / 100}
    # unit S
    TIME_OUT = 1


class StarLordException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class StarLordBase(SGModuleDriver):
    '''
    StarLordBase is a high resolution differential input digital audio analyzer module

    Args:
        i2c:    instance(I2C), the instance of I2C bus. which will be used to used
                               to control eeprom, sensor and io expander.
        ipcore: instance(MIXAUT5SGR), the instance of MIXAUT5SGR, which include
                                    AD717x, FFT Analyzer, Signal Source and gpio
                                    function. If device name string is passed
                                    to the parameter, the ipcore can be instanced
                                    in the module.

    '''
    rpc_public_api = ['enable_upload', 'disable_upload', 'measure',
                      'enable_output', 'disable_output', 'measure_lna',
                      'enable_lna_upload', 'disable_lna_upload', 'config_lna_scope'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, ipcore, range_table=starlord_table):

        self.eeprom = CAT24C32(StarLordDef.EEPROM_I2C_ADDR, i2c)
        self.nct75 = NCT75(StarLordDef.TEMP_I2C_ADDR, i2c)
        self.pca9536 = PCA9536(StarLordDef.PCA9536_DEV_ADDR, i2c)

        if isinstance(ipcore, basestring):
            ipcore = MIXAUT5SGR(ipcore)

        self.ipcore = ipcore
        self.analyzer = self.ipcore.analyzer
        self.signal_source = self.ipcore.signal_source
        self.ad7175 = self.ipcore.ad717x
        self.ad7175.config = {
            'ch0': {'P': 'AIN0', 'N': 'AIN1'},
            'ch1': {'P': 'AIN2', 'N': 'AIN3'}
        }
        self.adc_rst_pin = Pin(self.ipcore.gpio, StarLordDef.ADC_RESET_PIN)
        self.i2s_rx_en_pin = Pin(self.ipcore.gpio, StarLordDef.I2S_RX_EN_PIN)
        self.dac_rst_pin = Pin(self.ipcore.gpio, StarLordDef.DAC_RESET_PIN)
        self.i2s_tx_en_pin = Pin(self.ipcore.gpio, StarLordDef.I2S_TX_EN_PIN)
        self.i2s_ch_select = [Pin(self.ipcore.gpio, StarLordDef.I2S_CH_SELECT_2),
                              Pin(self.ipcore.gpio, StarLordDef.I2S_CH_SELECT_3)]
        self.fft_source_select = Pin(self.ipcore.gpio, StarLordDef.FFT_SOURCE_SELECT)
        self.ad7175_upload_select = Pin(self.ipcore.gpio, StarLordDef.AD7175_TO_FFT_OR_NOT)

        super(StarLordBase, self).__init__(self.eeprom, self.nct75, range_table=range_table)
        self.is_lna_up = False
        self.is_analyzer_up = False
        self.is_enable_upload = False

    def post_power_on_init(self, timeout=StarLordDef.TIME_OUT):
        '''
        Init starLord module to a know harware state.

        This function will reset dac/adc, i2s module and load calibration

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        self.reset(timeout)

    def reset(self, timeout=StarLordDef.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()
        while True:
            try:
                self.adc_rst_pin.set_dir(StarLordDef.IO_DIR_OUTPUT)
                self.dac_rst_pin.set_dir(StarLordDef.IO_DIR_OUTPUT)
                self.i2s_rx_en_pin.set_dir(StarLordDef.IO_DIR_OUTPUT)
                self.i2s_tx_en_pin.set_dir(StarLordDef.IO_DIR_OUTPUT)
                self.i2s_ch_select[StarLordDef.AUDIO_CHANNEL_SELECT_BIT0].set_dir(StarLordDef.IO_DIR_OUTPUT)
                self.i2s_ch_select[StarLordDef.AUDIO_CHANNEL_SELECT_BIT1].set_dir(StarLordDef.IO_DIR_OUTPUT)
                self.fft_source_select.set_dir(StarLordDef.IO_DIR_OUTPUT)
                self.ad7175_upload_select.set_dir(StarLordDef.IO_DIR_OUTPUT)

                # reset ADC
                self.adc_rst_pin.set_level(0)
                time.sleep(StarLordDef.RELAY_DELAY_S)
                self.adc_rst_pin.set_level(1)

                # reset DAC
                self.dac_rst_pin.set_level(0)
                time.sleep(StarLordDef.RELAY_DELAY_S)
                self.dac_rst_pin.set_level(1)

                # reset i2s rx
                self.i2s_rx_en_pin.set_level(0)

                # reset i2s tx
                self.i2s_tx_en_pin.set_level(0)

                # io init
                self.pca9536.set_pin_dir(StarLordDef.AD7175_CH_LEFT_CTL_BIT, StarLordDef.IO_DIR_OUTPUT)
                self.pca9536.set_pin_dir(StarLordDef.AD7175_CH_RIGHT_CTL_BIT, StarLordDef.IO_DIR_OUTPUT)

                self.pca9536.set_pin(StarLordDef.AD7175_CH_LEFT_CTL_BIT, 0)
                self.pca9536.set_pin(StarLordDef.AD7175_CH_RIGHT_CTL_BIT, 0)

                # ad7175 init
                self.ad7175.channel_init()

                # measure lna config init
                self.config_lna_scope(StarLordDef.CH_LEFT, StarLordDef.LNA_RANGE_5V)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise StarLordException("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=StarLordDef.TIME_OUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set pca9536 io direction to output and set pin level to 0.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()
        while True:
            try:
                self.adc_rst_pin.set_level(0)
                self.i2s_rx_en_pin.set_level(0)
                self.dac_rst_pin.set_level(0)
                self.i2s_tx_en_pin.set_level(0)
                self.signal_source.close()
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise StarLordException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get starLord driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def enable_upload(self):
        '''
        Enable module data upload.

        Returns:
            string, "done", execution successful.
        '''
        self.i2s_rx_en_pin.set_level(StarLordDef.I2S_RX_ENABLE)
        self.analyzer.enable_upload()
        self.is_enable_upload = True

        return "done"

    def disable_upload(self):
        '''
        Disable module data upload.

        Returns:
            string, "done", execution successful.
        '''
        self.analyzer.disable_upload()
        self.i2s_rx_en_pin.set_level(StarLordDef.I2S_RX_DISABLE)
        self.is_enable_upload = False

        return "done"

    def measure(self, channel, bandwidth_hz, harmonic_count,
                decimation_type=0xFF, sampling_rate=StarLordDef.AUDIO_SAMPLING_RATE):
        '''
        Measure audio input signal, which captures data using CS5361.

        Args:
            channel:         string, ['left', 'right'], select input signal channel.
            bandwidth_hz:    int/string, [42~48000], unit Hz, the signal bandwidth.
            harmonic_count:  int, [2~10], The harmonic count of signal.
            decimation_type: int, [1~255], default 0xFF, sample data decimation.
            sampling_rate:   int, [1~192000], default 192000, unit Hz, ADC sampling rate.

        Returns:
            dict, {'vpp': value, 'freq': value, 'thd': value, 'thdn': value, 'rms': value, 'noisefloor': value},
            measurement result.
        '''
        assert channel in StarLordDef.AUDIO_CHANNEL_LIST

        if self.is_enable_upload is False:
            self.i2s_rx_en_pin.set_level(StarLordDef.I2S_RX_ENABLE)

        pin = self.i2s_ch_select[StarLordDef.AUDIO_CHANNEL_SELECT_BIT0]
        pin.set_level(StarLordDef.AUDIO_CHANNEL_LIST[channel][StarLordDef.AUDIO_CHANNEL_SELECT_BIT0])
        pin = self.i2s_ch_select[StarLordDef.AUDIO_CHANNEL_SELECT_BIT1]
        pin.set_level(StarLordDef.AUDIO_CHANNEL_LIST[channel][StarLordDef.AUDIO_CHANNEL_SELECT_BIT1])

        self.fft_source_select.set_level(StarLordDef.FFT_SOURCE_FROM_CS5361)

        result = self._analyzer(sampling_rate, decimation_type, bandwidth_hz, harmonic_count)

        range_name = "AUDIO_CS5361_RMS_" + channel

        result['rms'] = (self.calibrate(range_name, result['rms'][0]), StarLordDef.VOLT_UNIT_RMS)

        if self.is_enable_upload is False:
            self.i2s_rx_en_pin.set_level(StarLordDef.I2S_RX_DISABLE)

        return result

    def config_lna_scope(self, channel, scope, adc_upload_ch=StarLordDef.AD7175_UPLOAD_TO_FFT):
        '''
        Config LNA measurement scope

        Args:
            channel:        string, ['left', 'right'], the channel to be upload.
            scope:          string, ['5V', '50mV'], AD7175 measurement range.
            adc_upload_ch:  string, ['dma', 'fft'], default 'fft', AD7175 source data is uploaded to DMA or FFT.

        Returns:
            string, "done",  execution successful.
        '''
        assert channel in StarLordDef.AD7175_CH_LIST
        assert scope in StarLordDef.LNA_SCOPE
        assert adc_upload_ch in StarLordDef.AD7175_UPLOAD_CH

        self.channel = channel
        self.scope = scope
        if scope == StarLordDef.LNA_RANGE_5V:
            self.pca9536.set_pin(StarLordDef.AD7175_CH_LIST[channel], StarLordDef.SEL_GAIN_1)
        else:
            self.pca9536.set_pin(StarLordDef.AD7175_CH_LIST[channel], StarLordDef.SEL_GAIN_100)

        self.ad7175_upload_select.set_level(StarLordDef.AD7175_UPLOAD_CH[adc_upload_ch])

        return "done"

    def enable_lna_upload(self, channel, sampling_rate=StarLordDef.LNA_SAMPLING_RATE):
        '''
        Enable LNA adc data upload

        Args:
            channel:        string, ['left', 'right'], the channel to be upload.
            sampling_rate:  float, default 250000, unit Hz, AD7175 sampling rate,
                                   please refer to datasheet for more information.

        Returns:
            string, "done",  execution successful.
        '''
        assert channel in StarLordDef.AD7175_CH_LIST

        self.is_lna_up = True
        self.ad7175.disable_continuous_sampling(StarLordDef.AD7175_CH_LIST[channel])
        time.sleep(StarLordDef.RELAY_DELAY_S)

        self.ad7175.enable_continuous_sampling(StarLordDef.AD7175_CH_LIST[channel], sampling_rate)

        return "done"

    def disable_lna_upload(self, channel):
        '''
        Disable LNA adc data upload

        Args:
            channel:        string, ['left', 'right'], the channel to be upload.

        Returns:
            string, "done", execution successful.
        '''
        assert channel in StarLordDef.AD7175_CH_LIST

        self.is_lna_up = False
        if self.is_analyzer_up is True:
            self.analyzer.disable_upload()
            self.is_analyzer_up = False

        self.ad7175.disable_continuous_sampling(StarLordDef.AD7175_CH_LIST[channel])

        return "done"

    def measure_lna(self, bandwidth_hz, harmonic_count,
                    decimation_type=0xFF, sampling_rate=StarLordDef.LNA_SAMPLING_RATE):
        '''
        Measure audio LNA input signal, which captures data using AD7175.

        Args:
            bandwidth_hz:    int/string, [42~48000], unit Hz, the signal bandwidth.
            harmonic_count:  int, [2~10], The harmonic count of signal.
            decimation_type: int, [1~255], default 0xFF, sample data decimation.
            sampling_rate:   int, [5~250000], default 250000, unit Hz,
                                  Sample rate of your ADC device.

        Returns:
            dict, {'vpp': value, 'freq': value, 'thd': value, 'thdn': value, 'rms': value, 'noisefloor': value},
            measurement result.
        '''
        self.fft_source_select.set_level(StarLordDef.FFT_SOURCE_FROM_AD7175)

        if self.is_lna_up is True and self.is_analyzer_up is False:
            self.analyzer.enable_upload()
            self.is_analyzer_up = True

        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(sampling_rate, decimation_type, bandwidth_hz, harmonic_count)
        self.analyzer.analyze()

        range_name = "LNA_" + self.scope + "_" + self.channel
        gain = StarLordDef.GAIN_VALUE[self.scope]
        vpp = self.analyzer.get_vpp() * gain
        rms = vpp / StarLordDef.RMS_TO_VPP_RATIO
        rms = self.calibrate(range_name, rms)
        thdn_value = self.analyzer.get_thdn()

        result = dict()
        result["vpp"] = (vpp, StarLordDef.VOLT_UNIT_MV)
        result["freq"] = (self.analyzer.get_frequency(), StarLordDef.FREQ_UNIT_HZ)
        result["thd"] = (self.analyzer.get_thd(), StarLordDef.THD_UNIT_DB)
        result["thdn"] = (thdn_value, StarLordDef.THDN_UNIT_DB)
        result["rms"] = (rms, StarLordDef.VOLT_UNIT_RMS)
        result["noisefloor"] = (10 ** (thdn_value / 20) * rms, StarLordDef.VOLT_UNIT_RMS)

        return result

    def enable_output(self, freq, vpp):
        '''
        StarLord CS5361 output audio sine waveform.

        Args:
            freq:       int, [5~50000], unit Hz, output signal's frequency.
            vpp:        float, [0~6504], unit mV, output signal's vpp.

        Returns:
            string, "done", execution successful.
        '''
        assert StarLordDef.OUTPUT_FREQ_MIN <= freq
        assert freq <= StarLordDef.OUTPUT_FREQ_MAX
        assert StarLordDef.OUTPUT_VPP_MIN <= vpp
        assert vpp <= StarLordDef.OUTPUT_VPP_MAX

        vpp = self.calibrate(StarLordDef.OUTPUT_CAL_ITEM, vpp)
        vpp = 0 if vpp < 0 else vpp
        # enable I2S tx module
        self.i2s_tx_en_pin.set_level(StarLordDef.AUDIO_OUTPUT_ENABLE)

        self.signal_source.close()
        self.signal_source.open()
        # calculate vpp to vpp scale for FPGA
        vpp_scale = vpp * StarLordDef.VPP_2_SCALE_RATIO
        self.signal_source.set_swg_paramter(StarLordDef.AUDIO_SAMPLING_RATE, freq,
                                            vpp_scale, StarLordDef.OUTPUT_SIGNAL_DUTY)
        self.signal_source.set_signal_type(StarLordDef.OUTPUT_WAVE)
        self.signal_source.set_signal_time(StarLordDef.SIGNAL_ALWAYS_OUTPUT)
        self.signal_source.output_signal()

        return "done"

    def disable_output(self):
        '''
        Disable Cs5361 output signal.

        Returns:
            string, "done", execution successful.
        '''
        self.signal_source.close()
        self.i2s_tx_en_pin.set_level(StarLordDef.AUDIO_OUTPUT_DISABLE)

        return "done"

    def _analyzer(self, sampling_rate, decimation_type, bandwidth_hz, harmonic_count):
        '''
        Measure audio input signal.

        Returns:
            dict, {'vpp': value, 'freq': value, 'thd': value, 'thdn': value, 'rms': value, 'noisefloor': value},
            measurement result.
        '''
        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(sampling_rate, decimation_type, bandwidth_hz, harmonic_count)
        self.analyzer.analyze()

        # calculate the actual vpp of HW by VREF
        vpp = self.analyzer.get_vpp() * StarLordDef.AUDIO_ANALYZER_VREF
        # vpp = RMS * 2 * sqrt(2)
        rms = vpp / StarLordDef.RMS_TO_VPP_RATIO
        vpp = rms * StarLordDef.RMS_TO_VPP_RATIO
        thdn_value = self.analyzer.get_thdn()

        result = dict()
        result["vpp"] = (vpp, StarLordDef.VOLT_UNIT_MV)
        result["freq"] = (self.analyzer.get_frequency(), StarLordDef.FREQ_UNIT_HZ)
        result["thd"] = (self.analyzer.get_thd(), StarLordDef.THD_UNIT_DB)
        result["thdn"] = (thdn_value, StarLordDef.THDN_UNIT_DB)
        result["rms"] = (rms, StarLordDef.VOLT_UNIT_RMS)
        result["noisefloor"] = (10 ** (thdn_value / 20) * rms, StarLordDef.VOLT_UNIT_RMS)

        return result


class StarLord(StarLordBase):
    '''
    StarLord is a high resolution differential input digital audio analyzer module

    Args:
        i2c:    instance(I2C), the instance of I2C bus. which will be used to used
                               to control eeprom, sensor and io expander.
        ipcore: instance(MIXAUT5SGR), the instance of MIXAUT5SGR, which include
                                    AD717x, FFT Analyzer, Signal Source and gpio
                                    function. If device name string is passed
                                    to the parameter, the ipcore can be instanced
                                    in the module.

    Examples:
        i2c = I2C('/dev/i2c-2')
        starlord = StarLord(i2c, '/dev/MIX_AUT5_SG_R_0')
        starlord.post_power_on_init()
        # measure left channel input
        result = starlord.measure('left', 20000, 3)
        print("vpp={}, freq={}, thd={}, thdn={}, rms={}, noisefloor={}".format(result['vpp'],
              result['freq'], result['thd'], result['thdn'], result['rms'], result['noisefloor']))

        # measure LNA signal
        starlord.config_lna_scope('right', '5V')
        starlord.enable_lna_upload('right', 250000)
        result = starlord.measure_lna(20000, 3, 1, 250000)
        print("vpp={}, freq={}, thd={}, thdn={}, rms={}, noisefloor={}".format(result['vpp'],
              result['freq'], result['thd'], result['thdn'], result['rms'], result['noisefloor']))

        # output audio sine waveform
        audio.enable_output(100, 50)
        audio.disable_output()
    '''
    compatible = ['GQQ-Q1QN-5-020']

    def __init__(self, i2c, ipcore):
        super(StarLord, self).__init__(i2c, ipcore)
