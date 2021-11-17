# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'chenfeng@SmartGiant'
__version__ = '0.1'


class AD9833Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class AD9833Emulator(object):
    '''
    AD9833 chip function class.

    Examples:
        ad9833 = AD9833Emulator()

    '''

    def __init__(self):
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self.reset()

    def __del__(self):
        del_recorder(self._recorder)

    def write_register(self, reg_value):
        '''
        AD9833 internal function to write register

        Args:
            reg_value:   hexmial, [0~0xffff], data to be write.

        Examples:
            ad9833.write_register(0x01)

        '''
        assert isinstance(reg_value, int) and (0 <= reg_value <= 0xffff)

        wr_data = [(reg_value >> 8) & 0xFF]
        wr_data.append(reg_value & 0xFF)

        self._recorder.record("write %s" % (hex(reg_data)))

    def reset(self):
        '''
        AD9833 internal function to reset

        :example:
                  ad9833.reset()
        '''
        self._recorder.record("AD9833 reset")

    def disable_reset(self):
        '''
        AD9833 internal function to disable reset

        Examples:
            ad9833.disable_reset()

        '''
        self._recorder.record("AD9833 disable reset")

    def set_frequency(self, freq_channel, freq_value):
        '''
        AD9833 internal function to set frequency

        Args:
            freq_channel:  string, ['FREQ0', 'FREQ1'],  The channel to set frequency.
            freq_value:    float, frequency value.

        Examples:
            ad9833.set_frequency('FREQ0', 1000)

        '''
        assert isinstance(freq_value, (int, float)) and (0 <= freq_value <= self._mclk)
        assert freq_channel in [AD9833Def.FREQ0_CHANNEL, AD9833Def.FREQ1_CHANNEL]

        self._recorder.record("AD9833 set_frequency channel:%s freq:%d" % (freq_channel, freq_value))

    def set_phase(self, phase_channel, phase_value):
        '''
        AD9833 internal function to set phase

        Args:
            phase_channel:  string, ['PHASE0', 'PHASE1'], The channel to set phase.
            phase_value:    float, phase value.

        Examples:
            ad9833.set_phase('PHASE0', 1.414)

        '''
        assert isinstance(phase_value, (int, float)) and (0 <= phase_value <= (2 * math.pi))

        assert phase_channel in [AD9833Def.PHASE0_CHANNEL, AD9833Def.PHASE1_CHANNEL]

        self._recorder.record("AD9833 set_phase channel:%s value:%d" % (phase_channel, phase_value))

    def select_freq_phase_channel(self, freq_channel, phase_channel):
        '''
        AD9833 select frequency and phase channel to generate waveform

        Args:
            freq_channel:   string, ['FREQ0', 'FREQ1'], frequency channel to generate waveform.
            phase_channel:  string, ['PHASE0', 'PHASE1'], phase channel to generate waveform.

        Examples:
            ad9833.select_freq_phase_channel('FREQ0', 'PHASE0')

        '''
        assert freq_channel in [AD9833Def.FREQ0_CHANNEL, AD9833Def.FREQ1_CHANNEL]
        assert phase_channel in [AD9833Def.PHASE0_CHANNEL, AD9833Def.PHASE1_CHANNEL]

        self._recorder.record("AD9833 select_freq_phase_channel freq_ch:%s phase_ch:%s" % (freq_channel, phase_channel))

    def set_output_mode(self, mode):
        '''
        AD9833 internal function to set output mode

        Args:
            mode:  string, ['sine', 'triangular', 'square', 'square_div_2'], output waveform mode.

        Examples:
            ad9833.set_output_mode('sine')

        '''
        assert mode in [AD9833Def.OUTPUT_MODE_SINE, AD9833Def.OUTPUT_MODE_TRIANGULAR,
                        AD9833Def.OUTPUT_MODE_SQUARE_DIV_2, AD9833Def.OUTPUT_MODE_SQUARE]

        self._recorder.record("AD9833 set_output_mode mode:%s" % (mode))

    def set_sleep_mode(self, mode):
        '''
        AD9833 internal funtion set sleep mode

        Args:
            mode:    string, ['dac', 'mclk', 'all'], sleep mode, disable dac mclk or all.

        Examples:
            ad9833.set_sleep_mode('dac')

        '''
        assert mode in [AD9833Def.SLEEP_MODE_DISABLE, AD9833Def.SLEEP_MODE_DAC,
                        AD9833Def.SLEEP_MODE_MCLK, AD9833Def.SLEEP_MODE_ALL]

        self._recorder.record("AD9833 set_sleep_mode mode:%s" % (mode))

    def output(self, freq_channel, frequency, phase_channel='PHASE0', phase=0, output_mode='sine'):
        '''
        AD9833 generate waveform output

        Args:
            freq_channel:  string, ['FREQ0', 'FREQ1'],   frequency channel to generate output.
            frequency:     float,                        waveform frequency.
            phase_channel: string, ['PHASE0', 'PHASE1'], phase channel to generate output.
            phase:         float,                        waveform phase.
            output_mode:   string, [sine', 'triangular', 'square', 'square_div_2'], output waveform mode.

        Examples:
            ad9833.output('FREQ0', 1000, 'PHASE0', 0, 'sine')

        '''

        self._recorder.record("AD9833 output freq_ch:%s freq:%d phase_ch:%s phase:%d output_mode:%s" %
                              (freq_channel, frequency, phase_channel, phase, output_mode))
