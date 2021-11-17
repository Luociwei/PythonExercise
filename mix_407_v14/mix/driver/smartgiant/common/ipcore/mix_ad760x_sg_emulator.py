# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class MIXAD760XSGException(Exception):

    '''
    MIXAD760XSGException shows the exception of AD760X
    '''

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class MIXAD760XSGEmulator(object):
    '''
    MIXAD760XSG ADC Driver:
        The AD7605, AD7606, AD7607, and AD7608 are 16-bit, 8-/6-/4-channel,
        simultaneous sampling successive approximation ADCs.
        The devices operate from a single 2.7 V to 5.25 V power supply and feature
        throughput rates of up to 200 kSPS.
        The devices have on-board 1 MΩ input buffers for direct connection from the
        user sensor outputs to the ADC.

    Args:
        axi4_bus: instance(AXI4LiteBus)/string; instance of AXI4 bus or device path
                                                If None, will create Emulator.

    Examples:
        axi = AXI4LiteBus('/dev/XXX', 256)
        ad760x = MIXAD760XSG(axi)

    '''

    def __init__(self, dev_name):
        self._dev_name = dev_name

        self._r_reg = {0x00: 0x80, 0x03: 0x000000,
                       0x04: 0x000000, 0x07: 0x4FD0}
        self._w_reg = {}
        self._recorder = Recorder()
        add_recorder(self._recorder)

        self._sampling_rate = [1000, 1000, 1000, 1000]
        self._channel_state = ['disable', 'disable', 'disable', 'disable']
        self._enable()

    def __del__(self):
        self._disable()

    def _enable(self):
        '''
        AD760X enable, set ENABLE register ENABLE_BIT

        Examples:
            ad760x._enable()

        '''
        self._recorder.record("AD760X enable")

    def _disable(self):
        '''
        AD760X disable, clear ENABLE register

        Examples:
            ad760x._disable()

        '''
        self._recorder.record("AD760X disable")

    def reset(self):
        '''
        AD760X reset chip,
        The RESET high pulse should be minimum 50 ns wide.

        Examples:
            ad760x.reset()

        '''
        self._recorder.record("AD760X reset")

    def single_sampling(self, over_sampling, adc_range):
        '''
        AD760X measure single voltage, there is an improvement in SNR as
        over_sampling increases. Refer to AD7608 Datasheet Table 8(Page26).
        Conversion Control:
            Simultaneous Sampling on All Analog Input Channels

            +-------------------+-------------------+------+
            | over_sampling | sampling_rate limit | unit |
            +===================+===================+======+
            |  0 (No OS)        |  2000~200000      | 'Hz' |
            +-------------------+-------------------+------+
            |  1                |  2000~100000      | 'Hz' |
            +-------------------+-------------------+------+
            |  2                |  2000~50000       | 'Hz' |
            +-------------------+-------------------+------+
            |  3                |  2000~25000       | 'Hz' |
            +-------------------+-------------------+------+
            |  4                |  2000~12500       | 'Hz' |
            +-------------------+-------------------+------+
            |  5                |  2000~6250        | 'Hz' |
            +-------------------+-------------------+------+
            |  6                |  2000~3125        | 'Hz' |
            +-------------------+-------------------+------+
            |  7 (Invalid)      |  /                |  /   |
            +-------------------+-------------------+------+

        Args:
            over_sampling:  int, [0~7], OS[2:0] oversample bit value.
            adc_range:      string, ['10V', '5V'], adc reference voltage range.

        Examples:
            ad760x.single_sampling(0, '10V')

        '''
        assert(0 <= over_sampling < 8)
        assert(adc_range in ['10V', '5V'])

        _volt_list = [100.124456, 100.124456 * 2, 100.124456 * 3, 100.124456 * 4,
                      100.124456 * 5, 100.124456 * 6, 100.124456 * 7, 100.124456 * 8]
        self._recorder.record("AD760X measure_single_voltage")
        return _volt_list

    def enable_continuous_sampling(self, over_sampling, adc_range, sampling_rate):
        '''
        AD760X enable continuous measure, there is an improvement in SNR as
        over_sampling increases. Refer to AD7608 Datasheet Table 8(Page26).

        Args:
            over_sampling:  int, [0~7], OS[2:0] oversample bit value.
            adc_range:      string, ['10V', '5V'], reference voltage range.
            sampling_rate:  int, [2000~200000], sampling_rate.

        Examples:
            ad760x.enable_continuous_sampling(0, '10V', 2000)

        '''
        assert(0 <= over_sampling < 8)
        assert(adc_range in ['10V', '5V'])
        assert isinstance(sampling_rate, int) and 2000 <= sampling_rate <= 200000

        self._recorder.record("AD760X enable_continuous_measure")

    def disable_continuous_sampling(self):
        '''
        AD760X disable continuous measure

        Examples:
            ad760x.disable_continuous_sampling()

        '''
        self._disable()
