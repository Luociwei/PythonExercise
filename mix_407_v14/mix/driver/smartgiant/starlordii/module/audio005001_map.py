# -*- coding: utf-8 -*-
import time
import math
import bisect
from mix.driver.core.bus.pin import Pin
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.common.ic.pca9536 import PCA9536
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.ipcore.mix_audio005_sg_r import MIXAudio005SGR


__author__ = "dongdong.zhang@SmartGiant"
__version__ = "0.0.2"


starlordii_range_table = {
    "AUDIO_OUTPUT": 0,
    "AUDIO_20mV_left": 1,
    "AUDIO_20mV_right": 2,
    "AUDIO_2V_30Hz_left": 3,
    "AUDIO_2V_600Hz_left": 4,
    "AUDIO_2V_3000Hz_left": 5,
    "AUDIO_2V_5000Hz_left": 6,
    "AUDIO_2V_6000Hz_left": 7,
    "AUDIO_2V_7000Hz_left": 8,
    "AUDIO_2V_8000Hz_left": 9,
    "AUDIO_2V_9000Hz_left": 10,
    "AUDIO_2V_10000Hz_left": 11,
    "AUDIO_2V_11000Hz_left": 12,
    "AUDIO_2V_12000Hz_left": 13,
    "AUDIO_2V_13000Hz_left": 14,
    "AUDIO_2V_14000Hz_left": 15,
    "AUDIO_2V_15000Hz_left": 16,
    "AUDIO_2V_16000Hz_left": 17,
    "AUDIO_2V_17000Hz_left": 18,
    "AUDIO_2V_18000Hz_left": 19,
    "AUDIO_2V_19000Hz_left": 20,
    "AUDIO_2V_20000Hz_left": 21,
    "AUDIO_2V_30Hz_right": 22,
    "AUDIO_2V_600Hz_right": 23,
    "AUDIO_2V_3000Hz_right": 24,
    "AUDIO_2V_5000Hz_right": 25,
    "AUDIO_2V_6000Hz_right": 26,
    "AUDIO_2V_7000Hz_right": 27,
    "AUDIO_2V_8000Hz_right": 28,
    "AUDIO_2V_9000Hz_right": 29,
    "AUDIO_2V_10000Hz_right": 30,
    "AUDIO_2V_11000Hz_right": 31,
    "AUDIO_2V_12000Hz_right": 32,
    "AUDIO_2V_13000Hz_right": 33,
    "AUDIO_2V_14000Hz_right": 34,
    "AUDIO_2V_15000Hz_right": 35,
    "AUDIO_2V_16000Hz_right": 36,
    "AUDIO_2V_17000Hz_right": 37,
    "AUDIO_2V_18000Hz_right": 38,
    "AUDIO_2V_19000Hz_right": 39,
    "AUDIO_2V_20000Hz_right": 40
}


class Audio005Def:
    # the definition can be found in Driver ERS
    EEPROM_I2C_ADDR = 0x50
    TEMP_I2C_ADDR = 0x48
    PCA9536_DEV_ADDR = 0x41

    ADC_RESET_PIN = 0
    I2S_RX_EN_PIN = 1
    DAC_RESET_PIN = 8
    I2S_TX_EN_PIN = 9
    # audio measure, us pin2 and pin3 to select channel
    I2S_CH_SELECT_2 = 2
    I2S_CH_SELECT_3 = 3

    IO_DIR_OUTPUT = "output"
    PIN_LEVEL_LOW = 0
    PIN_LEVEL_HIGH = 1
    RELAY_DELAY_S = 0.01

    ADC_CH_RIGHT_CTL_BIT = 0
    ADC_CH_LEFT_CTL_BIT = 1
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
    SEL_GAIN_1 = 0
    SEL_GAIN_100 = 1
    DEF_SAMPLING_RATE = 48000

    SAMPLING_RANGE = [50001, 100001, 192001]
    ADCM_CTL_LIST = ([0, 0], [0, 1], [1, 0])

    # audio measure, which range used to do calibration, unit Hz
    CAL_RANGE = [30, 600, 3000, 5000, 6000, 7000, 8000, 9000, 10000, 11000,
                 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000, 400000]

    AUDIO_OUTPUT_ENABLE = 1
    AUDIO_OUTPUT_DISABLE = 0

    VOLT_UNIT_MV = "mV"
    VOLT_UNIT_RMS = "mVrms"
    FREQ_UNIT_HZ = "Hz"
    THD_UNIT_DB = "dB"
    THDN_UNIT_DB = "dB"

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
    # Hardware attenuation, The hardware engineer provides the parameters
    AUDIO_HARDWARE_ATTENUATION = 0.82
    # if scope is '2V', max rms is 2000 mVrms
    AUDIO_ANALYZER_2V_VREF = 2.0 * math.sqrt(2) * 2000
    # if scope is '20mV', max rms is 20 mVrms
    AUDIO_ANALYZER_20mV_VREF = 2.0 * math.sqrt(2) * 20

    RMS_TO_VPP_RATIO = 2.0 * math.sqrt(2)

    VPP_2_SCALE_RATIO = 0.999 / OUTPUT_VPP_MAX
    OUTPUT_CAL_ITEM = "AUDIO_OUTPUT"
    # unit S
    TIME_OUT = 1


