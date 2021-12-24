# -*- coding: utf-8 -*-
import time
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator
from mix.driver.core.bus.pin import Pin

__author__ = 'zhangdongdong@SmartGiant'
__version__ = '0.1'


class AD9628Def(object):
    REGISTER_ADDRESS = {
        "chip_id": 0x01,
        "chip_grade_id": 0x02,
        "device_index": 0x05,
        "power_mode": 0x08,
        "output_mode": 0x14,
        "sample_rate": 0x100,
        "transfer_addr": 0xFF,
        "global_clock": 0x09,
        "port_config": 0x00,
        "enhancement_ctrl": 0x0C,
        "test_mode": 0x0D,
        "bist_reg": 0x0E,
        "customer_offset": 0x10,
        "user_pattern_1_L": 0x19,
        "user_pattern_2_L": 0x1B,
        "user_ctrl_reg_2": 0x101,
        "user_ctrl_reg_3": 0x102,
        "overrange_reg": 0x2A,
        "vref_reg": 0x18,
        "output_delay": 0x17,
        "output_adjust": 0x15,
        "clock_phase": 0x16,
        "clock_divide": 0x0B,
        "sync_ctrl": 0x3A
    }

    # The definition comes from the ad9628 chip manual register function.
    SYNC_TRANSFER = 0x02
    # Use enhancement control, Chop mode enabled if Bit 2 is enabled.
    CHOP_MODE_OPEN = 0x04
    CHOP_MODE_CLOSE = 0x00
    CHANNEL_SELECT = {"A": 0x01, "B": 0x02, "BOTH": 0x03}
    OUTPUT_TYPE = {"CMOS": (0x00 << 6), "LVDS_ANSI": (0x02 << 6),
                   "LVDS_REDUCED": (0x03 << 6)}
    OUTPUT_FORMAT = {"OFFSET_BIN": 0x00, "TWOS_COMPLEMENT": 0x01, "GRAY_CODE": 0x02}
    SAMPLE_SPEED = {80000000: 0x03, 105000000: 0x04, 125000000: 0x05}
    RESOLUTION_12_BITS = (0x04 << 3)
    RESOLUTION_10_BITS = (0x06 << 3)
    PHASE_INPUT_CLOCK_CYCLES = {"NO_DELAY": 0x00, "ONE_INPUT": 0x01,
                                "TWO_INPUT": 0x02, "THREE_INPUT": 0x03,
                                "FOUR_INPUT": 0x04, "FIVE_INPUT": 0x05,
                                "SIX_INPUT": 0x06, "SEVEN_INPUT": 0x07}
    CLOCK_DIVIDE = {"BY_1": 0x00, "BY_2": 0x01, "BY_3": 0x02, "BY_4": 0x03,
                    "BY_5": 0x04, "BY_6": 0x05, "BY_7": 0x06, "BY_8": 0x07}
    DCO_STRENGTH = {"1X": (0x00 << 4), "2X": (0x01 << 4),
                    "3X": (0x02 << 4), "4X": (0x03 << 4)}
    DATA_STRENGTH = {"1X": 0x00, "2X": 0x01, "3X": 0x02, "4X": 0x03}
    DATA_OUTPUT_DELAY = {"0_56_NS": 0x00, "1_12_NS": 0x01, "1_68_NS": 0x02,
                         "2_24_NS": 0x03, "2_80_NS": 0x04, "3_36_NS": 0x05,
                         "3_92_NS": 0x06, "4_48_NS": 0x07}
    VREF_LEVEL = {"1_00": 0x00, "1_14": 0x01, "1_33": 0x02,
                  "1_60": 0x03, "2_00": 0x04}
    POWER_MODE = {"POWER_ON": 0x00, "POWER_DOWN": 0x01,
                  "STANDBY": 0x02, "DIGITAL_RESET": 0x03}
    TEST_MODE = {"SINGLE": (0x00 << 6), "ALTERNATE_REPEAT": (0x01 << 6),
                 "ONCE": (0x02 << 6), "ALTERNATE_ONCE": (0x03 << 6)}
    OUTPUT_TEST_MODE = {"OFF": 0x00, "MIDSCALE_SHORT": 0x01, "POSITIVE_FS": 0x02,
                        "NEGATIVE_FS": 0x03, "ALTERNATING_CHECKERBOARD": 0x04,
                        "PN_LONG_SEQUENCE": 0x05, "PN_SHORT_SEQUENCE": 0x06,
                        "ONE_WORD_TOGGLE": 0x07, "USER_TEST_MODE": 0x08,
                        "RAMP_OUTPUT": 0x0F}

    # user-defined
    SLEEP_TIME = 0.001  # Set power mode need to reset it and wait 1 millisecond
    INVERT_DCO = (1 << 7)
    NOT_INVERT_DCO = (0 << 7)
    DIV_NEX_SYNC = (1 << 2)
    DIV_NEX_ASYNC = (0 << 2)
    DIV_SYNC_OPEN = (1 << 1)
    DIV_SYNC_CLOSE = (0 << 1)
    DCO_DELAY_OPEN = (1 << 7)
    DCO_DELAY_CLOSE = (0 << 7)
    DATA_DELAY_OPEN = (1 << 5)
    DATA_DELAY_CLOSE = (0 << 5)
    SOFT_RESET = (1 << 5 | 1 << 2)
    EN_RESET_PN_LONG_GEN = (1 << 5)
    DIS_RESET_PN_LONG_GEN = (0 << 5)
    EN_RESET_PN_SHORT_GEN = (1 << 4)
    DIS_RESET_PN_SHORT_GEN = (0 << 4)
    INIT_BIST_SEQ = ((1 << 2) | 1)
    NOT_INIT_BIST_SEQ = ((0 << 2) | 1)
    EN_OEB_PIN = (1 << 7)
    DIS_OEB_PIN = (0 << 7)
    EN_PDWN_PIN = (1 << 5)
    DIS_PDWN_PIN = (0 << 5)
    VCM_POWER_ON = (1 << 3)
    VCM_POWER_DOWN = (0 << 3)


