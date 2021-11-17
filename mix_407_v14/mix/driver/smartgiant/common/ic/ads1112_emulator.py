# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'jihua.jiang@SmartGiant'
__version__ = '0.1'


class ADS1112EmulatorDef:
    RESET_CMD = [0x00, 0x06]
    SINGLE_MODE = 0x10
    SAMPLERATE = {15: 0x03, 30: 0x02, 60: 0x01, 240: 0x0}
    CHANNEL_MIN = 0
    CHANNEL_MAX = 3
    PGA_GAIN = [1, 2, 4, 8]
    DATA_RATE_TO_RESOLUTION = [0xfff, 0x3fff, 0x7fff, 0xffff]
    DATA_RATE_TO_MARK = [0x8000, 0x2000, 0x4000, 0x8000]
    DATA_RATE_TO_MINCODE = [2048, 8192, 16384, 32768]
    VREF = 2048.0
    COUNT_MIN = 1
    COUNT_MAX = 4096
    TIMEOUT = 1
    TIMEOUT_UNIT = 0.2
    ADC_DEV_SIZE = 256


class ADS1112Emulator(object):
    '''
    ADS1112 Emulator class
    '''

    def __init__(self, dev_name):
        self.dev_name = dev_name
        self._recorder = Recorder()
        add_recorder(self._recorder)

    def reset(self):
        '''
        reset internal register.

        Examples:
            ads1112.reset()
        '''
        self._recorder.record("%s write_config: 0x%02x" % (self.dev_name, ADS1112EmulatorDef.RESET_CMD))

    def disable_continuous_sampling(self):
        '''
        set single sample mode.

        Examples:
            ads1112.disable_continuous_sampling()
        '''
        self._recorder.record("%s write_config: disable continuous sampling" % self.dev_name)

    def enable_continuous_sampling(self, channel=0):
        '''
        set continuous sample mode.

        Args:
            channel: int(0-3), channel num table:
                +----------+--------+--------+
                | channel  |  VIN+  |  VIN-  |
                +==========+========+========+
                |  0       |  AIN0  |  AIN1  |
                +----------+--------+--------+
                |  1       |  AIN2  |  AIN3  |
                +----------+--------+--------+
                |  2       |  AIN0  |  AIN3  |
                +----------+--------+--------+
                |  3       |  AIN1  |  AIN3  |
                +----------+--------+--------+

        Examples:
            ret = ads1112.continue_sample_mode()
            # ret == True
        '''
        self._recorder.record("%s write_config: enable continuous sampling" % self.dev_name)

    def set_sampling_rate(self, samplerate):
        '''
        control the ADS1112 data rate.

        Args:
            samplerate: int(15,30,60,240), data rate, unit is sps.

        Returns:
            bool: True | False, True for success, False for failed.

        Examples:
            ret = ads1112.set_sampling_rate(15)
            # ret == True
        '''
        assert samplerate in ADS1112EmulatorDef.SAMPLERATE
        self._recorder.record("%s set sampling rate as %s" % (self.dev_name, samplerate))

    def get_sampling_rate(self):
        '''
        get the ADS1112 data rate.

        Returns:
            string/False: string for data rate, False for failed.

        Raise:
            ADS1112Exception: when read sampling rate error.

        Examples:
            ret = ads1112.get_sampling_rate()
            # ret == 15
        '''
        self._recorder.record("%s get sampling rate %s" % self.dev_name)

    def set_pga_gain(self, gain):
        '''
        she the pga gain.

        Args:
            gain: int(1,2,4,8), the pga gain.

        Returns:
            bool: True | False, True for success, False for failed.

        Examples:
            ret = ads1112.set_pga_gain(1)
            # ret == True
        '''
        assert gain in ADS1112EmulatorDef.PGA_GAIN
        self._recorder.record("%s write_config: set pga gain as %s" % (self.dev_name, gain))

    def read_volt(self, channel):
        '''
        get the single valtage.

        Args:
            channel: int(0-3), channel num table:
                +----------+--------+--------+
                | channel  |  VIN+  |  VIN-  |
                +==========+========+========+
                |  0       |  AIN0  |  AIN1  |
                +----------+--------+--------+
                |  1       |  AIN2  |  AIN3  |
                +----------+--------+--------+
                |  2       |  AIN0  |  AIN3  |
                +----------+--------+--------+
                |  3       |  AIN1  |  AIN3  |
                +----------+--------+--------+

        Returns:
            fload: voltage value, unit is mV.

        Raise:
            ADS1112Exception: when read single voltage time out.

        Examples:
            ret = ads1112.read_volt(0)
            # ret == 2112
        '''
        assert ADS1112EmulatorDef.CHANNEL_MIN <= channel <= ADS1112EmulatorDef.CHANNEL_MAX
        self._recorder.record("%s read voltage" % self.dev_name)
        return 1.0

    def get_continuous_sampling_voltage(self, count):
        '''
        get the continuous valtage.

        Args:
            count: int(1-4096), get count data value.

        Returns:
            list: float voltage value list, unit is mV.

        Examples:
            ret = ads1112.get_continuous_sampling_voltage(0)
            # ret == [23.312,23.122,...]
        '''
        assert ADS1112EmulatorDef.COUNT_MIN <= count <= ADS1112EmulatorDef.COUNT_MAX
        self._recorder.record("%s read %d continuous voltage" % (self.dev_name, count))

    def code_2_voltage(self, raw_data):
        '''
        get the single valtage.

        Args:
            raw_data: list, [output register upper byte,output register lower byte,configuration register]

        Returns:
            fload: voltage value, unit is mV.

        Examples:
            ret = ads1112.code_2_voltage([0x21,0x34,0x04])
            # ret == 2112
        '''
        # 3 bytes consist of list [output register upper byte,output register lower byte,configuration register]
        config_reg = raw_data[2]
        output_reg = raw_data[0] << 8 | raw_data[1]
        # bit2 and bit3 is data rate value.
        data_rate = (config_reg & 0x0c) >> 2
        # bit0 and bit1 is pga gain value.
        pga = config_reg & 0x03

        output_code = output_reg & ADS1112EmulatorDef.DATA_RATE_RESOLUTION[data_rate]

        # Output Code = −1 * Min Code * PGA * ((VIN+) - (VIN-))/2.048V
        volt = output_code / (ADS1112EmulatorDef.DATA_RATE_TO_MINCODE[data_rate] *
                              ADS1112EmulatorDef.PGA_GAIN[pga]) * ADS1112EmulatorDef.VREF

        return volt
