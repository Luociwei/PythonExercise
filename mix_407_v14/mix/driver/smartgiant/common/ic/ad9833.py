# -*- coding: utf-8 -*-

import math
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator


__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class AD9833Def(object):
    B28_OFFSET = 13
    B28_MASK = (1 << B28_OFFSET)
    B28_FREQ_28BIT = (1 << B28_OFFSET)
    B28_FREQ_TWO_14BIT = (0 << B28_OFFSET)

    HLB_OFFSET = 12
    HLB_MASK = (1 << HLB_OFFSET)
    HLB_FREQ_MSB = (1 << HLB_OFFSET)
    HLB_FREQ_LSB = (0 << HLB_OFFSET)

    FSELECT_OFFSET = 11
    FSELECT_MASK = (1 << FSELECT_OFFSET)
    FSELECT_FREQ0 = (0 << FSELECT_OFFSET)
    FSELECT_FREQ1 = (1 << FSELECT_OFFSET)

    PSELECT_OFFSET = 10
    PSELECT_MASK = (1 << PSELECT_OFFSET)
    PSELECT_PHASE0 = (0 << PSELECT_OFFSET)
    PSELECT_PHASE1 = (1 << PSELECT_OFFSET)

    RESET_OFFSET = 8
    RESET_MASK = (1 << RESET_OFFSET)
    RESET_SET = (1 << RESET_OFFSET)
    RESET_CLEAR = (0 << RESET_OFFSET)

    SLEEP_OFFSET = 6
    SLEEP_MASK = (0x03 << SLEEP_OFFSET)
    SLEEP_DISABLE = (0x00 << SLEEP_OFFSET)
    SLEEP_DAC = (0x01 << SLEEP_OFFSET)
    SLEEP_MCLK = (0x02 << SLEEP_OFFSET)
    SLEEP_ALL = (0x03 << SLEEP_OFFSET)

    OPBITEN_OFFSET = 5
    DIV2_OFFSET = 3
    MODE_OFFSET = 1

    OUTPUT_MASK = ((1 << OPBITEN_OFFSET) | (1 << DIV2_OFFSET) | (1 << MODE_OFFSET))
    OUTPUT_SINE = ((0 << OPBITEN_OFFSET) | (0 << DIV2_OFFSET) | (0 << MODE_OFFSET))
    OUTPUT_RAMP = ((0 << OPBITEN_OFFSET) | (0 << DIV2_OFFSET) | (1 << MODE_OFFSET))
    OUTPUT_MSB_2 = ((1 << OPBITEN_OFFSET) | (0 << DIV2_OFFSET) | (0 << MODE_OFFSET))
    OUTPUT_MSB = ((1 << OPBITEN_OFFSET) | (1 << DIV2_OFFSET) | (0 << MODE_OFFSET))

    FREQ0_REG_ADDR = (0x01 << 14)
    FREQ1_REG_ADDR = (0x02 << 14)

    PHASE0_REG_ADDR = (0x06 << 13)
    PHASE1_REG_ADDR = (0x07 << 13)

    MCLK = 25000000.0
    FREQ0_CHANNEL = 'FREQ0'
    FREQ1_CHANNEL = 'FREQ1'
    PHASE0_CHANNEL = 'PHASE0'
    PHASE1_CHANNEL = 'PHASE1'
    SLEEP_MODE_DISABLE = 'disable'
    SLEEP_MODE_DAC = 'dac'
    SLEEP_MODE_MCLK = 'mclk'
    SLEEP_MODE_ALL = 'all'
    OUTPUT_MODE_SINE = 'sine'
    OUTPUT_MODE_TRIANGULAR = 'triangular'
    OUTPUT_MODE_SQUARE_DIV_2 = 'square_div_2'
    OUTPUT_MODE_SQUARE = 'square'
    FREQ_FULL_SCALE = pow(2, 28)
    PHASE_FULL_SCALE = 4096


