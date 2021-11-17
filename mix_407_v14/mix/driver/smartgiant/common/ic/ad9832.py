# -*- coding: utf-8 -*-

import math
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator


__author__ = 'yongjiu@SmartGiant'
__version__ = '0.2'


class AD9832Def(object):
    CMD_OFFSET = 12
    CMD_PHASE_SET = (0 << CMD_OFFSET)
    CMD_PHASE_DEFER = (1 << CMD_OFFSET)
    CMD_FREQ_SET = (2 << CMD_OFFSET)
    CMD_FREQ_DEFER = (3 << CMD_OFFSET)
    CMD_FREQ_PHASE_SELECT = (6 << CMD_OFFSET)

    # Power-Down, Resetting and Clearing the AD9832
    CMD_SLEEP_RESET_CLR = (0xc << CMD_OFFSET)
    SLEEP_BIT = (0x1 << 13)
    RESET_BIT = (0x1 << 12)
    CLR_BIT = (0x1 << 11)

    ADDR_OFFSET = 8
    ADDR_FREQ0_REG0 = (0 << ADDR_OFFSET)
    ADDR_FREQ0_REG1 = (1 << ADDR_OFFSET)
    ADDR_FREQ0_REG2 = (2 << ADDR_OFFSET)
    ADDR_FREQ0_REG3 = (3 << ADDR_OFFSET)
    ADDR_FREQ1_REG0 = (4 << ADDR_OFFSET)
    ADDR_FREQ1_REG1 = (5 << ADDR_OFFSET)
    ADDR_FREQ1_REG2 = (6 << ADDR_OFFSET)
    ADDR_FREQ1_REG3 = (7 << ADDR_OFFSET)

    ADDR_PHASE0_REG0 = (8 << ADDR_OFFSET)
    ADDR_PHASE0_REG1 = (9 << ADDR_OFFSET)
    ADDR_PHASE1_REG0 = (10 << ADDR_OFFSET)
    ADDR_PHASE1_REG1 = (11 << ADDR_OFFSET)
    ADDR_PHASE2_REG0 = (12 << ADDR_OFFSET)
    ADDR_PHASE2_REG1 = (13 << ADDR_OFFSET)
    ADDR_PHASE3_REG0 = (14 << ADDR_OFFSET)
    ADDR_PHASE3_REG1 = (15 << ADDR_OFFSET)

    SELECT_FREQ_OFFSET = 11
    SELECT_FREQ0_CHANNEL = (0 << SELECT_FREQ_OFFSET)
    SELECT_FREQ1_CHANNEL = (1 << SELECT_FREQ_OFFSET)

    SELECT_PHASE_OFFSET = 9
    SELECT_PHASE0_CHANNEL = (0 << SELECT_PHASE_OFFSET)
    SELECT_PHASE1_CHANNEL = (1 << SELECT_PHASE_OFFSET)
    SELECT_PHASE2_CHANNEL = (2 << SELECT_PHASE_OFFSET)
    SELECT_PHASE3_CHANNEL = (3 << SELECT_PHASE_OFFSET)

    # master clock in Hz
    MCLK = 25000000.0

    FREQ0_CHANNEL = 'FREQ0'
    FREQ1_CHANNEL = 'FREQ1'
    PHASE0_CHANNEL = 'PHASE0'
    PHASE1_CHANNEL = 'PHASE1'
    PHASE2_CHANNEL = 'PHASE2'
    PHASE3_CHANNEL = 'PHASE3'
    FREQ_FULL_SCALE = pow(2, 32)
    PHASE_FULL_SCALE = 4096

    REGS = {
        FREQ0_CHANNEL: {
            "reg0": ADDR_FREQ0_REG0,
            "reg1": ADDR_FREQ0_REG1,
            "reg2": ADDR_FREQ0_REG2,
            "reg3": ADDR_FREQ0_REG3,

            "select": SELECT_FREQ0_CHANNEL
        },
        FREQ1_CHANNEL: {
            "reg0": ADDR_FREQ1_REG0,
            "reg1": ADDR_FREQ1_REG1,
            "reg2": ADDR_FREQ1_REG2,
            "reg3": ADDR_FREQ1_REG3,

            "select": SELECT_FREQ1_CHANNEL
        },
        PHASE0_CHANNEL: {
            "reg0": ADDR_PHASE0_REG0,
            "reg1": ADDR_PHASE0_REG1,

            "select": SELECT_PHASE0_CHANNEL
        },
        PHASE1_CHANNEL: {
            "reg0": ADDR_PHASE1_REG0,
            "reg1": ADDR_PHASE1_REG1,

            "select": SELECT_PHASE1_CHANNEL
        },
        PHASE2_CHANNEL: {
            "reg0": ADDR_PHASE2_REG0,
            "reg1": ADDR_PHASE2_REG1,

            "select": SELECT_PHASE2_CHANNEL
        },
        PHASE3_CHANNEL: {
            "reg0": ADDR_PHASE3_REG0,
            "reg1": ADDR_PHASE3_REG1,

            "select": SELECT_PHASE3_CHANNEL
        }
    }


