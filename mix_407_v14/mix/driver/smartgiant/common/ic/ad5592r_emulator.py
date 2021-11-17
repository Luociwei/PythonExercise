# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *
from mix.driver.smartgiant.common.ic.ad5592r import AD5592RDef

__author__ = 'yongjiu@SmartGiant'
__version__ = '0.1'


class AD5592REmulator(object):
    '''
    AD5592R Emulator class
    '''
    def __init__(self, name='ad5592r'):
        self.name = name

        self._recorder = Recorder()
        add_recorder(self._recorder)
        self._recorder.record("{}.__init__()".format(self.name))

    def reset(self):
        '''
        soft reset chip, I/O*8 all pulldown to  85 KOhm

        Examples:
            ad5592r.reset()

        '''
        self._recorder.record("{}.reset()".format(self.name))

    @property
    def reference(self):
        '''
        AD5592R get mode of reference voltage

        Examples:
            result = ad5592r.reference

        '''
        self._recorder.record("{}.reference_get()".format(self.name))
        return 'external'

    @reference.setter
    def reference(self, ref_mode):
        '''
        AD5592R set mode of reference voltage

        Args:
            ref_mode:  string, ["internal, "external"], default is "external".

        Examples:
            ad5592r.reference("external")

        '''
        assert ref_mode in AD5592RDef.REFERENCY.LIST

        self._recorder.record("{}.reference_set({})".format(self.name, ref_mode))

    def gain_set(self, adc_gain, dac_gain):
        '''
        config ADC and DAC range gain

        Args:
            adc_gain:    int, [1, 2], ADC range gain.
            dac_gain:    int, [1, 2], DAC range gain.

        Examples:
            ad5592r.gain_set(1, 2)

        '''
        assert isinstance(adc_gain, int)
        assert isinstance(dac_gain, int)
        assert adc_gain in [AD5592RDef.GAIN_1, AD5592RDef.GAIN_2]
        assert dac_gain in [AD5592RDef.GAIN_1, AD5592RDef.GAIN_2]

        self._recorder.record("{}.gain_set({}, {})".format(self.name, adc_gain, dac_gain))

    def channel_config(self, channel, mode):
        '''
        set pin mode to ADC, DAC or GPIO

        Args:
            channel:     int, [0~7], channel id.
            mode:        string, ['DAC', 'ADC', 'INPUT', 'OUTPUT', 'OPEN_DRAIN_OUTPUT',
                                  'THREE_STATE', 'PULLDOWN_85KOHM'], eg.'INPUT'.

        Examples:
            ad5592r.channel_config(1, 'DAC')

        '''
        assert isinstance(channel, int)
        assert isinstance(mode, str)
        assert channel >= AD5592RDef.MIN_CHANNEL
        assert channel <= AD5592RDef.MAX_CHANNEL
        assert mode in AD5592RDef.MODE_LIST

        self._recorder.record("{}.channel_config({}, {})".format(self.name, channel, mode))

    def output_volt_dc(self, channel, volt):
        '''
        output dc voltage, 12bit dac

        Args:
            channel:    int, [0~7], channel id.
            volt:       float, output voltage value.

        Examples:
            ad5592r.output_volt_dc(0, 1000)

        '''
        assert isinstance(channel, int)
        assert isinstance(volt, (int, float))
        assert channel >= AD5592RDef.MIN_CHANNEL
        assert channel <= AD5592RDef.MAX_CHANNEL
        assert volt >= 0

        self._recorder.record("{}.output_volt_dc({}, {})".format(self.name, channel, volt))

    def read_volt(self, channel):
        '''
        AD5592R read input voltage

        Args:
            channel:     int, [0~7], channel id.

        Returns:
            float, value, unit mV.

        Examples:
            volt = ad5592r.read_volt(0)
            print(volt)

        '''
        assert isinstance(channel, int)
        assert channel >= AD5592RDef.MIN_CHANNEL
        assert channel <= AD5592RDef.MAX_CHANNEL

        self._recorder.record("{}.read_volt({})".format(self.name, channel))
        return 0