class AD9833(object):
    '''
    AD9833 chip function class.

    ClassType = DAC

    Args:
        spi_bus:   instance(QSPI)/None, MIXQSPISG class instance, if not using, will create emulator.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_SPI_0', 256)
        ad9833 = AD9833(axi4_bus)

    '''

    def __init__(self, spi_bus=None):
        if spi_bus is None:
            self.spi_bus = MIXQSPISGEmulator("ad9833_emulator", 256)
        else:
            self.spi_bus = spi_bus
        # AD9833 initialization needs to set SPI mode to "MODE2"
        self.spi_bus.set_mode("MODE2")
        self.control_register = 0x0000
        self.reset()

    def write_register(self, reg_value):
        '''
        AD9833 internal function to write register

        Args:
            reg_value:   hexmial, [0~0xffff], data to be write.

        Examples:
            ad9833.write_register(0x01)

        '''
        wr_data = [(reg_value >> 8) & 0xFF]
        wr_data.append(reg_value & 0xFF)
        self.spi_bus.write(wr_data)

    def reset(self):
        '''
        AD9833 internal function to reset device

        Examples:
            ad9833.reset()

        '''
        self.control_register &= ~AD9833Def.RESET_MASK
        self.control_register |= AD9833Def.RESET_SET
        self.write_register(self.control_register)

    def disable_reset(self):
        '''
        AD9833 internal function to disable reset

        Examples:
            ad9833.disable_reset()

        '''
        self.control_register = 0
        self.control_register &= ~AD9833Def.RESET_MASK
        self.control_register |= AD9833Def.RESET_CLEAR
        self.write_register(self.control_register)

    def set_frequency(self, freq_channel, freq_value):
        '''
        AD9833 internal function to set frequency

        Args:
            freq_channel:  string, ['FREQ0', 'FREQ1'],  The channel to set frequency.
            freq_value:    float, frequency value.

        Examples:
            ad9833.set_frequency('FREQ0', 1000)

        '''
        reg_value = int(freq_value * AD9833Def.FREQ_FULL_SCALE / AD9833Def.MCLK)

        self.control_register &= ~AD9833Def.B28_MASK
        self.control_register |= AD9833Def.B28_FREQ_28BIT
        self.write_register(self.control_register)
        if freq_channel == AD9833Def.FREQ0_CHANNEL:
            self.write_register(AD9833Def.FREQ0_REG_ADDR | (reg_value & 0x3FFF))
            self.write_register(AD9833Def.FREQ0_REG_ADDR | ((reg_value >> 14) & 0x3FFF))
        else:
            self.write_register(AD9833Def.FREQ1_REG_ADDR | (reg_value & 0x3FFF))
            self.write_register(AD9833Def.FREQ1_REG_ADDR | ((reg_value >> 14) & 0x3FFF))

    def set_phase(self, phase_channel, phase_value):
        '''
        AD9833 internal function to set phase

        Args:
            phase_channel:  string, ['PHASE0', 'PHASE1'], The channel to set phase.
            phase_value:    float, phase value.

        Examples:
            ad9833.set_phase('PHASE0', 1.414)

        '''
        reg_value = int(phase_value * AD9833Def.PHASE_FULL_SCALE / (2 * math.pi))
        if phase_channel == AD9833Def.PHASE0_CHANNEL:
            self.write_register(AD9833Def.PHASE0_REG_ADDR | (reg_value & 0xFFF))
        else:
            self.write_register(AD9833Def.PHASE1_REG_ADDR | (reg_value & 0xFFF))

    def select_freq_phase_channel(self, freq_channel, phase_channel):
        '''
        AD9833 select frequency and phase channel to generate waveform

        Args:
            freq_channel:   string, ['FREQ0', 'FREQ1'], frequency channel to generate waveform.
            phase_channel:  string, ['PHASE0', 'PHASE1'], phase channel to generate waveform.

        Examples:
            ad9833.select_freq_phase_channel('FREQ0', 'PHASE0')

        '''
        self.control_register &= ~AD9833Def.FSELECT_MASK
        self.control_register &= ~AD9833Def.PSELECT_MASK
        # select frequency channel
        if freq_channel == AD9833Def.FREQ0_CHANNEL:
            self.control_register |= AD9833Def.FSELECT_FREQ0
        else:
            self.control_register |= AD9833Def.FSELECT_FREQ1
        # select phase channel
        if phase_channel == AD9833Def.PHASE0_CHANNEL:
            self.control_register |= AD9833Def.PSELECT_PHASE0
        else:
            self.control_register |= AD9833Def.PSELECT_PHASE1
        self.write_register(self.control_register)

    def set_output_mode(self, mode):
        '''
        AD9833 internal function to set output mode

        Args:
            mode:  string, ['sine', 'triangular', 'square', 'square_div_2'], output waveform mode.

        Examples:
            ad9833.set_output_mode('sine')

        '''
        self.control_register &= ~AD9833Def.OUTPUT_MASK
        if mode == AD9833Def.OUTPUT_MODE_SINE:
            self.control_register |= AD9833Def.OUTPUT_SINE
        elif mode == AD9833Def.OUTPUT_MODE_TRIANGULAR:
            self.control_register |= AD9833Def.OUTPUT_RAMP
        elif mode == AD9833Def.OUTPUT_MODE_SQUARE_DIV_2:
            self.control_register |= AD9833Def.OUTPUT_MSB_2
        elif mode == AD9833Def.OUTPUT_MODE_SQUARE:
            self.control_register |= AD9833Def.OUTPUT_MSB
        self.write_register(self.control_register)

    def set_sleep_mode(self, mode):
        '''
        AD9833 internal funtion set sleep mode

        Args:
            mode:    string, ['dac', 'mclk', 'all'], sleep mode, disable dac mclk or all.

        Examples:
            ad9833.set_sleep_mode('dac')

        '''
        self.control_register &= ~AD9833Def.SLEEP_MASK
        if mode == AD9833Def.SLEEP_MODE_DISABLE:
            self.control_register |= AD9833Def.SLEEP_DISABLE
        elif mode == AD9833Def.SLEEP_MODE_DAC:
            self.control_register |= AD9833Def.SLEEP_DAC
        elif mode == AD9833Def.SLEEP_MODE_MCLK:
            self.control_register |= AD9833Def.SLEEP_MCLK
        elif mode == AD9833Def.SLEEP_MODE_ALL:
            self.control_register |= AD9833Def.SLEEP_ALL
        self.write_register(self.control_register)

    def output(self, freq_channel, frequency, phase_channel, phase, output_mode):
        ''''
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
        assert freq_channel in [AD9833Def.FREQ0_CHANNEL, AD9833Def.FREQ1_CHANNEL]
        assert phase_channel in [AD9833Def.PHASE0_CHANNEL, AD9833Def.PHASE1_CHANNEL]
        assert frequency > 0 and frequency <= AD9833Def.MCLK
        assert phase >= 0 and phase <= 2 * math.pi
        self.disable_reset()

        self.set_frequency(freq_channel, frequency)

        self.set_phase(phase_channel, phase)

        self.select_freq_phase_channel(freq_channel, phase_channel)
        if output_mode in [AD9833Def.OUTPUT_MODE_SQUARE_DIV_2, AD9833Def.OUTPUT_MODE_SQUARE]:
            self.set_sleep_mode(AD9833Def.SLEEP_MODE_DAC)
        else:
            self.set_sleep_mode(AD9833Def.SLEEP_MODE_DISABLE)
        self.set_output_mode(output_mode)