class Audio005Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Audio005Base(SGModuleDriver):
    '''
    Audio005Base is a high resolution differential input/output digital audio module.

    Args:
        i2c:    instance(I2C), the instance of I2C bus. which will be used to used
                               to control eeprom, sensor and io expander.
        ipcore: instance(MIXAudio005SGR), the instance of MIXAudio005SGR, which include
                                    AD717x, FFT Analyzer, Signal Source and gpio
                                    function. If device name string is passed
                                    to the parameter, the ipcore can be instanced
                                    in the module.

    '''
    rpc_public_api = ['enable_upload', 'disable_upload', 'measure',
                      'enable_output', 'disable_output'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, ipcore, range_table=starlordii_range_table):

        self.eeprom = CAT24C32(Audio005Def.EEPROM_I2C_ADDR, i2c)
        self.nct75 = NCT75(Audio005Def.TEMP_I2C_ADDR, i2c)
        self.pca9536 = PCA9536(Audio005Def.PCA9536_DEV_ADDR, i2c)

        if isinstance(ipcore, basestring):
            ipcore = MIXAudio005SGR(ipcore)

        self.ipcore = ipcore
        self.analyzer = self.ipcore.analyzer
        self.signal_source = self.ipcore.signal_source
        self.adc_rst_pin = Pin(self.ipcore.gpio, Audio005Def.ADC_RESET_PIN)
        self.i2s_rx_en_pin = Pin(self.ipcore.gpio, Audio005Def.I2S_RX_EN_PIN)
        self.dac_rst_pin = Pin(self.ipcore.gpio, Audio005Def.DAC_RESET_PIN)
        self.i2s_tx_en_pin = Pin(self.ipcore.gpio, Audio005Def.I2S_TX_EN_PIN)
        self.i2s_ch_select = [Pin(self.ipcore.gpio, Audio005Def.I2S_CH_SELECT_2),
                              Pin(self.ipcore.gpio, Audio005Def.I2S_CH_SELECT_3)]

        super(Audio005Base, self).__init__(self.eeprom, self.nct75, range_table=range_table)
        self.is_enable_upload = False

    def post_power_on_init(self, timeout=Audio005Def.TIME_OUT):
        '''
        Init audio005 module to a know harware state.

        This function will reset reset dac/adc and i2s module.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        self.reset(timeout)

    def reset(self, timeout=Audio005Def.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()
        while True:
            try:
                self.adc_rst_pin.set_dir(Audio005Def.IO_DIR_OUTPUT)
                self.dac_rst_pin.set_dir(Audio005Def.IO_DIR_OUTPUT)
                self.i2s_rx_en_pin.set_dir(Audio005Def.IO_DIR_OUTPUT)
                self.i2s_tx_en_pin.set_dir(Audio005Def.IO_DIR_OUTPUT)

                # reset ADC
                self.adc_rst_pin.set_level(Audio005Def.PIN_LEVEL_LOW)
                time.sleep(Audio005Def.RELAY_DELAY_S)
                self.adc_rst_pin.set_level(Audio005Def.PIN_LEVEL_HIGH)

                # reset DAC
                self.dac_rst_pin.set_level(Audio005Def.PIN_LEVEL_LOW)
                time.sleep(Audio005Def.RELAY_DELAY_S)
                self.dac_rst_pin.set_level(Audio005Def.PIN_LEVEL_HIGH)

                # reset i2s rx
                self.i2s_rx_en_pin.set_level(Audio005Def.PIN_LEVEL_LOW)

                # reset i2s tx
                self.i2s_tx_en_pin.set_level(Audio005Def.PIN_LEVEL_LOW)

                # io init
                self.pca9536.set_pin_dir(Audio005Def.ADC_CH_RIGHT_CTL_BIT, Audio005Def.IO_DIR_OUTPUT)
                self.pca9536.set_pin_dir(Audio005Def.ADC_CH_LEFT_CTL_BIT, Audio005Def.IO_DIR_OUTPUT)
                self.pca9536.set_pin_dir(Audio005Def.ADCM0_CTL_BIT, Audio005Def.IO_DIR_OUTPUT)
                self.pca9536.set_pin_dir(Audio005Def.ADCM1_CTL_BIT, Audio005Def.IO_DIR_OUTPUT)

                self.pca9536.set_pin(Audio005Def.ADC_CH_RIGHT_CTL_BIT, Audio005Def.PIN_LEVEL_LOW)
                self.pca9536.set_pin(Audio005Def.ADC_CH_LEFT_CTL_BIT, Audio005Def.PIN_LEVEL_LOW)
                self.pca9536.set_pin(Audio005Def.ADCM0_CTL_BIT, Audio005Def.PIN_LEVEL_LOW)
                self.pca9536.set_pin(Audio005Def.ADCM1_CTL_BIT, Audio005Def.PIN_LEVEL_LOW)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise Audio005Exception("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=Audio005Def.TIME_OUT):
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
                    raise Audio005Exception("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get audio005 driver version.

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
        self.i2s_rx_en_pin.set_level(Audio005Def.I2S_RX_ENABLE)
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
        self.i2s_rx_en_pin.set_level(Audio005Def.I2S_RX_DISABLE)
        self.is_enable_upload = False

        return "done"

    def measure(self, channel, scope, bandwidth_hz, harmonic_count,
                decimation_type=0xFF, sampling_rate=Audio005Def.DEF_SAMPLING_RATE):
        '''
        Measure audio input signal, which captures data using CS5361.

        Args:
            channel:         string, ['left', 'right'], select input signal channel.
            scope:           string, ['2V', '20mV'], AD7175 measurement range.
            bandwidth_hz:    int/string, [42~48000], unit Hz, the signal bandwidth.
                             In theory the bandwidth must smaller than half the sampling rate.
                             eg, if sampling_rate = 192000, so bandwidth_hz  < 96000.
                             The bandwidth must be greater than the frequency of the input signal.
            harmonic_count:  int, [2~10], The harmonic count of signal.
                             The harmonic frequency is the frequency of the input signal times the counts of harmonics.
                             eg, The input is 20K, the first harmonic is 20K, the second harmonic is 40K,
                                 the third harmonic is 60K, the fourth harmonic is 80K, the fourth harmonic is 100K.
                             The harmonic frequency must be smaller than half the sampling rate.
                             eg, if sampling_rate = 192000, input_signal_frequency = 20000, harmonic_count = 4
                                 so harmonic_frequency = 80000 < 96000.
                             The signal bandwidth  must be greater than harmonic frequency.
            decimation_type: int, [1~255], default 0xFF, sample data decimation.
                             decimation_type is 1 means not to decimate.
                             The smaller the input frequency, the larger the value should be.
            sampling_rate:   int, [0~192000], default 48000, unit Hz, ADC sampling rate.

        Returns:
            dict, {'vpp': value, 'freq': value, 'thd': value, 'thdn': value, 'rms': value, 'noisefloor': value},
            measurement result.
        '''
        assert channel in Audio005Def.AUDIO_CHANNEL_LIST
        assert scope in Audio005Def.LNA_SCOPE

        if self.is_enable_upload is False:
            self.i2s_rx_en_pin.set_level(Audio005Def.I2S_RX_ENABLE)

        pin = self.i2s_ch_select[Audio005Def.SELECT_BIT0]
        pin.set_level(Audio005Def.AUDIO_CHANNEL_LIST[channel][Audio005Def.SELECT_BIT0])
        pin = self.i2s_ch_select[Audio005Def.SELECT_BIT1]
        pin.set_level(Audio005Def.AUDIO_CHANNEL_LIST[channel][Audio005Def.SELECT_BIT1])

        if scope == Audio005Def.LNA_RANGE_2V:
            self.pca9536.set_pin(Audio005Def.ADC_CH_LIST[channel], Audio005Def.SEL_GAIN_1)
            gain = Audio005Def.AUDIO_ANALYZER_2V_VREF / Audio005Def.AUDIO_HARDWARE_ATTENUATION
        else:
            self.pca9536.set_pin(Audio005Def.ADC_CH_LIST[channel], Audio005Def.SEL_GAIN_100)
            gain = Audio005Def.AUDIO_ANALYZER_20mV_VREF / Audio005Def.AUDIO_HARDWARE_ATTENUATION

        index = bisect.bisect(Audio005Def.SAMPLING_RANGE, sampling_rate)

        self.pca9536.set_pin(Audio005Def.ADCM0_CTL_BIT, Audio005Def.ADCM_CTL_LIST[index][Audio005Def.SELECT_BIT0])
        self.pca9536.set_pin(Audio005Def.ADCM1_CTL_BIT, Audio005Def.ADCM_CTL_LIST[index][Audio005Def.SELECT_BIT1])

        self.analyzer.disable()
        self.analyzer.enable()
        self.analyzer.analyze_config(sampling_rate, decimation_type, bandwidth_hz, harmonic_count)
        self.analyzer.analyze()

        freq = self.analyzer.get_frequency()
        vpp = self.analyzer.get_vpp() * gain
        rms = vpp / Audio005Def.RMS_TO_VPP_RATIO

        if scope == Audio005Def.LNA_RANGE_2V:
            index = bisect.bisect(Audio005Def.CAL_RANGE, freq)
            range_name = "AUDIO_2V_" + str(Audio005Def.CAL_RANGE[index]) + "Hz_" + channel
        else:
            range_name = "AUDIO_20mV_" + channel

        rms = self.calibrate(range_name, rms)
        vpp = rms * Audio005Def.RMS_TO_VPP_RATIO
        thdn_value = self.analyzer.get_thdn()

        result = dict()
        result["vpp"] = (vpp, Audio005Def.VOLT_UNIT_MV)
        result["freq"] = (freq, Audio005Def.FREQ_UNIT_HZ)
        result["thd"] = (self.analyzer.get_thd(), Audio005Def.THD_UNIT_DB)
        result["thdn"] = (thdn_value, Audio005Def.THDN_UNIT_DB)
        result["rms"] = (rms, Audio005Def.VOLT_UNIT_RMS)
        result["noisefloor"] = (10 ** (thdn_value / 20) * rms, Audio005Def.VOLT_UNIT_RMS)

        if self.is_enable_upload is False:
            self.i2s_rx_en_pin.set_level(Audio005Def.I2S_RX_DISABLE)

        return result

    def enable_output(self, freq, vpp):
        '''
        Audio005 CS5361 output audio sine waveform.

        Args:
            freq:       int, [5~50000], unit Hz, output signal's frequency.
            vpp:        float, [0~6504], unit mV, output signal's vpp.

        Returns:
            string, "done", execution successful.
        '''
        assert Audio005Def.OUTPUT_FREQ_MIN <= freq
        assert freq <= Audio005Def.OUTPUT_FREQ_MAX
        assert Audio005Def.OUTPUT_VPP_MIN <= vpp
        assert vpp <= Audio005Def.OUTPUT_VPP_MAX

        vpp = self.calibrate(Audio005Def.OUTPUT_CAL_ITEM, vpp)
        vpp = 0 if vpp < 0 else vpp
        # enable I2S tx module
        self.i2s_tx_en_pin.set_level(Audio005Def.AUDIO_OUTPUT_ENABLE)

        self.signal_source.close()
        self.signal_source.open()
        # calculate vpp to vpp scale for FPGA
        vpp_scale = vpp * Audio005Def.VPP_2_SCALE_RATIO
        self.signal_source.set_swg_paramter(Audio005Def.AUDIO_SAMPLING_RATE, freq,
                                            vpp_scale, Audio005Def.OUTPUT_SIGNAL_DUTY)
        self.signal_source.set_signal_type(Audio005Def.OUTPUT_WAVE)
        self.signal_source.set_signal_time(Audio005Def.SIGNAL_ALWAYS_OUTPUT)
        self.signal_source.output_signal()

        return "done"

    def disable_output(self):
        '''
        Disable Cs5361 output signal.

        Returns:
            string, "done", execution successful.
        '''
        self.signal_source.close()
        self.i2s_tx_en_pin.set_level(Audio005Def.AUDIO_OUTPUT_DISABLE)

        return "done"


class Audio005001(Audio005Base):
    '''
    Audio005001 is a high resolution differential input/output digital audio module.

    Args:
        i2c:    instance(I2C), the instance of I2C bus. which will be used to used
                               to control eeprom, sensor and io expander.
        ipcore: instance(MIXAudio005SGR), the instance of MIXAudio005SGR, which include
                                    AD717x, FFT Analyzer, Signal Source and gpio
                                    function. If device name string is passed
                                    to the parameter, the ipcore can be instanced
                                    in the module.

    Examples:
        i2c = I2C('/dev/i2c-0')
        audio005001 = Audio005001(i2c, '/dev/MIX_Audio005001_SG_R')
        audio005001.post_power_on_init()
        # measure left channel input
        result = audio005001.measure('left', '2V', 20000, 3)
        print("vpp={}, freq={}, thd={}, thdn={}, rms={}, noisefloor={}".format(result['vpp'],
              result['freq'], result['thd'], result['thdn'], result['rms'],
              result['noisefloor']))

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-03C6-5-010"]

    def __init__(self, i2c, ipcore):
        super(Audio005001, self).__init__(i2c, ipcore)
