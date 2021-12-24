# -*- coding: utf-8 -*-

import math


__author__ = "huangjianxuan@SmartGiant, xuboyan@SmartGiant"
__version__ = "V0.0.2"


class AD9102_Register_Def(object):

    SPICONFIG_REG = 0x00
    REFADJ_REG = 0x03

    DACRSET_REG = 0x0C

    RAMUPDATE_REG = 0x1D
    PAT_STATUS_REG = 0x1E

    PAT_TYPE_REG = 0x1F
    DAC_PAT_REG = 0x2B

    WAV_CONFIG_REG = 0x27
    PAT_TIMEBASE_REG = 0x28
    PAT_PERIOD_REG = 0x29

    DOUT_START_REG = 0x2C

    DACDOF_REG = 0x25
    DAC_CST_REG = 0x31
    DAC_DGAIN_REG = 0x35
    SAW_CONFIG_REG = 0x37

    DDS_TW32_REG = 0x3E
    DDS_TW1_REG = 0x3F
    DDS_PW_REG = 0x43
    DDS_CONFIG_REG = 0x45

    START_DLY_REG = 0x5C
    START_ADDR_REG = 0x5D
    STOP_ADDR_REG = 0x5E
    DDS_CYC_REG = 0x5F


class AD9102Def(object):

    R_COMMAND_WORD = 0x80
    MCLK = 125000000.0  # 125M
    # RESERVED = 0x00

    # SPICONFIG
    RESET_FIELD = 0x1
    RESET_OFFSET = 13
    RESET_MASK = (RESET_FIELD << RESET_OFFSET)
    RESET_SET = 0x1
    RESETM_OFFSET = 2
    RESETM_MASK = (1 << RESETM_OFFSET)
    RESETM_SET = 1

    # REFADJ
    BGDR_VOL_DEFAULT = 1040  # mV, BGDR code = 0x00
    BGDR_VOL_MAX = 1248  # mV, 1040 * (1 + 20%)
    BGDR_VOL_MIN = 832  # mV, 1040 * (1 - 20%)
    BGDR_VOL_ABS_MAX_OFFSET = 208  # mV, 1248 - 1040 = 208, 1040 - 832 = 208
    BGDR_VOL_ABS_MIN_OFFSET = 6  # mV, (1248 - 1040) / 64 = 6
    BGDR_HALF_CODE = 31
    BGDR_FULL_CODE = 63

    # DACRSET
    DAC_RSET_FIELD = 0x1F
    RES_MAX = 16000.0  # MAX(Rset1) = 16KΩ, which is obtained from ad9102 block diagram.
    DAC_RSET_CAL_FIELD = 0x1F
    DAC_RSET_CAL_OFFSET = 8
    DAC_RSET_EN_FIELD = 1
    DAC_RSET_EN_OFFSET = 15
    DAC_RSET_VALUE_DEFAULT = 10  # 0x0A

    # RAMUPDATE
    UPDATE_CMD = 0x1

    # PAT_STATUS
    BUF_READ_OFFSET = 3
    MEM_ACCESS_OFFSET = 2

    # PAT_TYPE
    PAT_CONTINUOUS = 0
    PAT_REPEATS = 1

    # DAC_PAT
    DAC_REPEAT_CYCLE_FIELD = 0xFF

    # WAV_CONFIG
    PRESTORE_SEL_FIELD = 0x3
    PRESTORE_SEL_OFFSET = 4
    PRESTORE_SEL_MASK = PRESTORE_SEL_FIELD << PRESTORE_SEL_OFFSET
    PRESTORE_SEL = {"dc": 0, "sawtooth": 1, "random_seq": 2, "dds": 3}
    CH_ADD_FIELD = 0x1
    CH_ADD_OFFSET = 2
    CH_ADD_MASK = CH_ADD_FIELD << CH_ADD_OFFSET
    WAVE_SEL_MASK = 0x3
    WAVE_SEL = {"ram": 0, "pre": 1, "start_delay": 2, "pre_ram": 3}

    # PAT_TIMEBASE
    PAT_TIMEBASE_VALUE_DEFAULT = 1

    # DACDOF
    DAC_DIG_OFFSET_FIELD = 0xFFF
    DAC_DIG_OFFSET_OFFSET = 4
    DACDOF_OFFSET_MAX = 0.5
    DACDOF_RANGE_SIZE = 1.0

    # DAC_CST
    # If MSB = 1, the data is negative; if MSB = 0, the data is positive.
    DAC_CONST_FIELD = 0xFFF
    DAC_CONST_OFFSET = 4
    DAC_CST_OFFSET_MAX = 0.5
    DAC_CST_RANGE_SIZE = 1.0

    # DAC_DGAIN
    DAC_DGAIN_FIELD = 0xFFF
    DAC_DGAIN_OFFSET = 4
    DAC_DGAIN_VALUE_DEFAULT = 1.0
    DAC_DGAIN_OFFSET_MAX = 2.0
    DAC_DGAIN_RANGE_SIZE = 4.0

    # SAW_CONFIG
    SAW_STEP_FIELD = 0x3F
    SAW_STEP_OFFSET = 2
    SAW_STEP_MASK = SAW_STEP_FIELD << SAW_STEP_OFFSET
    SAW_TYPE_MASK = 0x3
    SAW_TYPE = {"positive": 0, "negative": 1, "triangle": 2, "none": 3}

    # DDS_TW32 & DDS_TW1
    DDSTW_MSB_FIELD = 0xFFFF
    DDSTW_LSB_FIELD = 0xFF
    DDSTW_LSB_OFFSET = 8
    DDSTW_LSB_LEN = 8

    # DDS_PW
    DDS_PHASE_FIELD = 0xFFFF

    # START_ADDR
    START_ADDR_OFFSET = 4

    # STOP_ADDR
    STOP_ADDR_OFFSET = 4

    # The SRAM block is a x12 memory. Its output occupies the 12 MSBs of the 14 bit DAC input.
    RESOLUTION = 12


