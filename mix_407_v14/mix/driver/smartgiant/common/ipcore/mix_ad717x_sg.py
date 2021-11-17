import time
import functools
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.bus.axi4_lite_bus_emulator import AXI4LiteBusEmulator
from mix.driver.smartgiant.common.utility.data_operate import DataOperate


__author__ = 'jingyong.xiao@SmartGiant & yuanle@SmartGiant'
__version__ = '0.2'


class AD717XDef:
    '''
    AD717XDef shows the registers address of AD717X
    '''

    DEFAULT_TIMEOUT = 1
    DEFAULT_DELAY = 0.001
    STATUS_REG_ADDR = 0x00
    ADC_MODE_REG_ADDR = 0x01
    INTERFACE_MODE_REG_ADDR = 0x02
    ID_REG_ADDR = 0x7
    CH0_REG_ADDR = 0x10
    CH1_REG_ADDR = 0x11
    CH2_REG_ADDR = 0x12
    CH3_REG_ADDR = 0x13
    WAIT_STEADY_COUNT = 12
    DATA_REG_ADDR = 0x04
    SETUPCON0_REG_ADDR = 0x20
    SETUPCON1_REG_ADDR = 0x21
    FILTER0_REG_ADDR = 0x28
    FILTER1_REG_ADDR = 0x29
    FILTER2_REG_ADDR = 0x2A
    FILTER3_REG_ADDR = 0x2B

    ADC_ERROR_BIT = (1 << 6)
    DATA_WIDTH = 32
    DATA_MASK = (1 << DATA_WIDTH) - 1

    CHANNELS = {"ch0", "ch1", "ch2", "ch3", "all", 0, 1, 2, 3}

    CHAN_REG_ADDR = {
        "ch0": CH0_REG_ADDR, "ch1": CH1_REG_ADDR,
        "ch2": CH2_REG_ADDR, "ch3": CH3_REG_ADDR}

    POLARS = {"bipolar": 0x01, "unipolar": 0x00}
    BUFFERS = {"enable": 0x0f, "disable": 0x00}
    REFERENCES = {"extern": 0x00, "internal": 0x02, "AVDD-AVSS": 0x03}
    SETUP_REG_ADDR = {"ch0": 0x20, "ch1": 0x21, "ch2": 0x22, "ch3": 0x23}

    SETUPS = {"ch0": 0x00, "ch1": 0x01, "ch2": 0x02, "ch3": 0x03}

    AINS = {"AIN0": 0x0, "AIN1": 0x01, "AIN2": 0x02,
            "AIN3": 0x03, "AIN4": 0x04, "Temp+": 0x11,
            "Temp-": 0x12, "AVDD1": 0x13, "AVSS": 0x14,
            "REF+": 0x15, "REF-": 0x16}

    CLOCKSEL = {
        "internal": 0x00,
        "output": 0x04,
        "external": 0X08,
        "crystal": 0x0c
    }
    CLOCKSEL_MASK = 0x0c

    SINCSEL = {
        "sinc5_sinc1": 0x00,
        "sinc3": 0x60
    }

    SAMPLING_CONFIG_TABLE_AD7175 = {5: 0x14,
                                    10: 0x13, 16.66: 0x12,
                                    20: 0x11, 49.96: 0x10,
                                    59.92: 0x0f, 100: 0x0e,
                                    200: 0x0d, 397.5: 0x0c,
                                    500: 0x0b, 1000: 0x0a,
                                    2500: 0x09, 5000: 0x08,
                                    10000: 0x07, 15625: 0x06,
                                    25000: 0x05, 31250: 0x04,
                                    50000: 0x03, 62500: 0x02,
                                    125000: 0x01, 250000: 0x00}

    SAMPLING_CONFIG_TABLE_AD7177 = {5: 0x14,
                                    10: 0x13, 16.66: 0x12,
                                    20: 0x11, 49.96: 0x10,
                                    59.92: 0x0f, 100: 0x0e,
                                    200: 0x0d, 397.5: 0x0c,
                                    500: 0x0b, 1000: 0x0a,
                                    2500: 0x09, 5000: 0x08,
                                    10000: 0x07}

    SAMPLING_CONFIG_TABLE_AD7172 = {1.25: 0x16, 2.5: 0x15,
                                    5: 0x14,
                                    10: 0x13, 16.63: 0x12,
                                    20.01: 0x11, 49.68: 0x10,
                                    59.52: 0x0f, 100.2: 0x0e,
                                    200.3: 0x0d, 381: 0x0c,
                                    503.8: 0x0b, 1007: 0x0a,
                                    2597: 0x09, 5208: 0x08,
                                    10417: 0x07, 15625: 0x06,
                                    31250: 0x05}

    AD7175_CHIP_ID = 0x0cd0
    AD7177_CHIP_ID = 0x4fd0
    AD7172_CHIP_ID = 0x00d0


