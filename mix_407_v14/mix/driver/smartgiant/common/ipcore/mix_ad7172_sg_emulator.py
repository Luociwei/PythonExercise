# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'haitezhuang@SmartGiant'
__version__ = '0.1'


class AD7172Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class MIXAd7172SGEmulator(object):
    '''
    AD7172 is a 24bit adc, you can use it to measure voltage at single sampling mode or coninus sampling mode.

    Args:
            dev_name:   string,     Device name
            vref:       float,      Reference name

    Examples:
                AD7172 = AD7172('AD7172', 2500)
    '''

    def __init__(self, dev_name, vref=2500):
        self._dev_name = dev_name
        self._vref = vref

        self._r_reg = {0x00: 0x80, 0x03: 0x000000,
                       0x04: 0x000000, 0x07: 0x00D0}
        self._w_reg = {}
        self._recorder = Recorder()
        add_recorder(self._recorder)

        self._sampling_rate = [500, 500, 500, 500]
        self._channel_state = ['disable', 'disable', 'disable', 'disable']

    def __del__(self):
        del_recorder(self._recorder)

    def reset(self, register_state=None):
        '''
        Reset spi state and the registers of ad7172

        Args:
                register_state:     dict,   the register state when reset, eg:{0x10:0x8001, 0x11:0x9043}.
                                                Default None, not set any register, all registers are default values.
        Examples:
                    AD7172.reset()
        '''
        if register_state is None:
            self._recorder.record("AD7172 reset all registers")
        elif isinstance(register_state, dict):
            for key, value in register_state:
                self._recorder.record("AD7172 reset %s register to %s value" %
                                      (hex(key), hex(value)))
        else:
            raise AD7172Exception("Invalid parameter: %s" % register_state)

    def channel_init(self):
        self._recorder.record("AD7172 channel init")

    def read_register(self, reg_addr):
        '''
        Read the register value of ad7172

        Args:
                reg_addr:       heximal,    Register address
        Examples:
                    data = AD7172.read_register(0x01)
                    print(data)
        '''
        assert reg_addr >= 0
        self._recorder.record("AD7172 read_register %s" % (hex(reg_addr)))
        if reg_addr in self._r_reg:
            return self._r_reg[reg_addr]
        elif reg_addr in self._w_reg:
            return self._w_reg[reg_addr]
        else:
            return 0x0

    def write_register(self, reg_addr, reg_data):
        '''
        Write the register value of ad7172

        Args:
                reg_addr:       hexmial,    Register address
                reg_data:       int,        Data to be write

        Examples:
                    AD7172.write_register(0x01, 10)
        '''
        assert reg_addr >= 0
        assert reg_data >= 0

        self._recorder.record("write %s to 0x%02x" % (hex(reg_data), reg_addr))
        self._w_reg[reg_addr] = reg_data

    def value_2_mvolt(self, code, mvref, bits):
        '''
        AD7172 adc value convert to mvolt

        Args:
                code:       hexmial,    Adc sample value
                mvref:      float,      Reference voltage
                bits:       int,        Data width

        Examples:
                    data = AD7172.value_2_mvolt(0xff, 2500, 32)
                    print(data)
        '''
        range_code = 1 << (bits - 1)
        volt = code
        volt -= range_code
        volt /= float(range_code)
        volt *= mvref

        # logger.debug("volt = %r mvref=%r"%(volt,mvref))
        return volt

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        Set the sampling rate of ad7172

        Args:
                channel:        int(0-3),   AD7172 sample channel
                sampling_rate:  float,        AD7172 sampling rate

        Examples
                    AD7172.set_sampling_rate(0, 1000)
        '''
        assert channel in [i for i in range(3)]
        assert isinstance(sampling_rate, (float, int))

        self._recorder.record("AD7172 set ch%d channel sampling rate to %dsps" % (channel, sampling_rate))
        self._sampling_rate[channel] = sampling_rate

    def get_sampling_rate(self, channel):
        '''
        Get the sampling rate of ad7172

        Args:
                channel:    int(0-3),   AD7172 sample channel

        Examples:
                    data = AD7172.get_sampling_rate(0)
                    print(data)
        '''
        assert channel in [i for i in range(3)]

        self._recorder.record("AD7172 get ch%d channel sampling rate" % (channel))

        return self._sampling_rate[channel]

    def set_channel_state(self, channel, state):
        assert channel in [i for i in range(3)]
        assert state in ["enable", "disable"]
        self._recorder.record("set channel %s state %s" % (channel, state))

    def select_single_channel(self, channel):
        '''
        channel register Select ADC work channel,open select channel,and close other channels
            It can be used, when  ADC work in single mode

        Examples:
                    AD7172.select_single_channel(0)
        '''
        for ch in [i for i in range(3)]:
            self.set_channel_state(ch, "disable")
        self.set_channel_state(channel, "enable")

    def read_volt(self, channel):
        '''
        Get the voltage of ad7172 at single sampling mode.

        Args:
                channel:    int(0-3),                   AD7172 sample channel

        Examples:
                    data = AD7172.read_volt(0)
                    print(data)
        '''
        assert channel in [i for i in range(3)]
        _volt_list = [100.124456, 200.544243, 300.323454, 500.475432]
        self._recorder.record("AD7172 get voltage")
        return _volt_list[channel]

    def is_communication_ok(self):
        '''
        Read the id of ad7172 and then confirm whether the communication of spi bus is ok

        Examples:
                    if AD7172.is_communication_ok():
                        print("communication ok")
                    else:
                        print("communication failed.")
        '''
        self._recorder.recorder("AD7172 is communication ok")
        return True

    def enable_continuous_sampling(self, channel, sampling_rate):
        '''
        Set the sampling rate of ad7172, and then enable the continus sampling mode.

        Args:
                channel:        int(0-3),   AD7172 sample channel
                sampling_rate:  int,        AD7172 sampling rate

        Examples:
                    AD7172.enable_continuous_sampling(0, 1000)
        '''
        assert channel in [i for i in range(3)]
        assert isinstance(sampling_rate, (float, int))

        self._recorder.record(
            "AD7172 enable ch%d continuous sampling mode sampling_rate is %dsps" % (channel, sampling_rate))

    def disable_continuous_sampling(self, channel):
        '''
        disanble the continus sampling mode, and reset the ad7172.

        Args:
                channel:        int(0-3),   AD7172 sample channel

        Examples:
                    AD7172.disable_continuous_sampling()
        '''

        self._recorder.record("AD7172 disable_continuous_sampling_mode")

    def get_continuous_sampling_voltage(self, channel, count):
        '''
        Get the voltage of ad7172 at continuous sampling mode.

        Args:
                channel:        int(0-3),   AD7172 sample channel
                count:          int,        count voltage to read

        Examples:
                    data = AD7172.get_continuous_sampling_voltage(0, 3)
                    print(data)
        '''
        assert channel in [i for i in range(3)]
        assert count > 0

        self._recorder.record(
            "AD7172 get ch%d channel voltage at continuous sampling mode count is %d" % (channel, count))

        if channel == 0:
            _result_dict = [-100.123456] * count
        if channel == 1:
            _result_dict = [-200.345367] * count

        return _result_dict
