# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import AD717XDef

__author__ = 'haitezhuang@SmartGiant'
__version__ = '0.1'


class AD7175Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class MIXAd7175SGEmulator(object):
    '''
    AD7175 is a 32bit adc, you can use it to measure voltage
       at single sampling mode or coninus sampling mode.

    Args:
            dev_name:   string,     Device name
            vref:       float,      Reference name

    Examples:
                AD7175 = AD7175('AD7175', 2500)
    '''

    def __init__(self, dev_name, vref=2500):
        self._dev_name = dev_name
        self._vref = vref

        self._r_reg = {0x00: 0x80, 0x03: 0x000000,
                       0x04: 0x000000, 0x07: 0x4FD0}
        self._w_reg = {}
        self._recorder = Recorder()
        add_recorder(self._recorder)

        self._sampling_rate = [1000, 1000, 1000, 1000]
        self._channel_state = ['disable', 'disable', 'disable', 'disable']

    def __del__(self):
        del_recorder(self._recorder)

    def reset(self, register_state=None):
        '''
        Reset spi state and the registers of ad7175

        Args:
                register_state:     dict,   the register state when reset, eg:{0x10:0x8001, 0x11:0x9043}.
                                                Default None, not set any register, all registers are default values.

        Examples:
                    AD7175.reset()
        '''
        if register_state is None:
            self._recorder.record("AD7175 reset all registers")
        elif isinstance(register_state, dict):
            for key, value in register_state:
                self._recorder.record("AD7175 reset %s register to %s value" %
                                      (hex(key), hex(value)))
        else:
            raise AD7175Exception("Invalid parameter: %s" % register_state)

    def channel_init(self):
        self._recorder.record("AD7175 channel init")

    def read_register(self, reg_addr):
        '''
        Read the register value of ad7175

        Args:
                reg_addr:       heximal,    Register address

        Examples:
                    data = AD7175.read_register(0x01)
                    print(data)
        '''
        assert reg_addr >= 0
        self._recorder.record("AD7175 read_register %s" % (hex(reg_addr)))
        if reg_addr in self._r_reg:
            return self._r_reg[reg_addr]
        elif reg_addr in self._w_reg:
            return self._w_reg[reg_addr]
        else:
            return 0x0

    def write_register(self, reg_addr, reg_data):
        '''
        Write the register value of ad7175

        Args:
                reg_addr:       hexmial,    Register address
                reg_data:       int,        Data to be write

        Examples:
                    AD7175.write_register(0x01, 10)
        '''
        assert reg_addr >= 0
        assert reg_data >= 0

        self._recorder.record("write %s to 0x%02x" % (hex(reg_data), reg_addr))
        self._w_reg[reg_addr] = reg_data

    def value_2_mvolt(self, code, mvref, bits):
        '''
        AD7175 adc value convert to mvolt

        Args:
                code:       hexmial,    Adc sample value
                mvref:      float,      Reference voltage
                bits:       int,        Data width

        Examples:
                    data = AD7175.value_2_mvolt(0xff, 2500, 32)
                    print(data)
        '''
        range_code = 1 << (bits - 1)
        volt = code
        volt -= range_code
        volt /= float(range_code)
        volt *= mvref

        # logger.debug("volt = %r mvref=%r"%(volt,mvref))
        return volt

    def set_setup_register(self, channel, code_polar="bipolar", reference="extern", buffer_flag="enable"):
        '''
        AD717x setup register set, code polar,refrence, buffer

        Args:
                channel:    string("ch0"/"ch1"/"ch2"/"ch3"),            The channel to config setup_register
                code_polar: string("unipolar"/"bipolar"),               "unipolar" for unipolar input,
                                                                       "bipolar" for bipolar input
                reference:  string("extern"/"internal"/"AVDD-AVSS"),    Select voltage reference
                buffer:     string("enable"/"disable"),                 Enable or disable input buffer

        Examples:
                ad717x.set_setup_register("ch0", "bipolar", "extern", "enable")
        '''

        value = 0x0
        value |= AD717XDef.POLARS[code_polar] << 12 | AD717XDef.BUFFERS[buffer_flag] << 8 |\
            AD717XDef.REFERENCES[reference] << 4

        self._recorder.record("setup %s code_polar=%s, reference=%s, buffer_flag=%s" %
                              (channel, code_polar, reference, buffer_flag))
        self._w_reg[AD717XDef.SETUP_REG_ADDR[channel]] = value

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        Set the sampling rate of ad7175

        Args:
                channel:        int(0-3),   AD7175 sample channel
                sampling_rate:  int,        AD7175 sampling rate

        Examples:
                    AD7175.set_sampling_rate(0, 1000)
        '''
        assert channel in ([i for i in range(4)] + ["ch%d" % j for j in range(4)])
        assert isinstance(sampling_rate, (float, int))

        channel = int(channel[-1]) if isinstance(channel, str) else channel

        self._recorder.record("AD7175 set ch%d channel sampling rate to %dsps" % (channel, sampling_rate))
        self._sampling_rate[channel] = sampling_rate

    def get_sampling_rate(self, channel):
        '''
        Get the sampling rate of ad7175

        Args:
                    channel:    int(0-3),   AD7175 sample channel

        Examples:
                    data = AD7175.get_sampling_rate(0)
                    print(data)
        '''
        assert channel in [i for i in range(4)]

        self._recorder.record("AD7175 get ch%d channel sampling rate" % (channel))

        return self._sampling_rate[channel]

    def set_channel_state(self, channel, state):

        assert channel in [i for i in range(4)]
        assert state in ["enable", "disable"]
        self._recorder.record("set channel %s state %s" % (channel, state))

    def select_single_channel(self, channel):
        '''
        channel register Select ADC work channel,open select channel,and close other channels
            It can be used, when  ADC work in single mode

        Examples:
                    AD7175.select_single_channel(0)
        '''
        for ch in [i for i in range(4)]:
            self.set_channel_state(ch, "disable")
        self.set_channel_state(channel, "enable")

    def read_volt(self, channel):
        '''
        Get the voltage of ad7175 at single sampling mode.

        Args:
            channel:    int(0-3),                   AD7175 sample channel

        Examples:
                    data = AD7175.read_volt(0)
                    print(data)
        '''
        assert channel in [i for i in range(4)]
        _volt_list = [100.124456, 200.544243, 300.323454, 500.475432]
        self._recorder.record("AD7175 get voltage")
        return _volt_list[channel]

    def is_communication_ok(self):
        '''
        Read the id of ad7175 and then confirm whether the communication of spi bus is ok

        Examples:
                    if AD7175.is_communication_ok():
                        print("communication ok")
                    else:
                        print("communication failed.")
        '''
        self._recorder.record("AD7175 is communication ok")
        return True

    def enable_continuous_sampling(self, channel, sampling_rate, samples=0):
        '''
        Set the sampling rate of ad7175, and then enable the continus sampling mode.

        Args:
                channel:        int(0-3),   AD7175 sample channel
                sampling_rate:  float,        AD7175 sampling rate

        Examples:
                    AD7175.enable_continuous_sampling(0, 1000)
        '''
        assert channel in [i for i in range(4)]
        assert isinstance(sampling_rate, (float, int))

        self._recorder.record(
            "AD7175 enable ch%d continuous sampling mode sampling_rate is %dsps" % (channel, sampling_rate))

    def disable_continuous_sampling(self, channel):
        '''
        disanble the continus sampling mode, and reset the ad7175.

        Args:
                channel:        int(0-3),   AD7175 sample channel

        Examples:
                    AD7175.disable_continuous_sampling()
        '''

        self._recorder.record("AD7175 disable_continuous_sampling_mode")

    def get_continuous_sampling_voltage(self, channel, count):
        '''
        Get the voltage of ad7175 at continuous sampling mode.

        Args:
                channel:        int(0-3),   AD7175 sample channel
                count:          int,        count voltage to read

        Examples:
                    data = AD7175.get_continuous_sampling_voltage(0, 3)
                    print(data)
        '''
        assert channel in [i for i in range(4)]
        assert count > 0

        self._recorder.record(
            "AD7175 get ch%d channel voltage at continuous sampling mode count is %d" % (channel, count))

        if channel == 0:
            _result_dict = [-100.123456] * count
        if channel == 1:
            _result_dict = [-200.345367] * count

        return _result_dict