class MIXAD717XSGDef:
    ENABLE_REGISTER = 0x10
    BUSY_STAT_REGISTER = 0x26
    START_SPI_REGITSER = 0x24
    READ_DATA_REGISTER = 0x28
    WRITE_DATA_REGISTER = 0x20
    WRITE_FLUSH_REGISTER = 0x24
    DATA_COUNT_REGISTER = 0x12
    DATA_READY_REGISTER = 0x11
    DATA_CONTINUOS_REGISTER = 0x2C
    MAX_VALUE_CONFIG_REGISTER = 0x30
    MAX_VALUE_SAMPLES_REGISTER = 0x31
    MAX_VALUE_CONFIG_ENABLE = 0x01
    MAX_VALUE_CONFIG_DUAL_CHANNEL = 0x10
    MIN_VALUE_CONFIG_ENABLE = 0x02
    REG_SIZE = 0x4000


class MIXAD717XSGException(Exception):
    '''
    MIXAD717XSGException shows the exception of AD717X
    '''

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


def CHAN(chan):
    if isinstance(chan, int):
        return "ch{}".format(chan)
    # default channel type is string
    return chan


class MIXAd717xSG(object):
    '''
    MIXAD717XSG ADC function class. This is a base class of AD717X IP core.

    ClassType = ADC

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string/None, instance or dev path of AXI4 bus,
                                                        If None, will create Emulator.
        mvref:       float, unit mV, reference voltage.
        code_polar:  string, ['bipolar', 'unipolar'], Input channel polar/unipolar config.
        reference:   string, ['extern', 'internal'], reference voltage select.
        buffer_flag: string, ['enable', 'disable'], buffer function enable or disable.
        clock:       string, ['internal', 'output', 'external', 'crystal'], select AD717x chip clock.

    Examples:
        ad717x = MIXAD717XSG('/dev/MIX_AD717X_x', 2500)

    AD7172, AD7175 and AD7177's sample rate range is different, details as below:

    +--------+------------+---------+----------+
    |AD7172  | AD7175     |  AD7177 |   unit   |
    +========+============+=========+==========+
    |1       |  5         |  5      |   'sps'  |
    +--------+------------+---------+----------+
    |2       |  10        |  10     |   'sps'  |
    +--------+------------+---------+----------+
    |5       |  16        |  16     |   'sps'  |
    +--------+------------+---------+----------+
    |10      |  20        |  20     |   'sps'  |
    +--------+------------+---------+----------+
    |16      |  49        |  49     |   'sps'  |
    +--------+------------+---------+----------+
    |20      |  59        |  59     |   'sps'  |
    +--------+------------+---------+----------+
    |49      |  100       |  100    |   'sps'  |
    +--------+------------+---------+----------+
    |59      |  200       |  200    |   'sps'  |
    +--------+------------+---------+----------+
    |100     |  397       |  397    |   'sps'  |
    +--------+------------+---------+----------+
    |200     |  500       |  500    |   'sps'  |
    +--------+------------+---------+----------+
    |381     |  1000      |  1000   |   'sps'  |
    +--------+------------+---------+----------+
    |503     |  2500      |  2500   |   'sps'  |
    +--------+------------+---------+----------+
    |1007    |  5000      |  5000   |   'sps'  |
    +--------+------------+---------+----------+
    |2597    |  10000     |  10000  |   'sps'  |
    +--------+------------+---------+----------+
    |5208    |  15625     |    /    |   'sps'  |
    +--------+------------+---------+----------+
    |10417   |  25000     |    /    |   'sps'  |
    +--------+------------+---------+----------+
    |15625   |  31250     |    /    |   'sps'  |
    +--------+------------+---------+----------+
    |31250   |  50000     |    /    |   'sps'  |
    +--------+------------+---------+----------+
    |   /    |  62500     |    /    |   'sps'  |
    +--------+------------+---------+----------+
    |   /    |  125000    |    /    |   'sps'  |
    +--------+------------+---------+----------+
    |   /    |  250000    |    /    |   'sps'  |
    +--------+------------+---------+----------+

    AD717X Clock source

    +----------------+---------------------------------+
    |  clock         |  description                    |
    +----------------+---------------------------------+
    | 'internal'     |  Internal oscillator            |
    +----------------+---------------------------------+
    | 'output'       |  Internal oscillator and output |
    +----------------+---------------------------------+
    | 'external'     |  External clock source          |
    +----------------+---------------------------------+
    | 'crystal'      |  External crystal               |
    +----------------+---------------------------------+

    '''

    rpc_public_api = ['channel_init', 'reset', 'read_register', 'write_register',
                      'set_setup_register', 'set_sinc', 'set_sampling_rate', 'get_sampling_rate', 'set_channel_state',
                      'select_single_channel', 'read_volt', 'is_communication_ok', 'config_max_value_measure',
                      'enable_continuous_sampling', 'disable_continuous_sampling', 'get_continuous_sampling_voltage']

    def __init__(self, axi4_bus=None, mvref=2500, code_polar="bipolar",
                 reference="extern", buffer_flag="enable", clock="crystal"):
        if axi4_bus is None:
            self.axi4_bus = AXI4LiteBusEmulator("mix_ad717x_sg_emulator",
                                                MIXAD717XSGDef.REG_SIZE)
        elif isinstance(axi4_bus, basestring):
            # dev path; create axi4lite bus here.
            self.axi4_bus = AXI4LiteBus(axi4_bus, MIXAD717XSGDef.REG_SIZE)
        else:
            self.axi4_bus = axi4_bus
        self.mvref = mvref
        self.clock = AD717XDef.CLOCKSEL[clock]
        self.sample_rate_table = AD717XDef.SAMPLING_CONFIG_TABLE_AD7175
        self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.ENABLE_REGISTER, [0x00])
        self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.ENABLE_REGISTER, [0x01])

        wr_data = [0xFF, 0x01]
        self.axi4_bus.write_8bit_inc(0x24, wr_data)
        self.resolution = 24
        self.samples = 1

        self.config = {
            "ch0": {"P": "AIN0", "N": "AIN1"},
            "ch1": {"P": "AIN2", "N": "AIN3"}
        }
        self.max_chan = 3
        self.continue_sampling_mode_ch_state = "all"
        self.chip_id = AD717XDef.AD7175_CHIP_ID
        self.sampling_rates = {}
        self.code_polar = code_polar
        self.reference = reference
        self.buffer_flag = buffer_flag
        self.channel_init()

    def channel_init(self):
        for channel in self.config:
            self.set_setup_register(channel, self.code_polar, self.reference, self.buffer_flag)

    def reset(self, register_state=None):
        '''
        MIXAD717XSG reset chip

        Args:
            register_state: dict/None, the register state when reset,
                                             eg:{0x10:0x8001, 0x11:0x9043}
                                             None: all registers keep
                                             default state.

        Examples:
            ad717x.reset()

        '''
        # assert not register_state or isinstance(register_state, dict)
        filter_list = [x for x in [0x00, 0x03, 0x04] if register_state is not None and x in register_state]
        if register_state is not None and filter_list:
            raise MIXAD717XSGException(
                "0x%2x is a read-only register, not allowed to write!"
                % (filter_list[0]))
        self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.ENABLE_REGISTER, [0x00])
        self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.ENABLE_REGISTER, [0x01])

        # reset ad717x
        wr_data = [0xFF, 0x01]
        self.axi4_bus.write_8bit_inc(0x24, wr_data)

        if register_state:
            for reg_addr, reg_data in register_state.items():
                self.write_register(reg_addr, reg_data)

    def read_register(self, reg_addr):
        '''
        MIXAD717XSG read the register value

        Args:
            reg_addr:    hexmial, [0x00~0x3F].

        Returns:
            int, value.

        Raises:
            keyError:   raises an MIXAD717XSGException

        Examples:
            print(ad717x.read_register(0x00))

        '''
        assert isinstance(reg_addr, int) and 0 <= reg_addr <= 0x3F
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXAD717XSGDef.BUSY_STAT_REGISTER, 1)
        if rd_data[0] & 0x01 == 0x00:
            raise MIXAD717XSGException('MIXAD717XSG Bus is busy now')

        # set ad717x comms register to read the other register
        # which register address is reg_addr
        com_data = (0x3F & reg_addr) | (0x1 << 6)
        wr_data = [com_data, 0x01]

        self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.START_SPI_REGITSER, wr_data)
        rd_data = [0x00]
        last_time = time.time()

        timeout_cnt = 0
        while(rd_data[0] & 0x01 == 0x00) and \
                (time.time() - last_time < AD717XDef.DEFAULT_TIMEOUT):
            time.sleep(AD717XDef.DEFAULT_DELAY)
            timeout_cnt = timeout_cnt + 1
            rd_data = self.axi4_bus.read_8bit_inc(
                MIXAD717XSGDef.BUSY_STAT_REGISTER, 1)
        if time.time() - last_time >= AD717XDef.DEFAULT_TIMEOUT:
            raise MIXAD717XSGException('MIXAD717XSG read register wait timeout')
        rd_data = self.axi4_bus.read_32bit_fix(
            MIXAD717XSGDef.READ_DATA_REGISTER, 1)
        return rd_data[0]

    def write_register(self, reg_addr, reg_data, conti_mode=False):
        '''
        MIXAD717XSG write the register value

        Args:
            reg_addr:    hexmial, [0x00~0x3F].
            reg_data:    int.

        Raises:
            keyError:   raises an MIXAD717XSGException

        Examples:
            ad717x.write_register(0x10, 30)

        '''
        assert isinstance(reg_addr, int) and isinstance(
            reg_data, int) and 0 <= reg_addr <= 0x3F
        if reg_addr in [0x00, 0x03, 0x04]:
            raise MIXAD717XSGException("The register address is read only!")
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXAD717XSGDef.BUSY_STAT_REGISTER, 1)
        if rd_data[0] & 0x01 == 0x00:
            raise MIXAD717XSGException('MIXAD717XSG Bus is busy now')

        wr_data = DataOperate.int_2_list(reg_data, 4)
        wr_data.append(0x3F & reg_addr)
        wr_data.append(0x01)
        self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.WRITE_DATA_REGISTER, wr_data)

        if conti_mode is True:
            return True

        rd_data = [0x00]

        last_time = time.time()

        while(rd_data[0] & 0x01 == 0x00) and (time.time() - last_time < AD717XDef.DEFAULT_TIMEOUT):
            time.sleep(AD717XDef.DEFAULT_DELAY)
            rd_data = self.axi4_bus.read_8bit_inc(
                MIXAD717XSGDef.BUSY_STAT_REGISTER, 1)

        if time.time() - last_time >= AD717XDef.DEFAULT_TIMEOUT:
            raise MIXAD717XSGException('MIXAD717XSG write register wait timeout')

        return True

    def _value_2_mvolt(self, code, mvref, bits, gain=0x555555, offset=0x800000):
        '''
        translate the value to voltage value

        Args:
            code:    int.
            mvref:   float, unit mV.
            bits:    int, [16, 24, 32].
            gain:    int, default 0x555555, gain register value, nominal value 0x555555.
            offset:  int, default 0x800000, offset register value.

        Returns:
            float, value, unit mV.

        '''
        if "bipolar" == self.code_polar:
            tmp = float(code - (1 << bits - 1)) * 0x400000 / gain
            volt = float(tmp + (offset - 0x800000)) / (1 << bits - 1) * mvref / 0.75
        else:
            tmp = float(code / 2.0) * 0x400000 / gain
            volt = float(tmp + (offset - 0x800000)) / (1 << bits - 1) * mvref / 0.75

        return volt

    def set_setup_register(self, channel, code_polar="bipolar", reference="extern", buffer_flag="enable"):
        '''
        AD717x setup register set, code polar,refrence, buffer

        Args:
            channel:    string, ["ch0", "ch1", "ch2", "ch3"], The channel to config setup_register.
            code_polar: string, ["unipolar", "bipolar"],      "unipolar" for unipolar input,
                                                              "bipolar" for bipolar input.
            reference:  string, ["extern", "internal", "AVDD-AVSS"],  Select voltage reference.
            buffer:     string, ["enable", "disable"],                Enable or disable input buffer.

        Examples:
            ad717x.set_setup_register("ch0", "bipolar", "extern", "enable")

        '''

        self.code_polar = code_polar
        value = 0x0
        value |= AD717XDef.POLARS[code_polar] << 12 | AD717XDef.BUFFERS[buffer_flag] << 8 |\
            AD717XDef.REFERENCES[reference] << 4

        return self.write_register(AD717XDef.SETUP_REG_ADDR[channel], value)

    def set_sinc(self, channel, sinc):
        '''
        AD717X set digtal filter.

        Args:
            channel:    string/int, ["ch0"~"ch3"]/[0~3]
            sinc:       string, ["sinc5_sinc1", "sinc3"]

        Example:
            ad717x.set_sinc("ch0", "sinc5_sinc1")

        '''
        assert channel in ["ch" + str(i) for i in range(4)] or channel in [i for i in range(4)]
        assert sinc in AD717XDef.SINCSEL.keys()

        channel = CHAN(channel)
        filter_reg = (eval("AD717XDef.FILTER" + channel[-1] + "_REG_ADDR"))
        value = self.read_register(filter_reg)

        # bit operation, clear first then set digital filter.
        value = value & (~0x60)
        value = (value | AD717XDef.SINCSEL[sinc])
        self.write_register(filter_reg, value)

    def set_sampling_rate(self, channel, rate):
        '''
        MIXAD717XSG set sample rate of channel

        Args:
            channel: string/int, ["ch0"~"ch3"]/[0~3].
            rate:    float.

        Examples:
            ad717x.set_sampling_rate("ch0", 3000)

        '''
        assert channel in ["ch" + str(i) for i in range(4)] or channel in [i for i in range(4)]

        channel = CHAN(channel)
        filter_reg = (eval("AD717XDef.FILTER" + channel[-1] + "_REG_ADDR"))
        value = self.read_register(filter_reg)

        if rate not in self.sample_rate_table:
            raise MIXAD717XSGException("Sample rate is out of range of MIXAD717XSG capable.")

        for sample_rate, reg_value in self.sample_rate_table.items():
            if sample_rate == rate:
                sampling_code = reg_value

        # bit operation, clear first, then set 1
        value = value & (~0x1f)
        value = (value | sampling_code)
        self.write_register(filter_reg, value)
        self.sampling_rates[channel] = rate

    def get_sampling_rate(self, channel):
        '''
        MIXAD717XSG get sample rate

        Args:
            channel: string/int, ["ch0"~"ch3"]/[0~3].

        Returns:
            int, value, unit sps.

        Examples:
            print(ad717x.get_sampling_rate("ch0"))

        '''

        assert channel in ["ch" + str(i) for i in range(4)] or channel in [i for i in range(4)]

        channel = CHAN(channel)
        filter_reg = eval("AD717XDef.FILTER" + channel[-1] + "_REG_ADDR")
        data = self.read_register(filter_reg)
        # get the rate operation bit, low five bits
        data = data & (0x1f)
        result = None
        for sample_rate, reg_value in self.sample_rate_table.items():
            if reg_value == data:
                result = sample_rate

        if result is None:
            raise MIXAD717XSGException("Register value invalid:0x%x" % (data))

        return result

    def set_channel_state(self, channel, state):
        '''
        MIXAD717XSG set_channel_state

        Args:
            channel: string/int, ["ch0"~"ch3"]/[0~3].
            state:   string, ["enable", "disable"].

        Examples:
                   ad717x.set_channel_state("ch0", "enable")

        '''

        channel = CHAN(channel)
        reg_value = 0x0
        if state == "enable":
            reg_value |= 0x1 << 15

        reg_value |= AD717XDef.SETUPS[channel] << 12
        reg_value |= AD717XDef.AINS[self.config[channel]["P"]] << 5
        reg_value |= AD717XDef.AINS[self.config[channel]["N"]]

        self.write_register(AD717XDef.CHAN_REG_ADDR[channel], reg_value)

    def select_single_channel(self, channel):
        '''
        MIXAD717XSG select_single_channel

        Args:
            channel: string/int, ["ch0"~"ch3"]/[0~3].

        Examples:
            ad717x.select_single_channel("ch0")

        '''
        assert channel in AD717XDef.CHANNELS

        channel = CHAN(channel)
        # close all channeal
        for chan in self.config:
            self.set_channel_state(chan, "disable")

        # open one channel
        self.set_channel_state(channel, "enable")

    def enable(self, channel):
        raise NotImplementedError("Not support funtion")

    def disable(self, channel):
        raise NotImplementedError("Not support function")

    def read_volt(self, channel):
        '''
        MIXAD717XSG read voltage at single conversion mode

        Args:
            channel: string/int, ["ch0"~"ch3"]/[0~3].

        Returns:
            int, value, unit mV.

        Raises:
            keyError:   raises an MIXAD717XSGException

        Examples:
            print(ad717x.get_voltage("ch0"))

        '''
        assert channel in AD717XDef.CHANNELS

        channel = CHAN(channel)
        self.select_single_channel(channel)
        if self.resolution == 24:
            self.write_register(AD717XDef.INTERFACE_MODE_REG_ADDR, 0x0)
        else:
            self.write_register(AD717XDef.INTERFACE_MODE_REG_ADDR, 0x02)

        rd_data = self.read_register(AD717XDef.ADC_MODE_REG_ADDR)

        # set ad717x to continuous conversion mode
        wr_data = rd_data & 0xFF0F
        self.write_register(AD717XDef.ADC_MODE_REG_ADDR, wr_data)

        rd_data = self.read_register(AD717XDef.ADC_MODE_REG_ADDR)
        if rd_data & 0x00F0 != 0:
            raise MIXAD717XSGException(
                "Set ad717x to continuous conversion mode fail!")

        wr_data = rd_data & 0xFF0F | 0x0010
        wr_data &= ~AD717XDef.CLOCKSEL_MASK
        wr_data |= self.clock
        self.write_register(AD717XDef.ADC_MODE_REG_ADDR, wr_data)

        reg_data = self.read_register(AD717XDef.DATA_REG_ADDR)
        if (AD717XDef.ADC_ERROR_BIT & self.read_register(AD717XDef.STATUS_REG_ADDR)):
            raise MIXAD717XSGException('Warning, the voltage value exceeds the range')

        rd_data = self.axi4_bus.read_8bit_inc(
            MIXAD717XSGDef.BUSY_STAT_REGISTER, 1)

        # reg_data is 32 bit width. But for AD7175, only 24 bit is valid
        if self.resolution == 24:
            if rd_data[0] & 0x08 == 0x08:
                # high 24 bit is valid
                reg_data = (reg_data & (0xFFFFFF00)) >> 8
            else:
                # low 24 bit is valid
                reg_data = reg_data & (0x00FFFFFF)
        volt = self._value_2_mvolt(reg_data, self.mvref, self.resolution)
        return volt

    def is_communication_ok(self):
        '''
        MIXAD717XSG read the id of MIXAD717XSG and then confirm whether the communication of SPI bus is OK

        Returns:
            boolean, [True, False].

        Raises:
            keyError:   raises an MIXAD717XSGException

        Examples:
            print(ad717x.is_communication_ok())

        '''

        read_times = 5
        ret = False
        while read_times > 0:
            ret = self.read_register(AD717XDef.ID_REG_ADDR)

            # read ad7175 ID(0x0CDX) or AD7177 ID(0x4FDX)
            if ret is False or (ret & 0xFFF0) != self.chip_id:
                # do something to ensure communication is OK
                self.reset()
                read_times -= 1
                time.sleep(0.001)
            else:
                return True
        if ret is False:
            raise MIXAD717XSGException(
                "An error occurred when communicating with MIXAD717XSG fail.")
        return False

    def config_max_value_measure(self, channel, samples, selection='max'):
        '''
        MIXAD717XSG config max or min value measure

        Args:
            channel: string, ["ch0"~"ch3", "all"].
            samples:     int, [5~100], get max value in every samples data.
            selection (string): 'max'|'min'. This parameter takes effect as long as down_sample is
                                    higher than 1. Default 'max'

        '''
        if samples == 1:
            self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.MAX_VALUE_CONFIG_REGISTER, [0x00])
        else:
            if selection == 'max':
                reg_value = MIXAD717XSGDef.MAX_VALUE_CONFIG_ENABLE
            else:
                reg_value = MIXAD717XSGDef.MIN_VALUE_CONFIG_ENABLE
            reg_value |= MIXAD717XSGDef.MAX_VALUE_CONFIG_DUAL_CHANNEL if channel == 'all' else 0
            self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.MAX_VALUE_SAMPLES_REGISTER,
                                         [samples])
            self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.MAX_VALUE_CONFIG_REGISTER,
                                         [reg_value])

    def enable_continuous_sampling(self, channel, rate, samples=1, selection='max'):
        '''
        MIXAD717XSG enable continuous sampling

        Args:
            channel: string/int, ["ch0"~"ch3", "all"]/[0~3].
            rate:        float
            samples: int, [0]|[5~100], 0 means not enable max sample function.
            selection (string): 'max'|'min'. This parameter takes effect as long as down_sample is
                                    higher than 1. Default 'max'

        Examples:
            ad717x.enable_continuous_sampling("ch0", 1000)

        '''

        assert channel in AD717XDef.CHANNELS
        assert isinstance(rate, (float, int)) and rate > 0
        assert samples == 1 or samples in [i for i in range(5, 101)]
        assert selection in ['max', 'min']

        channel = CHAN(channel)
        self.samples = samples
        self.config_max_value_measure(channel, samples, selection)

        data = self.read_register(AD717XDef.ADC_MODE_REG_ADDR)
        data = data & (~(0xF << 4))
        data &= ~AD717XDef.CLOCKSEL_MASK
        data |= self.clock
        self.write_register(AD717XDef.ADC_MODE_REG_ADDR, data)

        if channel == "all":
            for chan in self.config:
                self.set_channel_state(chan, "enable")
                self.set_sampling_rate(chan, rate)
            if self.resolution == 32:
                self.write_register(AD717XDef.INTERFACE_MODE_REG_ADDR, 0xC2, conti_mode=True)
            else:
                self.write_register(AD717XDef.INTERFACE_MODE_REG_ADDR, 0xC0, conti_mode=True)

        else:
            self.select_single_channel(channel)
            self.set_sampling_rate(channel, rate)
            if self.resolution == 32:
                self.write_register(AD717XDef.INTERFACE_MODE_REG_ADDR, 0x82, conti_mode=True)
            else:
                self.write_register(AD717XDef.INTERFACE_MODE_REG_ADDR, 0x80, conti_mode=True)
        self.continue_sampling_mode_ch_state = channel
        self.sampling_rates[channel] = rate

        self.config_max_value_measure(channel, samples, selection)

    def disable_continuous_sampling(self, channel):
        '''
        MIXAD717XSG disable continuous sampling

        Args:
            channel: string/int, ["ch0", "ch1"]/[0, 1].

        Examples:
            ad717x.disable_continuous_sampling('ch0')

        '''
        wr_data = [0x44, 0x01]
        self.axi4_bus.write_8bit_inc(0x24, wr_data)

        rd_data = [0x00]

        last_time = time.time()

        while(rd_data[0] & 0x01 == 0x00) and (time.time() - last_time < AD717XDef.DEFAULT_TIMEOUT):
            time.sleep(AD717XDef.DEFAULT_DELAY)
            rd_data = self.axi4_bus.read_8bit_inc(
                MIXAD717XSGDef.BUSY_STAT_REGISTER, 1)

        if time.time() - last_time >= AD717XDef.DEFAULT_TIMEOUT:
            raise MIXAD717XSGException('MIXAD717XSG write register wait timeout')

    def _volt_2_channeldata(self, volt):
        '''
        This function convert the ad717x sampling date to the user channel data.

        Args:
            volt (list): ad717x sampling data

        Returns:
            List
        '''
        code_2_mvolt = functools.partial(self._value_2_mvolt,
                                         mvref=self.mvref,
                                         bits=32)
        channel_data = list(map(code_2_mvolt, volt))
        return channel_data

    def get_continuous_sampling_voltage(self, channel, count):
        '''
        MIXAD717XSG get continuous sampling voltage

        Args:
            channel: string/int, ["ch0"~"ch3", 'all']/[0~3].
            count:      int, [1~512], how many data to get.

        Returns:
            list, [value,...] the unit of elements in the list is mV.
                when channel is `all`, result is [[channel0_data], ..., [channel3_data]]
        Raises:
            keyError:   raises an MIXAD717XSGException

        Examples:
            print(ad717x.get_voltage_at_continuous_sampling_mode("ch0", 30))

        '''

        assert channel in ["ch" + str(i) for i in range(4)] + ['all'] or channel in [i for i in range(4)]
        assert isinstance(count, int) and count > 0 and count <= 512

        if channel == 'all':
            if self.continue_sampling_mode_ch_state != "all":
                raise MIXAD717XSGException('ensure sampling state is all')
            sampling_rate = self.sampling_rates['ch0']
            for ch, rate in self.sampling_rates.items():
                if sampling_rate > rate:
                    sampling_rate = rate
        else:
            channel = CHAN(channel)
            if self.continue_sampling_mode_ch_state not in [channel, "all"]:
                raise MIXAD717XSGException('ensure sampling state is consistent')
            sampling_rate = self.sampling_rates[channel]
        # use sampling rate and data count to get sampling time. To ensure the data has been capcuted
        # exclude front 12 count data to ensure data is steady.
        timeout = 1.0 / (self.sampling_rates[channel] / self.samples) * (count + AD717XDef.WAIT_STEADY_COUNT)
        rd_data = self.axi4_bus.read_8bit_inc(
            MIXAD717XSGDef.BUSY_STAT_REGISTER, 1)
        if rd_data[0] & 0x04 != 0x04:
            raise MIXAD717XSGException("MIXAD717XSG not in continue sample mode")
        self.axi4_bus.write_16bit_inc(MIXAD717XSGDef.DATA_COUNT_REGISTER, [count])
        self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.DATA_READY_REGISTER, [0x00])
        self.axi4_bus.write_8bit_inc(MIXAD717XSGDef.DATA_READY_REGISTER, [0x01])

        start_time = time.time()
        while True:
            rd_data = self.axi4_bus.read_8bit_inc(
                MIXAD717XSGDef.DATA_READY_REGISTER, 1)
            if rd_data[0] == 0x00:
                break
            if time.time() - start_time >= timeout:
                raise MIXAD717XSGException('capture data time out')
            time.sleep(0.001)

        get_data = self.axi4_bus.read_32bit_fix(
            MIXAD717XSGDef.DATA_CONTINUOS_REGISTER, count)

        code_mask = AD717XDef.DATA_MASK & ~((1 << (AD717XDef.DATA_WIDTH - self.resolution)) - 1)
        if self.continue_sampling_mode_ch_state == "all":
            code_mask &= ~0xf

        for data in get_data:
            if self.continue_sampling_mode_ch_state == "all" and channel != "all":
                if CHAN(0xF & int(data)) != channel:
                    continue
            if (code_mask & data) == code_mask or not(code_mask & data):
                raise MIXAD717XSGException('Warning, the voltage value exceeds the range')

        channel_data = []
        if self.continue_sampling_mode_ch_state == "all":
            channel_data = []
            # There are two channel data in variable "data",
            # you have to separate it, low 4 bit is the channel
            for ch in range(self.max_chan + 1):
                if channel != "all":
                    if CHAN(ch) != CHAN(channel):
                        continue
                    single_channel_data = [
                        data for data in get_data if 0xF & int(data) == ch
                    ]
                    channel_data = self._volt_2_channeldata(single_channel_data)
                else:
                    single_channel_data = [
                        data for data in get_data if 0xF & int(data) == ch
                    ]
                    single_channel_data = self._volt_2_channeldata(single_channel_data)
                    channel_data.append(single_channel_data)
        else:
            channel_data = self._volt_2_channeldata(get_data)

        return channel_data