class AD9628RException(Exception):
    def __init__(self, err_str):
        self.err_reason = 'AD9628R: %s.' % (err_str)

    def __str__(self):
        return self.err_reason


class AD9628(object):
    '''
    The AD9628 is a monolithic, dual-channel, 1.8V supply, 12-bit, 125MSPS/105MSPS analog-to-digital converter (ADC).
    It features a high performance sample-and-hold circuit and onchip voltage reference.
    The digital output data is presented in offset binary, Gray code, or twos complement format.
    A data output clock (DCO) is provided for each ADC channel to ensure proper latch timing with receiving logic.
    1.8V CMOS or LVDS output logic levels are supported. Output data can also be multiplexed onto a single output bus.

    ClassType = ADC

    Args:
        spi_bus:     instance(QSPI)/None,  MIXQSPISG class instance, if not using, will create emulator.
        pdwn_ctrl:   instance(GPIO)/None,  Class instance of GPIO, which is used to control ad9628 pdwn_ctrl signal,
                                           default None for not use.
        oeb_ctrl:    instance(GPIO)/None,  Class instance of GPIO, which is used to control ad9628 oeb_ctrl signal,
                                           default None for not use.
        cs_ctrl:     instance(GPIO)/None,  Class instance of GPIO, which is used to control ad9628 cs_ctrl signal,
                                           default None for not use.
        use_cs:      Bool('True'/'False'), determine if CS is used internally.

    Examples:
        pdwn_ctrl = GPIO(cat9555, 6)
        oeb_ctrl = GPIO(cat9555, 7)
        cs_ctrl = GPIO(cat9555, 12)
        axi4_bus = AXI4LiteBus('/dev/MIX_DUT_SPI_0', 256)
        spi_bus = MIXQSPISG(axi4_bus)
        ad9628 = AD9628(spi_bus, pdwn_ctrl, oeb_ctrl, cs_ctrl)

    '''

    def __init__(self, spi_bus=None, pdwn_ctrl=None, oeb_ctrl=None, cs_ctrl=None, use_cs=True):
        if(spi_bus is None and pdwn_ctrl is None and oeb_ctrl is None):
            self.spi_bus = MIXQSPISGEmulator("ad9628_emulator", 256)
            self.pdwn = Pin(None, 6)
            self.oeb = Pin(None, 7)
        elif(spi_bus is not None and pdwn_ctrl is not None and oeb_ctrl is not None):
            self.spi_bus = spi_bus
            self.pdwn = pdwn_ctrl
            self.oeb = oeb_ctrl
        else:
            raise AD9628RException('__init__ error! Please check the parameters')

        self.use_cs = use_cs
        if(self.use_cs is True and cs_ctrl is not None):
            self.cs = cs_ctrl
        elif(self.use_cs is False and cs_ctrl is None):
            self.cs = Pin(None, 12)
        else:
            raise AD9628RException('cs use error! Please check the parameters')

    def read_register(self, reg_addr):
        '''
        AD9628 internal function to read register

        Args:
            reg_addr:    hexmial, [0~0x102], The register range is 0-0x102 in datasheet, register to be read.

        Returns:
            int, value, register read data.

        Examples:
            rd_data = ad9628.read_register(0x01)
            print(rd_data)
            # rd_data will be like 0x05

        '''
        assert isinstance(reg_addr, int)
        assert 0 <= reg_addr <= 0x102

        if self.use_cs is True:
            self.cs.set_level(0)

        reg_address = (1 << 15) + (reg_addr & 0x3FF)
        read_data = 0
        write_date = [(reg_address >> 8) & 0xFF, reg_address & 0xFF]
        reg_value = self.spi_bus.transfer(write_date, 1, False)
        read_data = reg_value[0]

        if self.use_cs is True:
            self.cs.set_level(1)

        return read_data

    def write_register(self, reg_addr, reg_value):
        '''
        AD9628 internal function to write register

        Args:
            reg_addr:     hexmial, [0~0x102], register to be write.
            reg_value:    hexmial, [0~0xff], data to be write.

        Examples:
            ad9628.write_register(0x01, 0x02)

        '''
        assert isinstance(reg_addr, int)
        assert isinstance(reg_value, int)
        assert 0 <= reg_addr <= 0x102
        assert 0 <= reg_value <= 0xFF

        if self.use_cs is True:
            self.cs.set_level(0)

        reg_address = reg_addr & 0x3FF
        write_date = [(reg_address >> 8) & 0xFF, reg_address & 0xFF, reg_value]
        ret = self.spi_bus.write(write_date)

        if self.use_cs is True:
            self.cs.set_level(1)

        if ret is False:
            return False

        return True

    def get_chip_id(self):
        '''
        AD9628 internal function to get AD9628's chip ID number

        Returns:
            int, value, variable which to store the chip ID.

        Examples:
            id = ad9628.get_chip_id()
            print(id)

        '''
        chip_id = self.read_register(AD9628Def.REGISTER_ADDRESS["chip_id"])
        return chip_id

    def get_clock_speed_grade(self):
        '''
        AD9628 internal function to check AD9628's input clock speed supported, 105000000SPS or 125000000SPS.

        Returns:
            int, value, Return 105000000SPS or 125000000SPS.

        Examples:
            grade = ad9628.clock_speed_grade()
            print(grade)

        '''
        grade = 0
        rd_data = self.read_register(
            AD9628Def.REGISTER_ADDRESS["chip_grade_id"])
        if (((rd_data) >> 4) & 0x07) == 0x04:
            grade = 105000000
        elif (((rd_data) >> 4) & 0x07) == 0x05:
            grade = 125000000
        else:
            raise AD9628RException('get clock speed grade fail!')

        return grade

    def select_channel(self, channel):
        '''
        AD9628 internal function to select which channel to receive SPI command.

        Args:
            channel:    string, ["A", "B", "BOTH"]. select which channel to receive SPI command.

        Examples:
            ad9628.select_channel("A")

        '''
        assert channel in AD9628Def.CHANNEL_SELECT

        self.write_register(
            AD9628Def.REGISTER_ADDRESS["device_index"], AD9628Def.CHANNEL_SELECT[channel])

    def get_sampling_rate(self):
        '''
        AD9628 internal function to get sample rate.

        Returns:
            int, value, Return 80000000SPS, 105000000SPS or 125000000SPS.

        Examples:
            rate = ad9628.get_sampling_rate()
            print(rate)

        '''

        sample_rate = 0
        rd_data = self.read_register(AD9628Def.REGISTER_ADDRESS["sample_rate"])

        if (rd_data & 0x07) == 0x03:
            sample_rate = 80000000
        elif (rd_data & 0x07) == 0x04:
            sample_rate = 105000000
        elif (rd_data & 0x07) == 0x05:
            sample_rate = 125000000
        else:
            raise AD9628RException('get sampling rate fail!')

        return sample_rate

    def setup(self, type, format, msps, bits):
        '''
        AD9628 internal function to Initial AD9628.

        Args:
            type:    string, ["CMOS", "LVDS_ANSI", "LVDS_REDUCED"],
                             configure the data output type of the AD9628.
            format:  string, ["OFFSET_BIN", "TWOS_COMPLEMENT", "GRAY_CODE"],
                             configure the data output format of the AD9628.
            msps:    int, [80000000, 105000000, 125000000],
                          configure the sample speed of data output of the AD9628.
            bits:    string, ["WIDTH_10", "WIDTH_12"],
                             configure the output data bits of the AD9628.

        Examples:
            ad9628.setup("LVDS_ANSI", "OFFSET_BIN", "125000000", "WIDTH_12")

        '''
        assert type in AD9628Def.OUTPUT_TYPE
        assert format in AD9628Def.OUTPUT_FORMAT
        assert msps in AD9628Def.SAMPLE_SPEED
        assert bits in ["WIDTH_10", "WIDTH_12"]

        # Digital Output Enable Function
        self.oeb.set_level(0)
        # self.pdwn.set_level(0), external power down.
        self.power_mode("EXTERNAL", "POWER_DOWN")
        # Internal power-down mode ,register digital reset.
        self.power_mode("INTERNAL", "DIGITAL_RESET")
        # Set power mode need to reset it and wait 1 millisecond
        time.sleep(AD9628Def.SLEEP_TIME)
        self.power_mode("INTERNAL", "POWER_ON")

        output_mode = AD9628Def.OUTPUT_TYPE[type] | AD9628Def.OUTPUT_FORMAT[format]
        self.write_register(
            AD9628Def.REGISTER_ADDRESS["output_mode"], output_mode)

        sample_rate_bits = AD9628Def.RESOLUTION_12_BITS
        if bits == "WIDTH_10":
            sample_rate_bits = AD9628Def.RESOLUTION_10_BITS
        elif bits == "WIDTH_12":
            sample_rate_bits = AD9628Def.RESOLUTION_12_BITS
        else:
            raise AD9628RException('width bits set fail!')
        sample = AD9628Def.SAMPLE_SPEED[msps] | sample_rate_bits
        self.write_register(AD9628Def.REGISTER_ADDRESS["sample_rate"], sample)

        self.write_register(
            AD9628Def.REGISTER_ADDRESS["transfer_addr"], AD9628Def.SYNC_TRANSFER)

    def clock_phase(self, dco_invert_ctrl, phase_ratio):
        '''
        AD9628 internal function to input clock divider phase adjust relative to the encode clock.

        Args:
            dco_invert_ctrl:    string, ["NOT_INVERT", "INVERT"],
                                        control DCO(dat clock output) invert or not.
            phase_ratio:        string, ["NO_DELAY", "ONE_INPUT", "TWO_INPUT", "THREE_INPUT",
                                         "FOUR_INPUT", "FIVE_INPUT", "SIX_INPUT", "SEVEN_INPUT"],
                                        selection of clock delays into the input clock divider.

        Examples:
            ad9628.clock_phase("INVERT", "ONE_INPUT")

        '''
        assert dco_invert_ctrl in ["NOT_INVERT", "INVERT"]
        assert phase_ratio in AD9628Def.PHASE_INPUT_CLOCK_CYCLES

        phase_delay = AD9628Def.PHASE_INPUT_CLOCK_CYCLES[phase_ratio]
        if dco_invert_ctrl == "INVERT":
            phase_con = (AD9628Def.INVERT_DCO | phase_delay)
        else:
            phase_con = (AD9628Def.NOT_INVERT_DCO | phase_delay)

        self.write_register(
            AD9628Def.REGISTER_ADDRESS["clock_phase"], phase_con)

    def clock_divide(self, divide_ratio, div_next_sync, div_sync_en):
        '''
        AD9628 internal function to config clock divider's divide ratio.

        Args:
            divide_ratio:     string, ["BY_1", "BY_2", "BY_3", "BY_4", "BY_5", "BY_6", "BY_7", "BY_8"],
                                      config clock divider's divide ratio.
            div_next_sync:    string, ["NEX_SYNC", "NEX_ASYNC"],
                                      config divider next sync only open or not.
            div_sync_en:      string, ["SYNC_OPEN", "SYNC_CLOSE"],
                                      config divider sync open or not.

        Examples:
            ad9628.clock_divide("BY_1", "NEX_SYNC", "SYNC_OPEN")

        '''
        assert divide_ratio in AD9628Def.CLOCK_DIVIDE
        assert div_next_sync in ["NEX_SYNC", "NEX_ASYNC"]
        assert div_sync_en in ["SYNC_OPEN", "SYNC_CLOSE"]

        divider_con = AD9628Def.CLOCK_DIVIDE[divide_ratio]
        self.write_register(
            AD9628Def.REGISTER_ADDRESS["clock_divide"], divider_con)

        if div_next_sync == "NEX_SYNC":
            if div_sync_en == "SYNC_OPEN":
                sync_con = (AD9628Def.DIV_NEX_SYNC | AD9628Def.DIV_SYNC_OPEN)
            else:
                sync_con = (AD9628Def.DIV_NEX_SYNC | AD9628Def.DIV_SYNC_CLOSE)
        else:
            if div_sync_en == "SYNC_OPEN":
                sync_con = (AD9628Def.DIV_NEX_ASYNC | AD9628Def.DIV_SYNC_OPEN)
            else:
                sync_con = (AD9628Def.DIV_NEX_ASYNC | AD9628Def.DIV_SYNC_CLOSE)
        self.write_register(AD9628Def.REGISTER_ADDRESS["sync_ctrl"], sync_con)

    def clock_stabilizer(self, statu):
        '''
        AD9628 internal function to global clock duty cycle stabilizer control.

        Args:
            statu:    string, ["DIS_STABILIZE"/"EN_STABILIZE"],
                              control clock duty cycle stabilizer open or not.

        Examples:
            ad9628.clock_stabilizer("EN_STABILIZE")

        '''
        assert statu in ["DIS_STABILIZE", "EN_STABILIZE"]

        if statu == "EN_STABILIZE":
            stabilizer_con = 0x01
        else:
            stabilizer_con = 0x00
        self.write_register(
            AD9628Def.REGISTER_ADDRESS["global_clock"], stabilizer_con)

    def cmos_output_adjust(self, dco_strength, data_strength):
        '''
        AD9628 internal function to config CMOS output driver strength properties.

        Args:
            dco_strength:     string, ["1X", "2X", "3X", "4X"],
                                      config DCO strength level when chip config in CMOS mode.
            data_strength:    string, ["1X", "2X", "3X", "4X"],
                                      config data strength level when chip config in CMOS mode.

        Examples:
            ad9628.cmos_output_adjust("1X", "1X")

        '''
        assert dco_strength in AD9628Def.DCO_STRENGTH
        assert data_strength in AD9628Def.DATA_STRENGTH

        cmos_adjust = AD9628Def.DCO_STRENGTH[dco_strength] | AD9628Def.DATA_STRENGTH[data_strength]
        self.write_register(
            AD9628Def.REGISTER_ADDRESS["output_adjust"], cmos_adjust)

    def data_output_delay(self, dco_delay_en, data_delay_en, delay):
        '''
        AD9628 internal function to sets the fines output delay of the output clock, not change the internal timeing.

        Args:
            dco_delay_en:     string, ["DCO_DELAY_OPEN", "DCO_DELAY_CLOSE"],
                                      control DCO delay function open or not.
            data_delay_en:    string, ["DATA_DELAY_OPEN", "DATA_DELAY_CLOSE"],
                                      control data delay function open or not.
            delay:            string, ["0_56_NS", "1_12_NS", "1_68_NS", "2_24_NS",
                                       "2_80_NS", "3_36_NS", "3_92_NS", "4_48_NS"], select data delay level.

        Examples:
            ad9628.data_output_delay("DCO_DELAY_OPEN", "DATA_DELAY_OPEN", "1_12_NS")

        '''
        assert delay in AD9628Def.DATA_OUTPUT_DELAY
        assert dco_delay_en in ["DCO_DELAY_OPEN", "DCO_DELAY_CLOSE"]
        assert data_delay_en in ["DATA_DELAY_OPEN", "DATA_DELAY_CLOSE"]

        output_delay = AD9628Def.DATA_OUTPUT_DELAY[delay]
        if dco_delay_en == "DCO_DELAY_OPEN":
            if data_delay_en == "DATA_DELAY_OPEN":
                output_delay = (AD9628Def.DCO_DELAY_OPEN | AD9628Def.DATA_DELAY_OPEN | (output_delay))
            else:
                output_delay = (AD9628Def.DCO_DELAY_OPEN | AD9628Def.DATA_DELAY_CLOSE | (output_delay))
        else:
            if data_delay_en == "DATA_DELAY_OPEN":
                output_delay = (AD9628Def.DCO_DELAY_CLOSE | AD9628Def.DATA_DELAY_OPEN | (output_delay))
            else:
                output_delay = (AD9628Def.DCO_DELAY_CLOSE | AD9628Def.DATA_DELAY_CLOSE | (output_delay))

        self.write_register(
            AD9628Def.REGISTER_ADDRESS["output_delay"], output_delay)

    def vref_set(self, vref, overrange_en):
        '''
        AD9628 internal function to adjuse AD9628 VREF level.

        Args:
            vref:            string, ["1_00", "1_14", "1_33", "1_60", "2_00"], config the inter VREF level.
            overrange_en:    string, ["OVERRANGE", "NOT_OVERRANGE"],  config output overrange enable or not.

        Examples:
            ad9628.vref_set("1_00", "OVERRANGE")

        '''
        assert vref in AD9628Def.VREF_LEVEL
        assert overrange_en in ["OVERRANGE", "NOT_OVERRANGE"]

        overrange_con = 0x01
        if overrange_en == "OVERRANGE":
            overrange_con = 0x01
        else:
            overrange_con = 0x00
        self.write_register(
            AD9628Def.REGISTER_ADDRESS["overrange_reg"], overrange_con)

        vref_con = AD9628Def.VREF_LEVEL[vref]
        self.write_register(AD9628Def.REGISTER_ADDRESS["vref_reg"], vref_con)

    def _internal_power_mode(self, work_mode):
        '''
        AD9628 internal function to config AD9628 internal power mode.

        Args:
            work_mode:    string, ["POWER_ON", "POWER_DOWN", "STANDBY", "DIGITAL_RESET"],
                                  select AD9628's work mode.

        Examples:
            ad9628._internal_power_mode("POWER_ON")

        '''
        assert work_mode in AD9628Def.POWER_MODE

        power_con = 0
        power_con = self.read_register(
            AD9628Def.REGISTER_ADDRESS["power_mode"])
        power_con = ((power_con) & 0xFC) | AD9628Def.POWER_MODE[work_mode]

        self.write_register(
            AD9628Def.REGISTER_ADDRESS["power_mode"], power_con)

    def _external_power_mode(self, work_mode):
        '''
        AD9628 internal function to config AD9628 external power mode.

        Args:
            work_mode:    string, ["POWER_ON", "POWER_DOWN"], select AD9628's work mode.

        Examples:
            ad9628._external_power_mode("POWER_ON")

        '''
        assert work_mode in ["POWER_ON", "POWER_DOWN"]

        if self.pdwn is None:
            raise AD9628RException('power mode set fail!')

        if work_mode == "POWER_ON":
            self.pdwn.set_level(1)
        else:
            self.pdwn.set_level(0)

    def power_mode(self, refer, work_mode):
        '''
        AD9628 internal function to config AD9628 chip power mode.

        Args:
            refer:        string, ["INTERNAL", "EXTERNAL"], select internal or external power mode for controling.
            work_mode:    string, ["POWER_ON", "POWER_DOWN", "STANDBY", "DIGITAL_RESET"],
                                  select AD9628's work mode.

        Examples:
            ad9628.power_mode("EXTERNAL", "POWER_ON")

        '''
        assert refer in ["INTERNAL", "EXTERNAL"]

        if refer == "INTERNAL":
            self._internal_power_mode(work_mode)
        else:
            self._external_power_mode(work_mode)

    def soft_reset(self):
        '''
        AD9628 internal function to AD9628 soft reset.

        Examples:
            ad9628.soft_reset()

        '''
        port_con = self.read_register(
            AD9628Def.REGISTER_ADDRESS["port_config"])
        port_con = ((port_con) | AD9628Def.SOFT_RESET)
        self.write_register(
            AD9628Def.REGISTER_ADDRESS["port_config"], port_con)

    def chop_mode_open(self):
        '''
        AD9628 internal function to AD9628 enhancement control enable.

        Examples:
            ad9628.chop_mode_open()

        '''
        self.write_register(
            AD9628Def.REGISTER_ADDRESS["enhancement_ctrl"], AD9628Def.CHOP_MODE_OPEN)

    def chop_mode_close(self):
        '''
        AD9628 internal function to AD9628 enhancement control disable.

        Examples:
            ad9628.chop_mode_close()

        '''
        self.write_register(
            AD9628Def.REGISTER_ADDRESS["enhancement_ctrl"], AD9628Def.CHOP_MODE_CLOSE)

    def test_mode_config(self, user_mode, rst_pn_l_en, rst_pn_s_en, output_mode):
        '''
        AD9628 internal function to Config test data to AD9628's data output pins.

        Args:
            user_mode:      string, ["SINGLE", "ALTERNATE_REPEAT", "ONCE", "ALTERNATE_ONCE"],
                                    select user test mode.
            rst_pn_l_en:    string, ["EN_RESET_L", "DIS_RESET_L"],
                                    control reset PN long gen enable or not.
            rst_pn_s_en:    string, ["EN_RESET_S", "DIS_RESET_S"],
                                    control reset PN short gen enable or not.
            output_mode:    string, ["OFF", "MIDSCALE_SHORT", "POSITIVE_FS", "NEGATIVE_FS",
                                     "ALTERNATING_CHECKERBOARD", "PN_LONG_SEQUENCE", "PN_SHORT_SEQUENCE",
                                     "ONE_WORD_TOGGLE", "USER_TEST_MODE", "RAMP_OUTPUT"],
                                    select user output mode.

        Examples:
            ad9628.test_mode_config("SINGLE", "EN_RESET_L", "EN_RESET_S", "OFF")

        '''
        assert rst_pn_l_en in ["EN_RESET_L", "DIS_RESET_L"]
        assert rst_pn_s_en in ["EN_RESET_S", "DIS_RESET_S"]
        assert user_mode in AD9628Def.TEST_MODE
        assert output_mode in AD9628Def.OUTPUT_TEST_MODE

        user_test_mode_con = AD9628Def.TEST_MODE[user_mode]
        output_test_mode_con = AD9628Def.OUTPUT_TEST_MODE[output_mode]
        test_mode_con = (user_test_mode_con | AD9628Def.DIS_RESET_PN_LONG_GEN |
                         AD9628Def.DIS_RESET_PN_SHORT_GEN | output_test_mode_con)

        if rst_pn_l_en == "EN_RESET_L":
            if rst_pn_s_en == "EN_RESET_S":
                test_mode_con = (user_test_mode_con | AD9628Def.EN_RESET_PN_LONG_GEN | (
                                 AD9628Def.EN_RESET_PN_SHORT_GEN) | output_test_mode_con)
            else:
                test_mode_con = (user_test_mode_con | AD9628Def.EN_RESET_PN_LONG_GEN | (
                                 AD9628Def.DIS_RESET_PN_SHORT_GEN) | output_test_mode_con)
        else:
            if rst_pn_s_en == "EN_RESET_S":
                test_mode_con = ((user_test_mode_con) | AD9628Def.DIS_RESET_PN_LONG_GEN | (
                                 AD9628Def.EN_RESET_PN_SHORT_GEN) | (output_test_mode_con))
            else:
                test_mode_con = ((user_test_mode_con) | AD9628Def.DIS_RESET_PN_LONG_GEN | (
                                 AD9628Def.DIS_RESET_PN_SHORT_GEN) | (output_test_mode_con))

        self.write_register(
            AD9628Def.REGISTER_ADDRESS["test_mode"], test_mode_con)

    def bist_mode_open(self, init_sequence):
        '''
        AD9628 internal function to BIST(build in self test) mode open.

        Args:
            init_sequence:    string, ["INIT_SEQ", "NOT_INIT_SEQ"],
                                      init sequence or not in BIST(build in self test) mode.

        Examples:
            ad9628.bist_mode_open("INIT_SEQ")

        '''
        assert init_sequence in ["INIT_SEQ", "NOT_INIT_SEQ"]

        bist_mode_con = AD9628Def.INIT_BIST_SEQ
        if init_sequence == "INIT_SEQ":
            bist_mode_con = AD9628Def.INIT_BIST_SEQ
        else:
            bist_mode_con = AD9628Def.NOT_INIT_BIST_SEQ

        self.write_register(
            AD9628Def.REGISTER_ADDRESS["bist_reg"], bist_mode_con)

    def bist_mode_close(self):
        '''
        AD9628 internal function to BIST(build in self test) mode close.

        Examples:
            ad9628.bist_mode_close()

        '''
        self.write_register(
            AD9628Def.REGISTER_ADDRESS["bist_reg"], 0X00)

    def customer_offset_adjust(self, data):
        '''
        AD9628 internal function to Customer offset adjust when AD9628 config in twos complement format output type.

        Args:
            data:    hexmial, [0x00~0xFF], write register value.

        Examples:
            ad9628.customer_offset_adjust(0x00)

        '''
        assert isinstance(data, int)
        assert 0 <= data <= 0xFF

        self.write_register(
            AD9628Def.REGISTER_ADDRESS["customer_offset"], data)

    def user_define_pattern(self, pattern, format_data):
        '''
        AD9628 internal function to AD9628 user pattern definetion config.

        Args:
            pattern:        string, ["PATTERN_1", "PATTERN_2"], select which pattern to control.
            format_data:    hexmial, [0x00~0xFFFF], write register value.

        Examples:
            ad9628.user_define_pattern("PATTERN_1", 0x01)

        '''
        assert isinstance(format_data, int)
        assert pattern in ["PATTERN_1", "PATTERN_2"]
        assert 0x00 <= format_data <= 0xFFFF

        if pattern == "PATTERN_1":
            reg_address = AD9628Def.REGISTER_ADDRESS["user_pattern_1_L"] & 0x3FF
        else:
            reg_address = AD9628Def.REGISTER_ADDRESS["user_pattern_2_L"] & 0x3FF

        write_date = []
        write_date.append((reg_address & 0xFF00) >> 8)
        write_date.append(reg_address & 0x00FF)
        write_date.append(format_data >> 8 & 0xFF)
        write_date.append(format_data & 0xFF)
        self.spi_bus.write(write_date)

    def user_io_ctrl(self, io, state):
        '''
        AD9628 internal function to multiplexing pins control.

        Args:
            io:       string, ["OEB", "PDWN", "VCM", "SDIO"], select which IO to control.
            state:    string, ["EN_PIN", "DIS_PIN"],
                              control pin's function disable(effective when pin is PDWN) or enable.

        Examples:
            ad9628.user_io_ctrl("OEB", "EN_PIN")

        '''
        assert io in ["OEB", "PDWN", "VCM", "SDIO"]
        assert state in ["EN_PIN", "DIS_PIN"]

        if io == "OEB":
            rd_data = self.read_register(
                AD9628Def.REGISTER_ADDRESS["user_ctrl_reg_2"])
            if state == "EN_PIN":
                wr_data = (rd_data & 0x7F | AD9628Def.EN_OEB_PIN)
            else:
                wr_data = (rd_data & 0x7F | AD9628Def.DIS_OEB_PIN)
            return self.write_register(
                AD9628Def.REGISTER_ADDRESS["user_ctrl_reg_2"], wr_data)
        elif io == "PDWN":
            rd_data = self.read_register(
                AD9628Def.REGISTER_ADDRESS["power_mode"])
            if state == "EN_PIN":
                wr_data = (rd_data & 0xDF | AD9628Def.EN_PDWN_PIN)
            else:
                wr_data = (rd_data & 0xDF | AD9628Def.DIS_PDWN_PIN)
            return self.write_register(
                AD9628Def.REGISTER_ADDRESS["power_mode"], wr_data)
        elif io == "VCM":
            if state == "EN_PIN":
                wr_data = AD9628Def.VCM_POWER_ON
            else:
                wr_data = AD9628Def.VCM_POWER_DOWN
            return self.write_register(
                AD9628Def.REGISTER_ADDRESS["user_ctrl_reg_3"], wr_data)
        elif io == "SDIO":
            rd_data = self.read_register(
                AD9628Def.REGISTER_ADDRESS["user_ctrl_reg_2"])
            if state == "EN_PIN":
                wr_data = (rd_data & 0xFE | 1)
            else:
                wr_data = (rd_data & 0xFE | 0)
            return self.write_register(
                AD9628Def.REGISTER_ADDRESS["user_ctrl_reg_2"], wr_data)
