# -*- coding: utf-8 -*-

import math


__author__ = 'Jiasheng.Xie@SmartGiant'
__version__ = 'V0.0.1'


class AD9106_Register_Def(object):
    SPICONFIG_REG = 0x00
    REFADJ_REG = 0x03

    DAC4RSET_REG = 0x09
    DAC3RSET_REG = 0x0A
    DAC2RSET_REG = 0x0B
    DAC1RSET_REG = 0x0C

    RAMUPDATE_REG = 0x1D
    PAT_STATUS_REG = 0x1E
    PAT_TYPE_REG = 0x1F

    WAV4_3CONFIG_REG = 0x26
    WAV2_1CONFIG_REG = 0x27

    DAC4DOF_REG = 0x22
    DAC3DOF_REG = 0x23
    DAC2DOF_REG = 0x24
    DAC1DOF_REG = 0x25

    WAV4_3CONFIG = 0x26
    WAV2_1CONFIG = 0x27

    PAT_TIMEBASE_REG = 0x28
    PAT_PERIOD_REG = 0x29

    DAC4_3PATx_REG = 0x2A
    DAC2_1PATx_REG = 0x2B

    DOUT_START_REG = 0x2C

    DAC4_CST_REG = 0x2E
    DAC3_CST_REG = 0x2F
    DAC2_CST_REG = 0x30
    DAC1_CST_REG = 0x31

    DAC4_DGAIN_REG = 0x32
    DAC3_DGAIN_REG = 0x33
    DAC2_DGAIN_REG = 0x34
    DAC1_DGAIN_REG = 0x35

    SAW4_3CONFIG_REG = 0x36
    SAW2_1CONFIG_REG = 0x37

    DDS_TW32_REG = 0x3E
    DDS_TW1_REG = 0x3F

    DDS4_PW_REG = 0x40
    DDS3_PW_REG = 0x41
    DDS2_PW_REG = 0x42
    DDS1_PW_REG = 0x43

    DDS_CONFIG_REG = 0x45

    START_DLY4_REG = 0x50
    START_ADDR4_REG = 0x51
    STOP_ADDR4_REG = 0x52
    DDS_CYC4_REG = 0x53

    START_DLY3_REG = 0x54
    START_ADDR3_REG = 0x55
    STOP_ADDR3_REG = 0x56
    DDS_CYC3_REG = 0x57

    START_DLY2_REG = 0x58
    START_ADDR2_REG = 0x59
    STOP_ADDR2_REG = 0x5A
    DDS_CYC2_REG = 0x5B

    START_DLY1_REG = 0x5C
    START_ADDR1_REG = 0x5D
    STOP_ADDR1_REG = 0x5E
    DDS_CYC1_REG = 0x5F


