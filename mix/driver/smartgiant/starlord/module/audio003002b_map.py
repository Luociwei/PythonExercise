# -*- coding: utf-8 -*-
import bisect
from mix.driver.smartgiant.starlord.module.starlord_map import StarLordBase, StarLordDef

__author__ = 'zhangdongdong@SmartGiant'
__version__ = '0.1.4'


starlord_table = {
    "AUDIO_OUTPUT": 0,
    "LNA_50mV_left": 1,
    "LNA_50mV_right": 2,
    "LNA_5V_left": 3,
    "LNA_5V_right": 4,
    "AUDIO_30Hz_RMS_left": 5,
    "AUDIO_600Hz_RMS_left": 6,
    "AUDIO_3000Hz_RMS_left": 7,
    "AUDIO_5000Hz_RMS_left": 8,
    "AUDIO_6000Hz_RMS_left": 9,
    "AUDIO_7000Hz_RMS_left": 10,
    "AUDIO_8000Hz_RMS_left": 11,
    "AUDIO_9000Hz_RMS_left": 12,
    "AUDIO_10000Hz_RMS_left": 13,
    "AUDIO_11000Hz_RMS_left": 14,
    "AUDIO_12000Hz_RMS_left": 15,
    "AUDIO_13000Hz_RMS_left": 16,
    "AUDIO_14000Hz_RMS_left": 17,
    "AUDIO_15000Hz_RMS_left": 18,
    "AUDIO_16000Hz_RMS_left": 19,
    "AUDIO_17000Hz_RMS_left": 20,
    "AUDIO_18000Hz_RMS_left": 21,
    "AUDIO_19000Hz_RMS_left": 22,
    "AUDIO_20000Hz_RMS_left": 23,
    "AUDIO_30Hz_RMS_right": 24,
    "AUDIO_600Hz_RMS_right": 25,
    "AUDIO_3000Hz_RMS_right": 26,
    "AUDIO_5000Hz_RMS_right": 27,
    "AUDIO_6000Hz_RMS_right": 28,
    "AUDIO_7000Hz_RMS_right": 29,
    "AUDIO_8000Hz_RMS_right": 30,
    "AUDIO_9000Hz_RMS_right": 31,
    "AUDIO_10000Hz_RMS_right": 32,
    "AUDIO_11000Hz_RMS_right": 33,
    "AUDIO_12000Hz_RMS_right": 34,
    "AUDIO_13000Hz_RMS_right": 35,
    "AUDIO_14000Hz_RMS_right": 36,
    "AUDIO_15000Hz_RMS_right": 37,
    "AUDIO_16000Hz_RMS_right": 38,
    "AUDIO_17000Hz_RMS_right": 39,
    "AUDIO_18000Hz_RMS_right": 40,
    "AUDIO_19000Hz_RMS_right": 41,
    "AUDIO_20000Hz_RMS_right": 42
}


class Audio003002BDef:
    # audio measure, which range used to do calibration, unit Hz
    CAL_RANGE = [30, 600, 3000, 5000, 6000, 7000, 8000, 9000, 10000, 11000,
                 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000, 400000]


class Audio003002B(StarLordBase):
    '''
    Audio003002B is a high resolution differential input digital audio analyzer module

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
        audio = Audio003002B(i2c, '/dev/MIX_AUT5_SG_R_0')
        audio.post_power_on_init()
        # measure left channel input
        result = audio.measure('left', 20000, 3)
        print("vpp={}, freq={}, thd={}, thdn={}, rms={}, noisefloor={}".format(result['vpp'],
              result['freq'], result['thd'], result['thdn'], result['rms'], result['noisefloor']))

        # measure LNA signal
        audio.config_lna_scope('left', '5V')
        audio.enable_lna_upload('left', 250000)
        result = audio.measure_lna(20000, 3, 1, 250000)
        print("vpp={}, freq={}, thd={}, thdn={}, rms={}, noisefloor={}".format(result['vpp'],
              result['freq'], result['thd'], result['thdn'], result['rms'], result['noisefloor']))

        # output audio sine waveform
        audio.enable_output(100, 50)
        audio.disable_output()
    '''
    compatible = ['GQQ-Q1QN-5-02B']

    def __init__(self, i2c, ipcore):
        super(Audio003002B, self).__init__(i2c, ipcore, starlord_table)

    def measure(self, channel, bandwidth_hz, harmonic_count,
                decimation_type=0xFF, sampling_rate=StarLordDef.AUDIO_SAMPLING_RATE):
        '''
        Measure audio input signal, which captures data using CS5361.

        Args:
            channel:         string, ['left', 'right'], select input signal channel.
            bandwidth_hz:    int, [42~48000], unit Hz, the signal bandwidth.
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

        index = bisect.bisect(Audio003002BDef.CAL_RANGE, result['freq'][0])
        range_name = "AUDIO_" + str(Audio003002BDef.CAL_RANGE[index]) + "Hz_RMS_" + channel
        result['rms'] = (self.calibrate(range_name, result['rms'][0]), StarLordDef.VOLT_UNIT_RMS)

        if self.is_enable_upload is False:
            self.i2s_rx_en_pin.set_level(StarLordDef.I2S_RX_DISABLE)

        return result
