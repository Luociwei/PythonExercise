# -*- coding: UTF-8 -*-
from mix.driver.core.tracer.recorder import *


__author__ = 'tufeng.Mao@SmartGiant'
__version__ = '0.1'


class LTC2378Emulator(object):
    '''
    LTC2378 Emulator class
    '''

    def __init__(self, dev_name='ltc2378'):
        self.dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def measure_rms_average_amplitude_max_min(self, sample_rate, sample_time,
                                              upload_adc_data,
                                              sample_interval, upframe_mode):
        '''
        LTC2378 class provide function to measure rms average amplitude max min

        Args:
            sample_rate:     int, unit Hz.
            sample_time:     int, [1~0xFFFFFFFF], unit ms.
            upload_adc_data: string, ['off', 'on'], if upload is 'on' , then upload the raw data from ADC to DMA.
                                                    else disable the function.
            sample_interval: int, unit ms, less sample time.
            upframe_mode:    string, ['DEBUG', 'BYPASS'], choose mode.

        Returns:
            dict, {"rms": value, "avg": value, "vpp": value, "max": value, "min": value}, unit mV,
                  ret.rms,ret.average,ret.amp,ret.max,ret.min.

        Examples:
            ret = LTC2378.measure_rms_average_amplitude_max_min(256000, 1000, 'on', 500, 'DEBUG')

        '''
        assert isinstance(sample_rate, int)
        assert isinstance(sample_time, int)
        assert isinstance(upload_adc_data, str)
        assert isinstance(sample_interval, int)
        assert isinstance(upframe_mode, str)
        rms = 1000.0
        average = 1000.0
        max = 1000.0
        min = 1000.0
        vpp = max - min
        self._recorder.record("%s measure rms, average, amplitude, max and min" % (self.dev_name))
        return {'rms': rms, 'avg': average, 'vpp': vpp, 'max': max, 'min': min}

    def read_volt(self, channel=0):
        '''
        LTC2378 read the adc voltage

        Args:
            channel: int, [0], channel must be 0.

        Returns:
            float, value, unit mV.

        Examples:
            voltage = ltc2378.read_volt(0)

        '''
        assert channel == 0
        voltage = 1000.0
        self._recorder.record("%s read the adc voltage" % (self.dev_name))
        return voltage

    def measure_thdn(self, bandwidth_hz=20000, sample_rate=192000,
                     decimation_type='auto', upload='off',
                     harmonic_count=8, *measure_type):
        '''
        LTC2378 class provide function to measure thdn

        Args:
            bandwidth_hz:    int, [0~20000], default 20000, unit Hz.
            sample_rate:     int, [0~1000000, default 192000, unit sps.
            decimation_type: int, [1~255], default 0xFF, it means auto decimation.

            upload:          string, ['off', 'on'], default 'off', if upload is 'on' ,
                                     then upload the raw data from ADC to DMA, else disable the function.
            harmonic_count:  int, [1~10]|None, Default 8, if it is None, it will not do calculate.

        Returns:
            dict, {"freq": value, "vpp": value, "thd": value, "thdn": value},
                  ret.freq,unit is Hz,ret.thdn,unit is dB,ret.thd,unit is dB, ret.vpp,unit is mV.

        Raises:
            LTC2378Exception:open audio upload function fail!

        Examples:
            ret = LTC2378.measure_thdn('auto', 192000, 0xFF, 8)

        '''
        assert type(bandwidth_hz) is int
        assert type(sample_rate) is int
        assert 1 <= decimation_type <= 255
        assert type(upload) is str or type(upload) is unicode
        assert type(harmonic_count) is int
        freq = 0
        vpp = 0
        thd = 0
        thdn = 0
        self._recorder.record("%s measure thdn" % (self.dev_name))
        return {'freq': freq, 'vpp': vpp * 2, 'thd': thd, 'thdn': thdn}