class MIXAd7175SG(MIXAd717xSG):
    '''
    AD7175 ADC function class

    ClassType = ADC

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string/None, instance or dev path of AXI4 bus,
                                                        If None, will create Emulator.
        mvref:       float, unit mV, reference voltage.
        code_polar:  string, ['bipolar', 'unipolar'], Input channel polar/unipolar config.
        reference:   string, ['extern', 'internal'], reference voltage select.
        buffer_flag: string, ['enable', 'disable'], buffer function enable or disable.
        clock:       string, ['internal', 'output', 'external', 'crystal'], select AD7175 chip clock.

    Examples:
        ad7175 = MIXAD7175SG('/dev/MIX_AD717X_0', 5000)

    '''

    def __init__(self, axi4_bus=None, mvref=5000, code_polar="bipolar",
                 reference="extern", buffer_flag="enable", clock="crystal"):
        super(MIXAd7175SG, self).__init__(axi4_bus, mvref, code_polar=code_polar,
                                          reference=reference, buffer_flag=buffer_flag, clock=clock)
        self.sample_rate_table = AD717XDef.SAMPLING_CONFIG_TABLE_AD7175
        self.resolution = 24
        self.config = {
            "ch0": {"P": "AIN1", "N": "AIN0"},
            "ch1": {"P": "AIN2", "N": "AIN3"}
        }
        self.chip_id = AD717XDef.AD7175_CHIP_ID