class AD9106Def(object):
    R_COMMAND_WORD = 0x80
    CONST_MAX = 0x7FF
    CONST_PRECISION = (1 << 12)
    RSET_MAX = 0x1f
    RES_MAX = 16000.0
    PAT_PERIOD_BASE_MAX = 0xf
    BGDR_VOL_MAX = 1248
    BGDR_VOL_MIN = 832
    BGDR_VOL = 208
    BGDR_HALF_CODE = 31
    BGDR_FULL_CODE = 63
    DEFAULT_VOL = 1040

    MAX_DGAIN = 1024

    START_DELAY_MAX = 0xf
    PAT_PERIOD_BASE_BIT = 4
    REPEAT_CYCLE_MAX = 255
    PAT_PERIOD_MAX = 0xffff
    HOLD_BIT = 8
    HOLD_MAX = 0xf
    SRAM_ADDR_MIN = 0x6000
    SRAM_ADDR_MAX = 0x6fff
    START_ADDR_MIN = 0x000
    START_ADDR_MAX = 0xfff
    STOP_ADDR_MIN = 0x000
    STOP_ADDR_MAX = 0xfff
    START_ADDR_BIT = 4
    STOP_ADDR_BIT = 4
    CYCLE_MAX = 0xffff
    PHASE_MAX = 0xffff
    HASE_MAX = 0xffff

    GAIN_MAX = 0xfff
    GAIN_BIT = 4

    POSITIVE_DOFFSET_MAX = 0x7FF
    DOFFSET_MAX = 0xfff
    DOFFSET_PRECISION = (1 << 12)
    OFFSET_BIT = 4
    DAC_CST_BIT = 4
    BUF_READ_BIT = 3
    MEM_ACCESS_BIT = 2
    MCLK = 125000000.0
    RESERVED = 0x00

    RSET_EN_OFFSET = 15
    DAC_RSET_EN = (1 << RSET_EN_OFFSET)

    RESET_BIT = 13
    RESET_MASK = (1 << RESET_BIT)
    RESET_SET = (1 << RESET_BIT)

    RESETM_BIT = 2
    RESETM__MASK = (1 << RESET_BIT)
    RESETM_SET = (1 << RESETM_BIT)

    DOUT_EN_BIT = 10
    DOUT_VAL_BIT = 5
    DOUT_MODE_BIT = 4

    PHASE_FULL_SCALE = 0xffff

    CHAN_OFFSET = {1: 0, 2: 8, 3: 0, 4: 8}
    WAV_CONFIG_REG = {
        1: AD9106_Register_Def.WAV2_1CONFIG_REG,
        2: AD9106_Register_Def.WAV2_1CONFIG_REG,
        3: AD9106_Register_Def.WAV4_3CONFIG,
        4: AD9106_Register_Def.WAV4_3CONFIG,
    }
    DAC_PATx_REG = {
        1: AD9106_Register_Def.DAC2_1PATx_REG,
        2: AD9106_Register_Def.DAC2_1PATx_REG,
        3: AD9106_Register_Def.DAC4_3PATx_REG,
        4: AD9106_Register_Def.DAC4_3PATx_REG,
    }

    DAC_DGAIN_REG = {
        1: AD9106_Register_Def.DAC1_DGAIN_REG,
        2: AD9106_Register_Def.DAC2_DGAIN_REG,
        3: AD9106_Register_Def.DAC3_DGAIN_REG,
        4: AD9106_Register_Def.DAC4_DGAIN_REG,
    }

    DACDOF_REG = {
        1: AD9106_Register_Def.DAC1DOF_REG,
        2: AD9106_Register_Def.DAC2DOF_REG,
        3: AD9106_Register_Def.DAC3DOF_REG,
        4: AD9106_Register_Def.DAC4DOF_REG,
    }

    DACRSET_REG = {
        1: AD9106_Register_Def.DAC1RSET_REG,
        2: AD9106_Register_Def.DAC2RSET_REG,
        3: AD9106_Register_Def.DAC3RSET_REG,
        4: AD9106_Register_Def.DAC4RSET_REG,
    }

    DAC_CST_REG = {
        1: AD9106_Register_Def.DAC1_CST_REG,
        2: AD9106_Register_Def.DAC2_CST_REG,
        3: AD9106_Register_Def.DAC3_CST_REG,
        4: AD9106_Register_Def.DAC4_CST_REG,
    }

    SAW_CONFIG_REG = {
        1: AD9106_Register_Def.SAW2_1CONFIG_REG,
        2: AD9106_Register_Def.SAW2_1CONFIG_REG,
        3: AD9106_Register_Def.SAW4_3CONFIG_REG,
        4: AD9106_Register_Def.SAW4_3CONFIG_REG,
    }

    DDS_PW_REG = {
        1: AD9106_Register_Def.DDS1_PW_REG,
        2: AD9106_Register_Def.DDS2_PW_REG,
        3: AD9106_Register_Def.DDS3_PW_REG,
        4: AD9106_Register_Def.DDS4_PW_REG,
    }

    START_DLY_REG = {
        1: AD9106_Register_Def.START_DLY1_REG,
        2: AD9106_Register_Def.START_DLY2_REG,
        3: AD9106_Register_Def.START_DLY3_REG,
        4: AD9106_Register_Def.START_DLY4_REG
    }

    START_ADDR_REG = {
        1: AD9106_Register_Def.START_ADDR1_REG,
        2: AD9106_Register_Def.START_ADDR2_REG,
        3: AD9106_Register_Def.START_ADDR3_REG,
        4: AD9106_Register_Def.START_ADDR4_REG
    }

    STOP_ADDR_REG = {
        1: AD9106_Register_Def.STOP_ADDR1_REG,
        2: AD9106_Register_Def.STOP_ADDR2_REG,
        3: AD9106_Register_Def.STOP_ADDR3_REG,
        4: AD9106_Register_Def.STOP_ADDR4_REG
    }

    DDS_CYC_REG = {
        1: AD9106_Register_Def.DDS_CYC1_REG,
        2: AD9106_Register_Def.DDS_CYC2_REG,
        3: AD9106_Register_Def.DDS_CYC3_REG,
        4: AD9106_Register_Def.DDS_CYC4_REG
    }

    SAW_STEP_BIT = 2
    SAW_STEP_MIN = 1
    SAW_STEP_MAX = 63
    SAW_STEP_MASK = 0x3F << SAW_STEP_BIT
    SAW_TYPE_MASK = 0x3
    SAW_TYPE = {'positive': 0, 'negative': 1, 'triangle': 2, 'none': 3}

    PRESTORED_SEL_BIT = 4
    PRESTORED_SEL_MASK = 0x3 << PRESTORED_SEL_BIT
    PRESTORE_SEL = {'dc': 0, 'sawtooth': 1, 'random_seq': 2, 'dds': 3}
    WAVE_SEL_MASK = 0x3
    WAVE_SEL = {'ram': 0, 'pre': 1, 'start_delay': 2, 'pre_ram': 3}