class AD9102(object):
    '''
    AD9102 chip function class.

    The AD9102 TxDAC and waveform generator is a high performance digital to-analog converter (DAC)
    integrating on-chip pattern memory for complex waveform generation with a direct digital synthesizer (DDS).

    ClassType = DAC

    Args:
        spi:            instance(QSPI)/None, MIXQSPISG class instance.
        mclk:           int/float, reference clock frequency.
        dac_vrff:       int, the on-chip REFIO voltage level.
        cs:             instance(Pin)/None.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_QSPI_SG', 256)
        spi = MIXQSPISG(axi4_bus)
        ad9102 = AD9102(spi)

    '''

    def __init__(self, spi, mclk=AD9102Def.MCLK, dac_vref=AD9102Def.BGDR_VOL_DEFAULT, cs=None):
        self.spi_bus = spi
        self._dac_vref = dac_vref
        self._dac_rset = AD9102Def.DAC_RSET_VALUE_DEFAULT
        self._dac_dgain = AD9102Def.DAC_DGAIN_VALUE_DEFAULT
        self._mclk = mclk
        self._pat_period_base = AD9102Def.PAT_TIMEBASE_VALUE_DEFAULT
        self.cs = cs
        self._resolution = AD9102Def.RESOLUTION

    def write_register(self, reg_addr, reg_value):
        '''
        AD9102 internal function to write register

        Args:
            reg_addr:       hex, [0-0xFFFF], register address.
            reg_value:      hex, [0~0xFFFF], data to be write.

        Examples:
            ad9102.write_register(0x01, 0x11)

        '''
        if self.cs:
            self.cs.set_level(0)
        wr_data = [(reg_addr >> 8) & 0x7F]
        wr_data.append(reg_addr & 0xFF)
        wr_data.append(reg_value >> 8 & 0xFF)
        wr_data.append(reg_value & 0xFF)
        self.spi_bus.write(wr_data)
        if self.cs:
            self.cs.set_level(1)

    def read_register(self, reg_addr):
        '''
        AD9102 internal function to read register

        Args:
            reg_addr:       hex, [0-0xFFFF], register address.

        Returns:
            int, Half-word size, Data to be read.

        Examples:
            ad9102.read_register(0x01)

        '''
        if self.cs:
            self.cs.set_level(0)
        wr_data = [(reg_addr >> 8) & 0x7F | AD9102Def.R_COMMAND_WORD]
        wr_data.append(reg_addr & 0xFF)

        read_data = self.spi_bus.async_transfer(wr_data, 2)
        if self.cs:
            self.cs.set_level(1)
        return read_data[0] << 8 | read_data[1]

    def reset(self):
        '''
        AD9102 internal function to reset device, reloads default register values, except register 0x00.

        Examples:
            AD9102.reset()

        '''
        spiconfig_value = self.read_register(AD9102_Register_Def.SPICONFIG_REG)
        spiconfig_value &= ~AD9102Def.RESET_MASK
        spiconfig_value &= ~AD9102Def.RESETM_MASK
        spiconfig_value |= AD9102Def.RESET_SET << AD9102Def.RESET_OFFSET
        spiconfig_value |= AD9102Def.RESETM_SET << AD9102Def.RESETM_OFFSET
        self.write_register(AD9102_Register_Def.SPICONFIG_REG, spiconfig_value)

    def set_ref_voltage(self, voltage, mode="internal"):
        '''
        Adjust the Vrefio level in register 0x03.
        BGDR code for an on-chip reference with a default voltage (BGDR = 0x00) of 1.04 V.

        Args:
            voltage:        float, [832.0~1248.0], unit mV, for internal referent voltage value.
            mode:           string, ["extern", "internal"], REFIO voltage value.

        Examples:
            AD9102.set_ref_voltage(1040)

        '''
        assert mode in ["extern", "internal"]

        voltage = float(voltage)
        if mode == "internal":
            assert AD9102Def.BGDR_VOL_MIN <= voltage <= AD9102Def.BGDR_VOL_MAX
            res_code = abs(voltage - AD9102Def.BGDR_VOL_DEFAULT)

            # Principle of proximity
            res_code, remainder = divmod(res_code, AD9102Def.BGDR_VOL_ABS_MIN_OFFSET)
            res_code = int(res_code)
            if remainder >= (AD9102Def.BGDR_VOL_ABS_MIN_OFFSET / 2):
                res_code += 1
            if res_code > AD9102Def.BGDR_HALF_CODE:
                res_code = AD9102Def.BGDR_HALF_CODE

            if voltage < AD9102Def.BGDR_VOL_DEFAULT:
                res_code = AD9102Def.BGDR_FULL_CODE - res_code
            reg_value = res_code & 0xFFFF
            self.write_register(AD9102_Register_Def.REFADJ_REG, reg_value)

        self._dac_vref = voltage

    def set_dac_rset(self, res_value=0, mode="manual"):
        '''
        Digital control to set the value of the Rset resistor in the DAC.
        Use to configure DAC output full scale current.

        Args:
            res_value:    int, [0 ~ 16000], Rset resistors value.
            mode:         string, ["manual", "automatic"]

        Examples:
            AD9102.set_dac_rset(16000)

        '''
        assert mode in ["manual", "automatic"]
        assert isinstance(res_value, int) or res_value <= AD9102Def.RES_MAX

        res_value = float(res_value)
        if mode == "manual":
            # bit[4:0]
            res_code = int(res_value / AD9102Def.RES_MAX * AD9102Def.DAC_RSET_FIELD)
        else:
            # bit[12:8]
            res_code = self.read_register(AD9102_Register_Def.DACRSET_REG)
            # bit[4:0]
            res_code = res_code >> AD9102Def.DAC_RSET_CAL_OFFSET & AD9102Def.DAC_RSET_CAL_FIELD
            res_value = float(res_code) / AD9102Def.DAC_RSET_FIELD * AD9102Def.RES_MAX
        reg_value = (AD9102Def.DAC_RSET_EN_FIELD << AD9102Def.DAC_RSET_EN_OFFSET | res_code) & 0xFFFF
        self.write_register(AD9102_Register_Def.DACRSET_REG, reg_value)
        self._dac_rset = res_value

    def set_ram_update(self):
        '''
        Update all SPI settings with a new configuration
        The AD9102 performs this transfer automatically the next time the pattern generator is off.

        Examples:
            AD9102.set_ram_update()

        '''
        self.write_register(AD9102_Register_Def.RAMUPDATE_REG, AD9102Def.UPDATE_CMD)

    def set_pat_status(self, buf_read=0, mem_access=0, run=1):
        '''
        Set PAT_STATUS register value.

        Args:
            buf_read:       int, [0, 1], default 0, read back from updated buffer.
            mem_access:     int, [0, 1], default 0, memory spi access enable.
            run:            int, [0, 1], default 1, allow the pattern generation, and stop patten after trigger.

        Examples:
            AD9102.set_pat_status(0, 0, 1)

        '''
        assert isinstance(buf_read, int)
        assert isinstance(mem_access, int)
        assert isinstance(run, int)

        reg_value = buf_read << AD9102Def.BUF_READ_OFFSET | mem_access << AD9102Def.MEM_ACCESS_OFFSET | run
        self.write_register(AD9102_Register_Def.PAT_STATUS_REG, reg_value)

    def set_pat_type(self, pattern_rpt=0, dac_repeat_cycle=1):
        '''
        Setting this bit allows the pattern to repeat a number of times defined in register 0x002B.

        Args:
            pattern_rpt:        int, [0,1], 0 is pattern continuously runs.
                                            1 is pattern repeats the number of times defined in register 0x002B.
            dac_repeat_cycle:   int, [0-0xFF], default 1, Number of DAC pattern repeat cycles + 1,
                                               (0 means repeat 1 pattern).

        Examples:
            AD9102.set_pat_type(1, 1)

        '''
        assert pattern_rpt in [0, 1]
        assert isinstance(dac_repeat_cycle, int) and 0 <= dac_repeat_cycle <= 0xFF

        if pattern_rpt == 0:
            self.write_register(AD9102_Register_Def.PAT_TYPE_REG, AD9102Def.PAT_CONTINUOUS)
        else:
            reg_value = self.read_register(AD9102_Register_Def.DAC_PAT_REG) & ~AD9102Def.DAC_REPEAT_CYCLE_FIELD
            reg_value |= dac_repeat_cycle
            reg_value &= 0xFFFF
            self.write_register(AD9102_Register_Def.PAT_TYPE_REG, AD9102Def.PAT_REPEATS)
            self.write_register(AD9102_Register_Def.DAC_PAT_REG, reg_value)

    def waveform_config(self, prestore_sel, wave_sel="pre"):
        '''
        DAC waveform selectors output.

        Args:
            prestore_sel:   string, ["dc", "sawtooth", "random_seq", "dds"],
                                    dc:             constant value held into DAC contant value MSB/LSB register.
                                    sawtooth:       sawtooth at the frquency defined
                                                        in the DAC sawtooth configuration register.
                                    random_seq:     pseudorandom sequence.
                                    dds:            DDS output.
            wave_sel:       string, ["ram", "pre", "start_delay", "pre_ram"],
                                    ram:            waveform read from RAM between START_ADDR and STOP_ADDR.
                                    pre:            prestore waveform.
                                    start_delay:    prestore waveform using START_DELAY and PATTERN_PERIOD.
                                    pre_ram:        prestore waveform modulated by waveform from RAM.

        Examples:
            AD9102.wav_config("dds", "pre")

        '''
        assert prestore_sel in AD9102Def.PRESTORE_SEL
        assert wave_sel in AD9102Def.WAVE_SEL

        reg_value = self.read_register(AD9102_Register_Def.WAV_CONFIG_REG)
        reg_value &= ~((AD9102Def.PRESTORE_SEL_MASK | AD9102Def.CH_ADD_MASK | AD9102Def.WAVE_SEL_MASK))
        reg_value |= (AD9102Def.PRESTORE_SEL[prestore_sel] << AD9102Def.PRESTORE_SEL_OFFSET |
                      AD9102Def.WAVE_SEL[wave_sel])
        self.write_register(AD9102_Register_Def.WAV_CONFIG_REG, reg_value)

    def set_pat_timebase(self, hold=1, pat_period_base=1, start_delay_base=1):
        '''
        Set PAT_TIMEBASE register value.

        AD9102 data sheet has error in describing the PAT_PERIOD_BASE field of register PAT_TIMEBASE.
        0 = PATTERN_PERIOD LSB = 16 DAC clock period,
        1 = PATTERN_PERIOD LSB = 1 DAC clock period, 2 = PATTERN_PERIOD LSB = 2 DAC clock period and so on.

        Args:
            hold:               int, [0~15], the number of times the DAC value holds the sample,
                                        (0 = DAC holds for 1 sample).
            pat_period_base:    int, [0~15], the number of dac clock periods per pattern_period lsb,
                                        (0 = PATTERN_PERIOD LSB = 16 DAC clock period).
            start_delay_base:   int, [0~15], the number of dac clock periods per start delay,
                                        (0 = START_DELAY × LSB = 1 DAC clock period).

        Examples:
            AD9102.set_pat_timebase(1, 1, 1)

        '''
        assert isinstance(hold, int) and 0 <= hold <= 0xF
        assert isinstance(pat_period_base, int) and 0 <= pat_period_base <= 0xF
        assert isinstance(start_delay_base, int) and 0 <= start_delay_base <= 0xF

        reg_value = hold << 8 | pat_period_base << 4 | start_delay_base

        self.write_register(AD9102_Register_Def.PAT_TIMEBASE_REG, reg_value)
        self._pat_period_base = pat_period_base

    def set_pat_period(self, period):
        '''
        Pattern period register.

        AD9102 data sheet has error in describing the PAT_PERIOD_BASE field of register PAT_TIMEBASE.
        0 = PATTERN_PERIOD LSB = 16 DAC clock period,
        1 = PATTERN_PERIOD LSB = 1 DAC clock period, 2 = PATTERN_PERIOD LSB = 2 DAC clock period and so on.

        Args:
            period:         int/float, period value.
        Examples:
            AD9102.set_pat_period(10)

        '''
        if self._pat_period_base == 0:
            pat_period_base = 16
        else:
            pat_period_base = self._pat_period_base
        assert isinstance(period, (int, float)) and period <= 0xFFFF * pat_period_base

        # The DDS output frequency is DDS_TW / f_CLKP/N / pow(2, 24)
        # The longest pattern period available is 65,535 × 16 / f_CLKP/N.
        # So the pattern period available is PAT_PERIOD × 16/f_CLKP/N
        period = float(period)
        patperiod_value = int(period * self._mclk / pat_period_base)
        self.write_register(AD9102_Register_Def.PAT_PERIOD_REG, patperiod_value)

    def _real_value_to_reg_value(self, range_size, value):
        '''
        Real value to reg value for 12-pin.

        Args:
            range_size:     float, >0, offset range size.
            value:          float, offset value.

        Retruns:
            int, reg value.

        Examples:
            AD9102._real_value_to_reg_value(1.0, 2.0)

        '''
        value = float(value)
        step = range_size / pow(2, self._resolution)
        # Principle of proximity
        res_code, remainder = divmod(abs(value), step)
        res_code = int(res_code)
        if remainder >= (step / 2):
            res_code += 1
        abs_value = res_code * step

        if value >= 0:
            reg_value = int(abs_value * (1 / step))
            if reg_value >= pow(2, self._resolution):
                reg_value = pow(2, self._resolution) - 1
        else:
            reg_value = int(-abs_value * (1 / step)) + pow(2, self._resolution)
            if reg_value <= pow(2, self._resolution - 1):
                reg_value = pow(2, self._resolution - 1)
        return reg_value

    def set_dac_doffset(self, offset):
        '''
        Set DACDOF register value.

        Args:
            offset:         float, [-0.5~0.5], offset value.

        Examples:
            AD9102.set_dac_doffset(0.2)

        '''
        assert -AD9102Def.DACDOF_OFFSET_MAX <= offset <= AD9102Def.DACDOF_OFFSET_MAX

        range_size = AD9102Def.DACDOF_RANGE_SIZE
        reg_value = self._real_value_to_reg_value(range_size, offset)
        reg_value = reg_value << AD9102Def.DAC_DIG_OFFSET_OFFSET
        self.write_register(AD9102_Register_Def.DACDOF_REG, reg_value)

    def set_dac_cst(self, offset):
        '''
        Most significant byte of DAC constant value.

        Args:
            offset:         float, [-0.5~0.5], offset value.

        Examples:
            AD9102.set_dac_cst(0.5)

        '''
        assert -AD9102Def.DAC_CST_OFFSET_MAX <= offset <= AD9102Def.DAC_CST_OFFSET_MAX

        range_size = AD9102Def.DAC_CST_RANGE_SIZE
        reg_value = self._real_value_to_reg_value(range_size, offset)
        reg_value = reg_value << AD9102Def.DAC_CONST_OFFSET & 0xFFFF
        self.write_register(AD9102_Register_Def.DAC_CST_REG, reg_value)

    def set_dac_dgain(self, gain):
        '''
        Set DAC DGAIN register value.(12bit)

        Args:
            gain:         float, [-2.0-2.0], gain value.

        Examples:
            AD9102.ser_dac_dgain(1.0)

        '''
        assert -AD9102Def.DAC_DGAIN_OFFSET_MAX <= gain <= AD9102Def.DAC_DGAIN_OFFSET_MAX

        range_size = AD9102Def.DAC_DGAIN_RANGE_SIZE
        reg_value = self._real_value_to_reg_value(range_size, gain)
        reg_value = reg_value << AD9102Def.DAC_DGAIN_OFFSET & 0xFFFF
        self.write_register(AD9102_Register_Def.DAC_DGAIN_REG, reg_value)
        self._dac_dgain = gain

    def sawtooth_config(self, saw_step, saw_type="triangle"):
        '''
        Configure the type of sawtooth(positive, negative, triangle) for DAC.

        AD9102 data sheet has error in describing the SAW_STEP field of register SAW_CONFIG.
        0 = SAW_STEP LSB = 64 samples,
        1 = SAW_STEP LSB = 1 sample, 2 = SAW_STEP LSB = 2 samples and so on.

        Args:
            saw_step:       int,  [0-0x3F], number of samples per step for the DAC.

            saw_type:       string, ["positive", "negative", "triangle", "none"], default triangle,
                                    positive is ramp up sawtooth wave.
                                    negative is ramp down sawtooth wave.
                                    triangle is triangle sawtooth wave.
                                    none is no wave, zero.
        Examples:
            AD9102.saw_config(1, saw_type="triangle")

        '''
        assert isinstance(saw_step, int) and 0 <= saw_step <= 0x3F
        assert saw_type in AD9102Def.SAW_TYPE

        reg_value = self.read_register(AD9102_Register_Def.SAW_CONFIG_REG)
        reg_value &= ~((AD9102Def.SAW_TYPE_MASK | AD9102Def.SAW_STEP_MASK))
        reg_value |= (saw_step << AD9102Def.SAW_STEP_OFFSET |
                      AD9102Def.SAW_TYPE[saw_type])
        self.write_register(AD9102_Register_Def.SAW_CONFIG_REG, reg_value)

    def set_frequency(self, frequency):
        '''
        AD9102 internal function to set frequency.

        Args:
            frequency:      int, [0-4000000], frequency value.

        Examples:
            ad9102.set_frequency(1000)

        '''
        # The resolution of DDS tuning is  f_CLKP/N / pow(2, 24)
        # The DDS output frequency is DDS_TW * f_CLKP/N / pow(2, 24)
        ddstw_value = int(frequency / self._mclk * pow(2, 24))

        ddstw_msb_value = ddstw_value >> AD9102Def.DDSTW_LSB_LEN & AD9102Def.DDSTW_MSB_FIELD
        self.write_register(AD9102_Register_Def.DDS_TW32_REG, ddstw_msb_value)
        ddstw_lsb_value = (ddstw_value & AD9102Def.DDSTW_LSB_FIELD) << AD9102Def.DDSTW_LSB_OFFSET
        self.write_register(AD9102_Register_Def.DDS_TW1_REG, ddstw_lsb_value)

    def set_phase(self, phase):
        '''
        AD9102 internal function to set phase

        Args:
            phase:          float, [0~6.283185], phase value.

        Examples:
            ad9102.set_phase(0)

        '''
        assert 0 <= phase <= 2 * math.pi

        phase = float(phase)
        phase_code = int(phase / (2 * math.pi) * AD9102Def.DDS_PHASE_FIELD)

        self.write_register(AD9102_Register_Def.DDS_PW_REG, phase_code)

    def set_start_delay(self, delay=0):
        '''
        Set START DELAY register value.

        Args:
            delay: int, [0~0xFFFF], default 0, start delay of DAC.

        Examples:
            AD9102.set_start_delay(0)

        '''
        assert isinstance(delay, int)

        self.write_register(AD9102_Register_Def.START_DLY_REG, delay)

    def set_sram_addr(self, start_addr, stop_addr):
        '''
        Set SRAM start and stop address.

        Args:
            start_addr:     int, [0x000~0xFFF], RAM address where DAC starts to read waveform.
            stop_addr:      int, [0x000~0xFFF], RAM address where DAC stops to read waveform.

        Examples:
            AD9102.set_sram_addr(1, 0x000, 0xFFF)

        '''
        assert isinstance(start_addr, int) and 0x000 <= start_addr <= 0xFFF
        assert isinstance(stop_addr, int) and 0x000 <= start_addr <= 0xFFF

        start_value = start_addr << AD9102Def.START_ADDR_OFFSET & 0xFFFF
        stop_value = stop_addr << AD9102Def.STOP_ADDR_OFFSET & 0xFFFF
        self.write_register(AD9102_Register_Def.START_ADDR_REG, start_value)
        self.write_register(AD9102_Register_Def.STOP_ADDR_REG, stop_value)

    def set_dds_cycles(self, cycle_value):
        '''
        Set DDS_CYC register value.

        Args:
            cycle_value:    int, [0~65535], cycles counts, 0 means 1 cycle.

        Examples:
            AD9102.set_dds_cycles(10)

        '''
        assert isinstance(cycle_value, int) and 0 <= cycle_value <= 0xFFFF

        self.write_register(AD9102_Register_Def.DDS_CYC_REG, cycle_value)

    def set_dc_output(self, offset):
        '''
        AD9102 output dc

        Args:
            gain:           float, [-1~1], current value.

        Examples:
            ad9102.set_dc_output(0)

        '''
        self.set_pat_type()
        self.waveform_config("dc", "pre")
        self.set_dac_cst(offset)
        self.set_ram_update()
        self.set_pat_status()

    def sine_output(self, frequency, gain=1.0, offset=0, phase=0):
        '''
        Output sine wavefrom.

        Args:
            frequency:      int, frequency value.
            gain:           float, [-2.0~2.0], gain value, default 1.0.
            offset:         float, [-0.5~0.5], default 0, offset value.
            phase:          float, [0~6.283185].

        Examples:
            AD9102.sine_output(1000)

        '''
        self.set_pat_type()
        self.waveform_config("dds", "pre")
        self.set_dac_dgain(gain)
        self.set_frequency(frequency)
        self.set_dac_doffset(offset)
        self.set_phase(phase)
        self.set_ram_update()
        self.set_pat_status()

    def sawtooth_output(self, saw_step, gain=1.0, offset=0, saw_type="triangle"):
        '''
        Output Sawtooth wavefrom.

        Please refer to the following links:
        https://ez.analog.com/data_converters/high-speed_dacs/f/q-a/22744/ad9106-sawtooth-frequency-range-as-function-of-clk/136436#136436
        https://ez.analog.com/data_converters/high-speed_dacs/f/q-a/23044/ad9102-clock-source-and-triangle-wave-generation

        AD9102 data sheet has error in describing the SAW_STEP field of register SAW_CONFIG.
        0 = SAW_STEP LSB = 64 samples,
        1 = SAW_STEP LSB = 1 sample, 2 = SAW_STEP LSB = 2 samples and so on.

        Args:
            saw_step:       int, [0~63], saw step, fsaw = fdac / (2^14) / saw_step,
                                                   fdac = mclk.
            gain:           float, [-2.0~2.0], gain value, default 1.0.
            offset:         float, [-0.5~0.5], default 0, offset value.
            saw_type:       string, ["positive", "negative", "triangle", "none"], default triangle, saw type select.

        Examples:
            AD9102.sawtooth_output(1, saw_type="triangle")

        '''
        self.set_pat_type()
        self.waveform_config("sawtooth", "pre")
        self.sawtooth_config(saw_step, saw_type)
        self.set_dac_dgain(gain)
        self.set_dac_doffset(offset)
        self.set_ram_update()
        self.set_pat_status()

    def write_pattern(self, sram_addr, data_list):
        '''
        Write SRAM data.

        Args:
            sram_addr:      int, [0x6000~0x6FFF], SRAM address.
            data_list:      list, [0x000~0xFFF], SRAM write data.

        Examples:
            AD9102.write_pattern(0x6000, [0x000, 0x001])

        '''
        assert isinstance(data_list, list) and len(data_list) > 0
        assert 0x6000 <= sram_addr <= 0x6FFF

        self.reset()
        # To write to SRAM, set the PAT_STATUS register as follows
        self.set_pat_status(0, 1, 0)
        for index in range(len(data_list)):
            # AD9102 data sheet has error in describing the valid bit of register SRAM_DATA.
            # The valid bit of register SRAM_DATA is 12 bits higher.
            # Please refer to the following links:
            # https://ez.analog.com/data_converters/high-speed_dacs/f/q-a/22654/ad9102-internal-sram-size
            self.write_register(sram_addr + index, data_list[index] << 4 & 0xFFFF)

    def play_pattern(self, frequency, start_addr, stop_addr, pat_period_base=1, gain=1.0):
        '''
        Play SRAM waveform data.

        Args:
            frequency:          int/float, frequency value, it is related to the clock of DAC.
            start_addr:         int, [0x000~0xFFF], the start address of the waveform data.
            stop_addr:          int, [0x000~0xFFF], the stop address of the waveform data.
            pat_period_base:    int, [0-0xF], default 1, the number of dac clock periods per pattern_period lsb.
            gain:               float, [-2.0~2.0], gain value, default 1.0.

        Examples:
            waveform_data_list = [0x00A] * 1000
            AD9102.write_pattern(0x6000, waveform_data_list)
            AD9102.play_pattern(1000, 0x000, len(waveform_data_list) - 1)
            AD9102.set_ram_update()

        '''
        assert isinstance(start_addr, int) and start_addr <= 0xFFF
        assert isinstance(stop_addr, int) and stop_addr <= 0xFFF
        assert isinstance(pat_period_base, int) and 0 <= pat_period_base <= 0xF

        self.waveform_config("dds", "ram")
        self.set_pat_timebase(1, pat_period_base)
        period = 1.0 / frequency
        self.set_pat_period(period)
        self.set_dac_dgain(gain)
        self.set_sram_addr(start_addr, stop_addr)
        self.set_ram_update()
        self.set_pat_status()