class MIXAd7177SG(MIXAd717xSG):
    '''
    AD7177 ADC function class

    ClassType = ADC

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string/None, instance or dev path of AXI4 bus,
                                                        If None, will create Emulator.
        mvref:       float, unit mV, reference voltage.
        code_polar:  string, ['bipolar', 'unipolar'], Input channel polar/unipolar config.
        reference:   string, ['extern', 'internal'], reference voltage select.
        buffer_flag: string, ['enable', 'disable'], buffer function enable or disable.
        clock:       string, ['internal', 'output', 'external', 'crystal'], select AD7177 chip clock.

    Examples:
        ad7177 = MIXAD7177SG('/dev/MIX_AD717X_0', 2500)

    '''

    def __init__(self, axi4_bus=None, mvref=2500, code_polar="bipolar",
                 reference="extern", buffer_flag="enable", clock="crystal"):
        super(MIXAd7177SG, self).__init__(axi4_bus, mvref, code_polar=code_polar,
                                          reference=reference, buffer_flag=buffer_flag, clock=clock)
        self.sample_rate_table = AD717XDef.SAMPLING_CONFIG_TABLE_AD7177
        self.resolution = 32
        self.config = {
            "ch0": {"P": "AIN0", "N": "AIN1"},
            "ch1": {"P": "AIN2", "N": "AIN3"}
        }
        self.chip_id = AD717XDef.AD7177_CHIP_ID