class AD9832(object):
    '''
    AD9832 Driver
        The AD9832 is a numerically controlled oscillator employing a phase accumulator,
        a sine look-up table, and a 10-bit digital-to-analog converter (DAC)
        integrated on a single CMOS chip.
        Modulation capabilities are provided for phase modulation and frequency modulation.

    ClassType = DAC

    Args:
        spi_bus:   instance(QSPI)/None,   MIXQSPISG class instance, if not using, will create emulator.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_SPI_0', 256)
        ad9832 = AD9832(axi4_bus)

        # generate 1000 Hz sine waveform, phase is 0.
        ad9832.output("FREQ0", 1000, "PHASE0", 0)

    '''

    rpc_public_api = ['reset', 'enable_output', 'output', 'stop_output']

    def __init__(self, spi_bus=None, mclk=AD9832Def.MCLK):
        if spi_bus is None:
            self.spi_bus = MIXQSPISGEmulator("ad9832_emulator", 256)
        else:
            self.spi_bus = spi_bus
        self._mclk = mclk
        self.reset()

    def write_register(self, reg_value):
        '''
        AD9832 internal function to write register

        Args:
            reg_value:   hexmial, [0-0xffff], 16 bit data to be write.

        Examples:
            ad9832.write_register(0x01)

        '''
        assert isinstance(reg_value, int) and (0 <= reg_value <= 0xffff)

        wr_data = [(reg_value >> 8) & 0xFF]
        wr_data.append(reg_value & 0xFF)

        self.spi_bus.write(wr_data)

    def reset(self):
        '''
        AD9832 internal function to reset

        Returns:
            string, "done", api execution successful.

        Examples:
            ad9832.reset()

        '''
        cmd_data = AD9832Def.CMD_SLEEP_RESET_CLR
        cmd_data |= AD9832Def.RESET_BIT
        self.write_register(cmd_data)

        return 'done'

    def enable_output(self):
        '''
        AD9832 internal function to enable output

        Returns:
            string, "done", api execution successful.

        Examples:
            ad9832.enable_output()

        '''
        cmd_data = AD9832Def.CMD_SLEEP_RESET_CLR
        cmd_data &= ~(AD9832Def.RESET_BIT | AD9832Def.SLEEP_BIT | AD9832Def.CLR_BIT)
        self.write_register(cmd_data)

        return 'done'

    def set_frequency(self, freq_channel, freq_value):
        '''
        AD9832 internal function to set frequency

        Args:
            freq_channel:  string, ['FREQ0', 'FREQ1'], The channel to set frequency.
            freq_value:    float/int, frequency value.

        Examples:
            ad9832.set_frequency('FREQ0', 1000)

        '''
        assert isinstance(freq_value, (int, float)) and (0 <= freq_value <= self._mclk)
        assert freq_channel in {AD9832Def.FREQ0_CHANNEL, AD9832Def.FREQ1_CHANNEL}

        freq_code = int(freq_value * AD9832Def.FREQ_FULL_SCALE / self._mclk)

        self.write_register(AD9832Def.CMD_FREQ_DEFER | AD9832Def.REGS[freq_channel]["reg0"] | (freq_code & 0xFF))
        self.write_register(AD9832Def.CMD_FREQ_SET | AD9832Def.REGS[freq_channel]["reg1"] | ((freq_code >> 8) & 0xFF))
        self.write_register(AD9832Def.CMD_FREQ_DEFER |
                            AD9832Def.REGS[freq_channel]["reg2"] | ((freq_code >> 16) & 0xFF))
        self.write_register(AD9832Def.CMD_FREQ_SET | AD9832Def.REGS[freq_channel]["reg3"] | ((freq_code >> 24) & 0xFF))

    def set_phase(self, phase_channel, phase_value):
        '''
        AD9832 internal function to set phase

        Args:
            phase_channel:  string, ['PHASE0'~'PHASE3'], The channel to set phase.
            phase_value:    float/int, phase value.

        Examples:
            ad9832.set_phase('PHASE1', 1.414)

        '''
        assert isinstance(phase_value, (int, float)) and (0 <= phase_value <= (2 * math.pi))

        assert phase_channel in {AD9832Def.PHASE0_CHANNEL, AD9832Def.PHASE1_CHANNEL,
                                 AD9832Def.PHASE2_CHANNEL, AD9832Def.PHASE3_CHANNEL}

        phase_code = int(phase_value * AD9832Def.PHASE_FULL_SCALE / (2 * math.pi))

        self.write_register(AD9832Def.CMD_PHASE_DEFER | AD9832Def.REGS[phase_channel]["reg0"] | (phase_code & 0xFF))
        self.write_register(AD9832Def.CMD_PHASE_SET |
                            AD9832Def.REGS[phase_channel]["reg1"] | ((phase_code >> 8) & 0xFF))

    def select_freq_phase_channel(self, freq_channel, phase_channel):
        '''
        AD9832 select frequency and phase channel to generate sine waveform

        Args:
            freq_channel:   string, ['FREQ0', 'FREQ1'], frequency channel to generate waveform
            phase_channel:  string, ['PHASE0'~'PHASE3'],  phase channel to generate waveform.

        Examples:
            ad9832.select_freq_phase_channel('FREQ0', 'PHASE1')

        '''
        assert freq_channel in {AD9832Def.FREQ0_CHANNEL, AD9832Def.FREQ1_CHANNEL}
        assert phase_channel in {AD9832Def.PHASE0_CHANNEL, AD9832Def.PHASE1_CHANNEL,
                                 AD9832Def.PHASE2_CHANNEL, AD9832Def.PHASE3_CHANNEL}

        cmd_data = AD9832Def.CMD_FREQ_PHASE_SELECT

        # select frequency channel
        cmd_data |= AD9832Def.REGS[freq_channel]['select']

        # select phase channel
        cmd_data |= AD9832Def.REGS[phase_channel]['select']

        self.write_register(cmd_data)

    def output(self, freq_channel, frequency, phase_channel='PHASE0', phase=0):
        ''''
        AD9832 generate waveform output, just support sine waveform

        Args:
            freq_channel:  string, ['FREQ0', 'FREQ1'], frequency channel to generate output.
            frequency:     float/int, unit Hz, waveform frequency, max support 25MHz.
            phase_channel: string, ['PHASE0'~'PHASE3'], phase channel to generate output.
            phase:         float/int, [0 ~ 2*pi], waveform phase, 0 ~ 2*pi.

        Returns:
            string, "done", api execution successful.

        Examples:
            frequency = 1000
            phase = 0
            ad9832.output('FREQ0', frequency, 'PHASE0', phase)

        '''
        self.stop_output()
        self.set_frequency(freq_channel, frequency)
        self.set_phase(phase_channel, phase)
        self.select_freq_phase_channel(freq_channel, phase_channel)
        self.enable_output()

        return 'done'

    def stop_output(self):
        ''''
        AD9832 stop waveform output

        Returns:
            string, "done", api execution successful.

        Examples:
            ad9832.stop_output()

        '''
        self.reset()

        return 'done'
