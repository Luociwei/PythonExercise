# -*- coding: utf-8 -*-
import time

__version__ = "1.0"
__author__ = 'jihua.jiang'


class ADS1112Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class ADS1112Def:
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
    ST_DRDY_SET = 0x80
    CONV_MODE = ['single', 'continuous']


class ADS1112(object):
    '''
    ADS1112 Driver:
        The ADS1112 is a precision, continuously self–calibrating Analog-to-Digital
        (A/D) converter with two differential or three single–ended channels and
        up to 16 bits of resolution. The onboard 2.048V reference provides an input
        range of ±2.048V differentially.

        address config info:
        +---------+--------+
        | A0 | A1 |  ADDR  |
        +==========+=======+
        | 0  |  0 |  0x48  |
        +---------+--------+
        | 0  |  N |  0x49  |
        +---------+--------+
        | 0  |  1 |  0x4a  |
        +---------+--------+
        | 1  |  0 |  0x4c  |
        +---------+--------+
        | 1  |  N |  0x4d  |
        +---------+--------+
        | 1  |  1 |  0x4e  |
        +---------+--------+
        | N  |  0 |  0x4b  |
        +---------+--------+
        | N  |  1 |  0x4f  |
        +---------+--------+
        | N  |  N |Invalid |
        +---------+--------+

    ClassType = ADC

    Args:
        dev_addr:    hexmial,             ads1115 i2c bus device address.
        i2c_bus:     instance(I2C)/None,  i2c bus class instance, if not using, will create emulator.

    Examples:
        i2c_bus = I2C('/dev/i2c-0')
        ads1112 = ADS1112(0x48, i2c_bus)

    '''
    def __init__(self, dev_addr, i2c_bus=None):
        assert (dev_addr & (~0x03)) == 0x48

        self.dev_addr = dev_addr
        self.i2c_bus = i2c_bus

    def reset(self):
        '''
        reset internal register.

        Examples:
            ads1112.reset()
        '''
        self.i2c_bus.write(self.dev_addr, ADS1112Def.RESET_CMD)

    def config(self, channel, mode):
        '''
        Write The configuration register.

        Args:
            mode:     string, ['single', 'continuous'].
            channel:  int, [0, 1, 2, 3], four analog inputs:

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
            ads1112.config(0,'continuous')
        '''
        assert ADS1112Def.CHANNEL_MIN <= channel
        assert channel <= ADS1112Def.CHANNEL_MAX
        assert mode in ADS1112Def.CONV_MODE

        if mode == 'continuous':
            self.enable_continuous_sampling(channel)
        else:
            self.set_channel(channel)
            self.disable_continuous_sampling()

    def disable_continuous_sampling(self):
        '''
        set single sample mode.

        Examples:
            ads1112.disable_continuous_sampling()
        '''
        # 3 bytes consist of list [output register upper byte,output register lower byte,configuration register]
        config_reg = self.i2c_bus.read(self.dev_addr, 3)[2]

        config_reg = config_reg | ADS1112Def.SINGLE_MODE

        self.i2c_bus.write(self.dev_addr, [config_reg])

    def enable_continuous_sampling(self, channel):
        '''
        set continuous sample mode.
        Args:
            channel:  int, [0, 1, 2, 3], four analog inputs:
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
            ret = ads1112.enable_continuous_sampling(0)
            # ret == True
        '''
        assert ADS1112Def.CHANNEL_MIN <= channel
        assert channel <= ADS1112Def.CHANNEL_MAX

        self.set_channel(channel)
        # 3 bytes consist of list [output register upper byte,output register lower byte,configuration register]
        config_reg = self.i2c_bus.read(self.dev_addr, 3)[2]
        # reset bit4 as 0.
        config_reg = config_reg & (~ADS1112Def.SINGLE_MODE & 0xff)

        self.i2c_bus.write(self.dev_addr, [config_reg])

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
        assert samplerate in ADS1112Def.SAMPLERATE
        # 3 bytes consist of list [output register upper byte,output register lower byte,configuration register]
        config_reg = self.i2c_bus.read(self.dev_addr, 3)[2]

        # clear the bit2 bit3 as 0.
        config_reg = config_reg & 0xf3
        # set samplerate bits.
        config_reg = config_reg | ADS1112Def.SAMPLERATE[samplerate] << 2

        self.i2c_bus.write(self.dev_addr, [config_reg])

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
        # 3 bytes consist of list [output register upper byte,output register lower byte,configuration register]
        config_reg = self.i2c_bus.read(self.dev_addr, 3)[2]
        # get the bit2 and bit3 value.
        temp = (config_reg & 0x0c) >> 2

        for samplerate, value in ADS1112Def.SAMPLERATE.items():
            if temp == value:
                return samplerate

        raise ADS1112Exception("Get sampling rate error")

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
        assert gain in ADS1112Def.PGA_GAIN
        # 3 bytes consist of list [output register upper byte,output register lower byte,configuration register]
        config_reg = self.i2c_bus.read(self.dev_addr, 3)[2]
        # clear the bit0 bit1 as 0.
        config_reg = config_reg & 0xfc

        for index, value in enumerate(ADS1112Def.PGA_GAIN):
            if value == gain:
                config_reg = config_reg | index

        self.i2c_bus.write(self.dev_addr, [config_reg])

    def set_channel(self, channel):
        '''
        select the adc channel.

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
            ads1112.set_channel(0)
        '''
        # 3 bytes consist of list [output register upper byte,output register lower byte,configuration register]
        config_reg = self.i2c_bus.read(self.dev_addr, 3)[2]
        # clear the bit5 bit6 as 0.
        config_reg = config_reg & 0x9f
        # set channel bits.
        config_reg = config_reg | channel << 5

        self.i2c_bus.write(self.dev_addr, [config_reg])

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
        assert ADS1112Def.CHANNEL_MIN <= channel
        assert channel <= ADS1112Def.CHANNEL_MAX

        self.set_channel(channel)
        # 3 bytes consist of list [output register upper byte,output register lower byte,configuration register]
        config_reg = self.i2c_bus.read(self.dev_addr, 3)[2]
        # set bit8 for enable single voltage convert.
        config_reg = config_reg | (ADS1112Def.SINGLE_MODE | ADS1112Def.ST_DRDY_SET)

        self.i2c_bus.write(self.dev_addr, [config_reg])

        # 3 bytes consist of list [output register upper byte,output register lower byte,configuration register]
        value = self.i2c_bus.read(self.dev_addr, 3)
        # in order to get the new output register data.
        start_time = time.time()
        time_ = 0
        while (value[2] & 0x80) and time_ < ADS1112Def.TIMEOUT:
            value = self.i2c_bus.read(self.dev_addr, 3)
            time_ = time.time() - start_time
            time.sleep(0.1)

        if time_ >= ADS1112Def.TIMEOUT:
            raise ADS1112Exception("Read single voltage time out")
        return self.code_2_voltage(value)

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
        assert ADS1112Def.COUNT_MIN <= count
        assert count <= ADS1112Def.COUNT_MAX

        volt = []
        # in order to get the new output register data.
        start_time = time.time()
        time_ = 0
        time_out = count * ADS1112Def.TIMEOUT_UNIT
        for i in range(count):
            value = self.i2c_bus.read(self.dev_addr, 3)
            while (value[2] & 0x80) and time_ < time_out:
                value = self.i2c_bus.read(self.dev_addr, 3)
                time_ = time.time() - start_time
                time.sleep(0.01)

            if time_ >= time_out:
                raise ADS1112Exception("Read continue voltage time out")
            volt.append(self.code_2_voltage(value))

        return volt

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

        output_code = output_reg & ADS1112Def.DATA_RATE_TO_RESOLUTION[data_rate]
        # judge the mark,if the happer bit is 1 mean it is a negative, otherwise is a postive.
        if output_code & ADS1112Def.DATA_RATE_TO_MARK[data_rate]:
            output_code = output_code - ADS1112Def.DATA_RATE_TO_RESOLUTION[data_rate]

        # Output Code = −1 * Min Code * PGA * ((VIN+) - (VIN-))/2.048V
        volt = output_code * ADS1112Def.VREF / (ADS1112Def.DATA_RATE_TO_MINCODE[data_rate] * ADS1112Def.PGA_GAIN[pga])

        return volt