class MIXAd7172SG(MIXAd717xSG):
    '''
    AD7172 ADC function class

    ClassType = ADC

    Args:
        axi4_bus:    instance(AXI4LiteBus)/string/None, instance or dev path of AXI4 bus,
                                                        If None, will create Emulator.
        mvref:       float, unit mV, reference voltage.
        code_polar:  string, ['bipolar', 'unipolar'], Input channel polar/unipolar config.
        reference:   string, ['extern', 'internal'], reference voltage select.
        buffer_flag: string, ['enable', 'disable'], buffer function enable or disable.
        clock:       string, ['internal', 'output', 'external', 'crystal'], select AD7172 chip clock.

    Examples:
        ad7172 = MIXAD7172SG('/dev/MIX_AD717X_0', 2500)

    '''

    def __init__(self, axi4_bus=None, mvref=2500, code_polar="bipolar",
                 reference="extern", buffer_flag="enable", clock="crystal"):
        super(MIXAd7172SG, self).__init__(axi4_bus, mvref, code_polar=code_polar,
                                          reference=reference, buffer_flag=buffer_flag, clock=clock)
        self.sample_rate_table = AD717XDef.SAMPLING_CONFIG_TABLE_AD7172
        self.resolution = 24
        self.config = {
            "ch0": {"P": "AIN0", "N": "AIN1"},
            "ch1": {"P": "AIN2", "N": "AIN4"},
            "ch2": {"P": "AIN3", "N": "AIN4"}
        }
        self.chip_id = AD717XDef.AD7172_CHIP_ID
        self.set_setup_register("ch2", "bipolar", "extern", "enable")
