# -*- coding: utf-8 -*-
from mix.driver.smartgiant.starlord.module.starlord_map import StarLordBase

__author__ = 'zhangdongdong@SmartGiant'
__version__ = '0.1.4'


starlord_table = {
    "AUDIO_OUTPUT": 0,
    "AUDIO_CS5361_RMS_left": 1,
    "AUDIO_CS5361_RMS_right": 2,
    "LNA_50mV_left": 3,
    "LNA_50mV_right": 4,
    "LNA_5V_left": 5,
    "LNA_5V_right": 6
}


class Audio003002A(StarLordBase):
    '''
    Audio003002A is a high resolution differential input digital audio analyzer module

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
        audio = Audio003002A(i2c, '/dev/MIX_AUT5_SG_R_0')
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
    compatible = ['GQQ-Q1QN-5-02A']

    def __init__(self, i2c, ipcore):
        super(Audio003002A, self).__init__(i2c, ipcore, starlord_table)
