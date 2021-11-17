# -*- coding: utf-8 -*-
from mix.driver.core.tracer.recorder import *

__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.1'


class AD9832Exception(Exception):
    def __init__(self, err_str):
        self._err_reason = '%s.' % (err_str)

    def __str__(self):
        return self._err_reason


class AD9832Emulator(object):
    '''
    AD9832 chip function class

    :param   spi_bus:   Instance/None,   MIXQSPISG class instance,
                                         if not using, will create emulator
    :example:
              axi4_bus = AXI4LiteBus('/dev/MIX_DUT_SPI_0', 256)
              ad9832 = AD9832(axi4_bus)
    '''

    def __init__(self, spi_bus=None):
        self.spi_bus = spi_bus
        self._recorder = Recorder()
        add_recorder(self._recorder)
        self.reset()

    def __del__(self):
        del_recorder(self._recorder)

    def write_register(self, reg_value):
        '''
        AD9832 internal function to write register

        :param reg_value:   hexmial(0-0xffff)    16 bit data to be write

        :example:
                  ad9832.write_register(0x01)
        '''
        assert isinstance(reg_value, int) and (0 <= reg_value <= 0xffff)

        wr_data = [(reg_value >> 8) & 0xFF]
        wr_data.append(reg_value & 0xFF)

        self._recorder.record("write %s" % (hex(reg_data)))

    def reset(self):
        '''
        AD9832 internal function to reset

        :example:
                  ad9832.reset()
        '''
        self._recorder.record("AD9832 reset")

    def enable_output(self):
        '''
        AD9832 internal function to enable output

        :example:
                  ad9832.enable_output()
        '''
        self._recorder.record("AD9832 enable_output")

    def set_frequency(self, freq_channel, freq_value):
        '''
        AD9832 internal function to set frequency

        :param freq_channel:  str(FREQ0, FREQ1)     The channel to set frequency
        :param freq_value:    float/int             frequency value

        :example:
                  ad9832.set_frequency('FREQ0', 1000)
        '''
        assert isinstance(freq_value, (int, float)) and (0 <= freq_value <= self._mclk)
        assert freq_channel in {AD9832Def.FREQ0_CHANNEL, AD9832Def.FREQ1_CHANNEL}

        self._recorder.record("AD9832 set_frequency channel:%s freq:%d" % (freq_channel, freq_value))

    def set_phase(self, phase_channel, phase_value):
        '''
        AD9832 internal function to set phase

        :param phase_channel:  str(PHASE0 ~ PHASE3)     The channel to set phase
        :param phase_value:    float /int               phase value

        :example:
                  ad9832.set_phase('PHASE1', 1.414)
        '''
        assert isinstance(phase_value, (int, float)) and (0 <= phase_value <= (2 * math.pi))

        assert phase_channel in {AD9832Def.PHASE0_CHANNEL, AD9832Def.PHASE1_CHANNEL,
                                 AD9832Def.PHASE2_CHANNEL, AD9832Def.PHASE3_CHANNEL}

        self._recorder.record("AD9832 set_phase channel:%s value:%d" % (phase_channel, phase_value))

    def select_freq_phase_channel(self, freq_channel, phase_channel):
        '''
        AD9832 select frequency and phase channel to generate waveform

        :param freq_channel:   str(FREQ0, FREQ1)        frequency channel to generate waveform
        :param phase_channel:  str(PHASE0 ~ PHASE3)     phase channel to generate waveform

        :example:
                  ad9832.select_freq_phase_channel('FREQ0', 'PHASE1')
        '''
        assert freq_channel in {AD9832Def.FREQ0_CHANNEL, AD9832Def.FREQ1_CHANNEL}
        assert phase_channel in {AD9832Def.PHASE0_CHANNEL, AD9832Def.PHASE1_CHANNEL,
                                 AD9832Def.PHASE2_CHANNEL, AD9832Def.PHASE3_CHANNEL}

        self._recorder.record("AD9832 select_freq_phase_channel freq_ch:%s phase_ch:%s" % (freq_channel, phase_channel))

    def output(self, freq_channel, frequency, phase_channel='PHASE0', phase=0):
        ''''
        AD9832 generate waveform output, just support sine waveform

        :param freq_channel:  str(FREQ0, FREQ1)         frequency channel to generate output
        :param frequency:     float/int                 unit is Hz, waveform frequency, max support 25MHz
        :param phase_channel: str(PHASE0 ~ PHASE3)      phase channel to generate output
        :param phase:         float/int(0 ~ 2*pi)       waveform phase, 0 ~ 2*pi

        :example:
                    frequency = 1000
                    phase = 0
                    ad9832.output('FREQ0', frequency, 'PHASE0', phase)
        '''

        self._recorder.record("AD9832 output freq_ch:%s freq:%d phase_ch:%s phase:%d" %
                              (freq_channel, frequency, phase_channel, phase))

    def stop_output(self):
        ''''
        AD9832 stop waveform output

        :example:
                    ad9832.stop_output()
        '''
        self._recorder.record("AD9832 stop_output")