class AD9106(object):
    '''
    AD9106 chip function class.

    ClassType = DAC

    Args:
        spi_bus:   instance(QSPI)/None, MIXQSPISG class instance.
        cs:     instance(Pin)/None.
    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 256)
        spi_bus = MIXQSPISG(axi4_bu)
        ad9102 = AD9106(spi_bus)

    '''

    def __init__(self, spi_bus=None, mclk=AD9106Def.MCLK, dac_vref=AD9106Def.DEFAULT_VOL):
        self.spi_bus = spi_bus
        self._dac_vref = dac_vref
        self._dac_rset = dict()
        self._dac_dgain = dict()
        self._mclk = mclk

    def write_register(self, reg_addr, reg_value):
        '''
        AD9106 internal function to write register

        Args:
            reg_addr:    hex,[0-0xffff],   register address.
            reg_value:   hexmial, [0~0xffff], data to be write.

        Examples:
            ad9102.write_register(0x01,0x11)

        '''
        wr_data = [(reg_addr >> 8) & 0x7F]
        wr_data.append(reg_addr & 0xFF)
        wr_data.append((reg_value >> 8) & 0xFF)
        wr_data.append(reg_value & 0xFF)
        self.spi_bus.write(wr_data)

    def read_register(self, reg_addr):
        '''
        AD9106 internal function to read register

        Args:
            reg_addr:    hex,[0-0xffff],   register address.

        Returns:
            int, Half-word size, Data to be read.

        Examples:
            ad9102.read_register(0x01,1).

        '''
        wr_data = [(reg_addr >> 8) & 0x7F | AD9106Def.R_COMMAND_WORD]
        wr_data.append(reg_addr & 0xFF)

        read_data = self.spi_bus.async_transfer(wr_data, 2)
        return read_data[0] << 8 | read_data[1]

    def reset(self):
        '''
        AD9106 internal function to reset device, reloads default register values, except register 0x00.

        Examples:
            AD9106.reset().
        '''
        spiconfig_value = self.read_register(AD9106_Register_Def.SPICONFIG_REG)
        spiconfig_value &= ~AD9106Def.RESET_MASK
        spiconfig_value &= ~AD9106Def.RESETM__MASK
        spiconfig_value |= AD9106Def.RESET_SET
        spiconfig_value |= AD9106Def.RESETM_SET
        self.write_register(AD9106_Register_Def.SPICONFIG_REG, spiconfig_value)

    def set_frequency(self, freq_value):
        '''
        AD9106 internal function to set frequency.

        Args:
                  freq_value: int, [0-0xfff],frequency value.

        Examples:
            ad9102.set_frequency(1000)

        '''
        ddstw_value = int(freq_value / self._mclk * (1 << 24))

        self.write_register(AD9106_Register_Def.DDS_TW1_REG, (ddstw_value & 0xff) << 8)
        self.write_register(AD9106_Register_Def.DDS_TW32_REG, (ddstw_value >> 8) & 0xffff)

    def set_phase(self, dac_channel, phase_value):
        '''
        AD9106 internal function to set phase

        Args:
            dac_channel:     int,      [1, 2, 3, 4] dac output channel.
            phase_value:    int,[0-0xffff], phase value.

        Examples:
            ad9102.set_phase(0)

        '''
        assert isinstance(phase_value, (int, float)) and (0 <= phase_value <= (2 * math.pi))

        phase_code = int(phase_value * AD9106Def.PHASE_FULL_SCALE / (2 * math.pi))

        self.write_register(AD9106Def.DDS_PW_REG[dac_channel], phase_code)

    def waveform_config(self, dac_channel, prestore_sel, wave_sel="pre"):
        '''
        DAC waveform selectors output.

        Args:
            dac_channel:  int,      [1, 2, 3, 4] dac output channel.
            prestore_sel: str,      dc: constant value held into DAC contant value MSB/LSB register.
                                    sawtooth: sawtooth at the frquency defined
                                     in the DAC sawtooth configuration register.
                                    random_seq: pseudorandom sequence.
                                    dds: DDS output.
            wave_sel:     str,      ram: waveform read from RAM between START_ADDR and STOP_ADDR.
                                    pre: prestored waveform.
                                    start_delay: prestored waveform using START_DELAY and PATTERN_PERIOD.
                                    pre_ram: prestored waveform modulated by waveform from RAM.
        Examples:         AD9106.wav_config('dds','pre').
        '''
        assert prestore_sel in AD9106Def.PRESTORE_SEL

        assert wave_sel in AD9106Def.WAVE_SEL
        reg_value = self.read_register(AD9106Def.WAV_CONFIG_REG[dac_channel])
        reg_value &= ~((AD9106Def.PRESTORED_SEL_MASK | AD9106Def.WAVE_SEL_MASK) << AD9106Def.CHAN_OFFSET[dac_channel])
        reg_value |= (AD9106Def.PRESTORE_SEL[prestore_sel] << AD9106Def.PRESTORED_SEL_BIT |
                      AD9106Def.WAVE_SEL[wave_sel]) << AD9106Def.CHAN_OFFSET[dac_channel]
        self.write_register(AD9106Def.WAV_CONFIG_REG[dac_channel], reg_value)

    def sawtooth_config(self, dac_channel, saw_step, saw_type='triangle'):
        '''
        Configure the type of sawtooth(positive, negative, triangle) for DAC.

        Args:
            dac_channel: int,      [1, 2, 3, 4] dac output channel.
            saw_step:    int,  [1-63],     number of samples per step for the DAC.
            saw_type:    str,  default triangle,     positive is ramp up sawtooth wave.
                                    negative is ramp down sawtooth wave.
                                    triangle is triangle sawtooth wave.
                                    none is no wave, zero.
        Examples:
            AD9106.saw_config(1, saw_type='triangle').
        '''
        assert saw_step >= AD9106Def.SAW_STEP_MIN and saw_step <= AD9106Def.SAW_STEP_MAX

        assert saw_type in AD9106Def.SAW_TYPE

        reg_value = self.read_register(AD9106Def.SAW_CONFIG_REG[dac_channel])
        reg_value &= ~((AD9106Def.SAW_TYPE_MASK | AD9106Def.SAW_STEP_MASK) << AD9106Def.CHAN_OFFSET[dac_channel])
        reg_value |= (saw_step << AD9106Def.SAW_STEP_BIT |
                      AD9106Def.SAW_TYPE[saw_type]) << AD9106Def.CHAN_OFFSET[dac_channel]
        self.write_register(AD9106Def.SAW_CONFIG_REG[dac_channel], reg_value)

    def set_ram_update(self):
        '''
        Update all SPI settings with a new configuration

        '''
        self.write_register(AD9106_Register_Def.RAMUPDATE_REG, 0x01)

    def set_pat_type(self, dac_channel, pattern_rpt=0, dac_repeat_cycle=1):
        '''
        Setting this bit allows the pattern to repeat a number of times defined in register 0x002B.

        Args:
            dac_channel:         int, [1, 2, 3, 4], dac output channel.
            pattern_rpt:         int, [0,1],   0 is pattern continuously runs.
                                               1 is pattern repeats the number of times defined in register 0x002B.
            dac_repeat_cycle:    int, [0-255], default 1, Number of DAC pattern repeat cycles + 1,
                                                (0 means repeat 1 pattern).

        Examples:
            AD9106.set_pat_type(1, 0, 1)

        '''
        assert isinstance(dac_repeat_cycle, int)
        assert pattern_rpt in [0, 1]

        assert (dac_repeat_cycle >= 0) and (dac_repeat_cycle <= AD9106Def.REPEAT_CYCLE_MAX)

        if pattern_rpt == 0:
            self.write_register(AD9106_Register_Def.PAT_TYPE_REG, 0)
        else:
            reg_value = self.read_register(AD9106Def.DAC_PATx_REG[dac_channel])
            reg_value |= (dac_repeat_cycle << AD9106Def.CHAN_OFFSET[dac_channel])
            self.write_register(AD9106_Register_Def.PAT_TYPE_REG, 1)
            self.write_register(AD9106Def.DAC_PATx_REG[dac_channel], reg_value)

    def set_pat_status(self, buf_read=0, mem_access=0, run=1):
        '''
        Set PAT_STATUS register value.
        Args:
            buf_read:      int,[0,1], default 0,   read back from updated buffer.
            mem_access:    int,[0,1], default 0,   memory spi access enable.
            run:           int,[0,1], default 1,  allower the pattern generation, and stop patten after trigger.

        Examples:
            AD9106.set_pat_status(buf_read, mem_access, run).
        '''
        assert isinstance(buf_read, int)
        assert isinstance(mem_access, int)
        assert isinstance(run, int)

        reg_value = buf_read << AD9106Def.BUF_READ_BIT | mem_access << AD9106Def.MEM_ACCESS_BIT | run

        self.write_register(AD9106_Register_Def.PAT_STATUS_REG, reg_value)

    def set_dac_dgain(self, dac_channel, gain):
        '''
        Set DAC DGAIN register value.

        Args:
            dac_channel:  int, [1, 2, 3, 4], dac output channel.
            gain:         int, [0-0xfff]     gain value(12bit).

        Examples:
            AD9106.ser_dac_dgain(0x00).
        '''
        assert isinstance(gain, int) and gain <= AD9106Def.GAIN_MAX
        reg_value = gain << AD9106Def.GAIN_BIT
        self.write_register(AD9106Def.DAC_DGAIN_REG[dac_channel], reg_value)

    def set_dac_doffset(self, dac_channel, offset):
        '''
        Set DACDOF register value.

        Args:
            dac_channel: int, [1, 2, 3, 4], dac output channel.
            offset:      int, [0-0xfff],     offset value(12bit).

        Examples:
            AD9106.set_dac_doffset(0x00).

        '''
        assert isinstance(offset, int) and offset <= AD9106Def.DOFFSET_MAX

        reg_value = offset << AD9106Def.OFFSET_BIT
        self.write_register(AD9106Def.DACDOF_REG[dac_channel], reg_value)

    def set_dac_rset(self, dac_channel, res_value, mode="internal"):
        '''
        Digital control to set the value of the Rset resistor in the DAC.
        Use to configure DAC output full scale current.

        Args:
            dac_channel:  int, [1, 2, 3, 4], dac output channel.
            res_value:    int,[0 ~ 16000],    Rset resistors value.

        Examples:
            AD9106.set_dac_rset(0)

        '''
        assert isinstance(res_value, int) or res_value <= AD9106Def.RES_MAX
        if mode == "internal":
            # self._dac_rset = res_value
            res_code = int(res_value / AD9106Def.RES_MAX * AD9106Def.RSET_MAX)
            res_code = AD9106Def.DAC_RSET_EN | res_code
            self.write_register(AD9106Def.DACRSET_REG[dac_channel], res_code)
        else:
            res_code = self.read_register(AD9106Def.DACRSET_REG[dac_channel])
            res_code &= ~(AD9106Def.DAC_RSET_EN)
            self.write_register(AD9106Def.DACRSET_REG[dac_channel], res_code)
        self._dac_rset[dac_channel] = res_value

    def set_dac_cst(self, dac_channel, gain):
        '''
        Most significant byte of DAC constant value.

        Args:
            dac_channel: int, [1, 2, 3, 4], dac output channel.
            gain:        float, [-1 ~ 1], proportional value.

        Examples:
            AD9106.set_dac_cst(1.0).

        '''
        assert isinstance(gain, (int, float))
        if gain > 0:
            reg_value = int(gain * AD9106Def.CONST_MAX) << AD9106Def.DAC_CST_BIT
        else:
            reg_value = int(gain * AD9106Def.CONST_MAX) + AD9106Def.CONST_PRECISION
            reg_value = reg_value << AD9106Def.DAC_CST_BIT
        self.write_register(AD9106Def.DAC_CST_REG[dac_channel], reg_value)

    def set_ref_voltage(self, voltage, mode="internal"):
        '''
        Adjust the Vrefio level in register 0x03.
        Args:
            voltage: int, unit mV, [832~1248] for internal referent voltage value.
            mode:    string, ["extern","internal"], refio voltage value.

        Examples:
            AD9106.set_ref_voltage(1040).

        '''
        assert isinstance(voltage, (int, float))
        if mode == "internal":
            assert voltage >= AD9106Def.BGDR_VOL_MIN and voltage <= AD9106Def.BGDR_VOL_MAX
            reg_value = int(abs(voltage - AD9106Def.DEFAULT_VOL) * AD9106Def.BGDR_HALF_CODE / AD9106Def.BGDR_VOL)
            if voltage < AD9106Def.DEFAULT_VOL:
                reg_value = AD9106Def.BGDR_FULL_CODE - reg_value
            self.write_register(AD9106_Register_Def.REFADJ_REG, reg_value)

        self._dac_vref = voltage

    def _calculate_offset(self, offset):
        '''
        Calculate_offset.
        Args:
            offset:int,[-1~1], offset proportional value.
        Retruns:
            int,offset value.
        Examples:
            AD9106.sine_output(1000,1.664).
        '''
        if offset >= 0:
            offset = int(offset / 1.0 * AD9106Def.POSITIVE_DOFFSET_MAX)
        else:
            offset = int(offset * AD9106Def.POSITIVE_DOFFSET_MAX) + AD9106Def.DOFFSET_PRECISION

        return offset

    def set_dc_output(self, dac_channel, gain):
        '''
        AD9106 output dc

        Args:
            dac_channel:int, [1, 2, 3, 4], dac output channel.
            gain:    float, [-1,1],    current value.
        Examples:
            ad9102.set_dc_current_output(0)

        '''
        self.set_pat_type(dac_channel)
        self.waveform_config(dac_channel, 'dc', 'pre')
        self.set_dac_cst(dac_channel, gain)
        self.set_ram_update()
        self.set_pat_status()

    def sine_output(self, dac_channel, frequency, gain=1.0, offset=0):
        '''
        Output sine wavefrom.
        Args:
            dac_channel: int, [1, 2, 3, 4], dac output channel.
            frequency:   int, frequency value.
            gain:        float, [0~1], gain value, default is 1.0.
            offset:      float, [-1~1], default 0, offset value.
        Examples:
            AD9106.sine_output(1, 1000).
        '''
        self.set_pat_type(dac_channel)
        self.waveform_config(dac_channel, 'dds', 'pre')
        dgain = int(gain / 1.0 * AD9106Def.MAX_DGAIN)
        self.set_dac_dgain(dac_channel, dgain)
        self.set_frequency(frequency)
        offset = self._calculate_offset(offset)
        self.set_dac_doffset(dac_channel, offset)
        self.set_ram_update()
        self.set_pat_status()

    def sawtooth_output(self, dac_channel, saw_step, gain=1.0, offset=0, saw_type='triangle'):
        '''
        Output Sawtooth wavefrom.
        Args:
            dac_channel: int, [1, 2, 3, 4], dac output channel.
            saw_step:    int, [1 ~ 63], saw step.
            gain:        float, [0~1], gain value, default is 1.0.
            offset:      float, [-1~1], default 0, offset value.
            saw_type:    str, ['positive','negative','triangle','none'], default triangle,saw type select.

        Examples:
            AD9106.sawtooth_output(1, 'triangle').
        '''
        self.set_pat_type(dac_channel)
        self.waveform_config(dac_channel, 'sawtooth', 'pre')
        self.sawtooth_config(dac_channel, saw_step, saw_type)
        dgain = int(gain / 1.0 * AD9106Def.MAX_DGAIN)
        self.set_dac_dgain(dac_channel, dgain)
        offset = self._calculate_offset(offset)
        self.set_dac_doffset(dac_channel, offset)
        self.set_ram_update()
        self.set_pat_status()

    def set_pat_timebase(self, hold, pat_period_base, start_delay_base):
        '''
        Set PAT_TIMEBASE register value.

        Args:
            hold:     int, [0~0xf],    The number of times the DAC value holds the sample.
            pat_period_base:     int, [0~0xf],    the number of dac clock periods per pattern_period lsb.
            start_delay_base:    int, [0~0xf],    the number of dac clock periods per start delay.

        Examples:
            AD9106.set_pat_timebase(1, 1, 0).
        '''
        assert isinstance(hold, int) and hold <= 0xf
        assert isinstance(pat_period_base, int) and pat_period_base <= 0xf
        assert isinstance(start_delay_base, int) and start_delay_base <= 0xf

        reg_value = hold << 8 | pat_period_base << 4 | start_delay_base

        self.write_register(AD9106_Register_Def.PAT_TIMEBASE_REG, reg_value)

    def set_pat_period(self, period):
        '''
        Pattern period register.

        Args:
            period:    int, [0~0xffff],    period value.
        Examples:
            AD9106.set_pat_period(0x8000).
        '''
        assert isinstance(period, int) and period <= 0xffff

        self.write_register(AD9106_Register_Def.PAT_PERIOD_REG, period)

    def set_sram_addr(self, dac_channel, start_addr, stop_addr):
        '''
        Set SRAM start and stop address.

        Args:
            dac_channel: int, [1, 2, 3, 4], dac output channel.
            start_addr:     int, [0x000~0xfff],    RAM address where DAC starts to read waveform.
            stop_addr:     int, [0x000~0xfff],    RAM address where DAC stops to read waveform.

        Examples:
            AD9106.set_sram_addr(1, 0x000, 0xfff).
        '''
        assert isinstance(dac_channel, int)
        assert isinstance(start_addr, int)
        assert isinstance(stop_addr, int)
        assert dac_channel in [1, 2, 3, 4]
        assert start_addr >= 0x000 and start_addr <= 0xfff
        assert stop_addr >= 0x000 and stop_addr <= 0xfff

        start_value = start_addr << 4
        stop_value = stop_addr << 4
        self.write_register(AD9106Def.START_ADDR_REG[dac_channel], start_value)
        self.write_register(AD9106Def.STOP_ADDR_REG[dac_channel], stop_value)

    def set_start_delay(self, dac_channel, delay=0):
        '''
        Set START DELAY register value.

        Args:
            dac_channel: int, [1, 2, 3, 4], dac output channel.
            delay: int, [0~0xffff],  default 0, start delay of DAC.

        Examples:
            AD9106.set_start_delay(1, 0).
        '''
        assert dac_channel in [1, 2, 3, 4]
        assert isinstance(delay, int)

        self.write_register(AD9106Def.START_DLY_REG[dac_channel], delay)

    def set_dds_cycles(self, dac_channel, cycle_value):
        '''
        Set DDS_CYC register value.

        Args:
            dac_channel: int, [1, 2, 3, 4], dac output channel.
            cycle_value: int, [0~0xffff]    cycles counts.

        Examples:
            AD9106.set_dds_cycles(3, 10)
        '''
        assert dac_channel in [1, 2, 3, 4]
        assert isinstance(cycle_value, int) and cycle_value <= 0xffff
        self.write_register(AD9106Def.DDS_CYC_REG[dac_channel], cycle_value)

    def write_pattern(self, sram_addr, data_list):
        '''
        Write SRAM data.

        Args:
            sram_addr:    int, [0x6000~0x6fff],     SRAM address.
            data_list:    list, [0x000~0xfff],    SRAM write data.

        Examples:
            AD9106.write_pattern(0x6000, [0x000,0x001]).
        '''
        assert isinstance(data_list, list) and len(data_list) > 0
        assert sram_addr >= 0x6000 and sram_addr <= 0x6fff

        self.reset()
        # To write to SRAM, set the PAT_STATUS register as follows
        self.set_pat_status(0, 1, 0)
        for index in range(len(data_list)):
            # AD9106 data sheet has error in describing the valid bit of register SRAM_DATA.
            # The valid bit of register SRAM_DATA is 12 bits higher.
            self.write_register(sram_addr + index, data_list[index] << 4 & 0xfff0)

    def play_pattern(self, dac_channel, frequency, start_addr, stop_addr,
                     pat_period_base=1, dac_repeat_cycle=1, cycle_value=1, gain=1.0):
        '''
        Play SRAM waveform data.

        Args:
            dac_channel: int, [1, 2, 3, 4], dac output channel.
            frequency: int/float, frequency value, it is related to the clock of DAC.
            start_addr: int, [0x000~0xfff],    the start address of the waveform data.
            stop_addr: int, [0x000~0xfff],    the stop address of the waveform data.
            pat_period_base: int, [0~0xf], default 1, the number of dac clock periods per pattern_period lsb.
            dac_repeat_cycle:    int, [0-255], default 1, Number of DAC pattern repeat cycles + 1,
                                                (0 means repeat 1 pattern).
            cycle_value: int/float, (>0), default 1, the number of waveform cycles in per pattern_period.
            gain:        float, [0~1], gain value, default is 1.0.

        Examples:
            waveform_data_list = [0x00A] * 1000
            AD9106.write_pattern(0x6000, waveform_data_list)
            AD9106.play_pattern(1, 1000, 0x000, len(waveform_data_list) - 1)
            AD9106.play_pattern(2, 1000, 0x000, len(waveform_data_list) - 1)
            AD9106.set_ram_update()
        '''
        assert dac_channel in [1, 2, 3, 4]
        assert isinstance(start_addr, int) and start_addr <= 0xfff
        assert isinstance(stop_addr, int) and stop_addr <= 0xfff
        assert isinstance(pat_period_base, int) and pat_period_base <= 0xf
        assert dac_repeat_cycle >= 0 and dac_repeat_cycle <= 255

        self.set_pat_type(dac_channel, 1, dac_repeat_cycle)
        self.waveform_config(dac_channel, 'dds', 'ram')
        self.set_pat_timebase(1, pat_period_base, 1)
        period = int((self._mclk / pat_period_base / frequency) * cycle_value)
        self.set_pat_period(period)
        dgain = int(gain / 1.0 * AD9106Def.MAX_DGAIN)
        self.set_dac_dgain(dac_channel, dgain)
        self.set_sram_addr(dac_channel, start_addr, stop_addr)
        self.set_pat_status(0, 0, 1)

    def output_sine_pattern(self, dac_channel, frequency, pat_period_base=1,
                            dac_repeat_cycle=1, start_delay=0, cycle_value=1, gain=1.0):
        '''
        Pulsed sine waves in pattern periods.

        Args:
            dac_channel: int, [1, 2, 3, 4], dac output channel.
            frequency: int/float, frequency value, it is related to the clock of DAC.
            pat_period_base: int,[0-0xf], default 1, the number of dac clock periods per pattern_period lsb.
            dac_repeat_cycle:    int, [0-255], default 1, Number of DAC pattern repeat cycles + 1,
                                                (0 means repeat 1 pattern).
            start_delay: int, [0-0xffff], default 0, start delay of DAC.
            cycle_value: int, [0-0xffff], default 1, cycles counts, number of sine wave cycles when DDS
                                          prestored waveform with start and stop delays is selected for DAC output.
            gain:        float, [0~1], gain value, default is 1.0.

        Examples:
            AD9106.output_sine_pattern(1, 1000)
            AD9106.output_sine_pattern(2, 1000)
            AD9106.set_ram_update()
        '''
        assert dac_channel in [1, 2, 3, 4]
        assert isinstance(pat_period_base, int) and pat_period_base <= 0xf
        assert dac_repeat_cycle >= 0 and dac_repeat_cycle <= 255
        assert isinstance(start_delay, int) and start_delay <= 0xffff
        assert isinstance(cycle_value, int) and cycle_value <= 0xffff

        self.set_pat_type(dac_channel, 1, dac_repeat_cycle)
        self.waveform_config(dac_channel, 'dds', 'start_delay')
        self.set_pat_timebase(1, pat_period_base, 1)
        period = int(self._mclk / pat_period_base / frequency)
        self.set_pat_period(period)
        dgain = int(gain / 1.0 * AD9106Def.MAX_DGAIN)
        self.set_dac_dgain(dac_channel, dgain)
        self.set_frequency(frequency)
        self.set_start_delay(dac_channel, start_delay)
        self.set_dds_cycles(dac_channel, cycle_value)
        self.set_pat_status(0, 0, 1)
