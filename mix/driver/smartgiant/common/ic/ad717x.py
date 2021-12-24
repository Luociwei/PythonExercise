import time
from mix.driver.smartgiant.common.utility.data_operate import DataOperate
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.1'


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
    FILTER0_REG_ADDR = 0x28
    FILTER1_REG_ADDR = 0x29
    FILTER2_REG_ADDR = 0x2A
    FILTER3_REG_ADDR = 0x2B

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

    REGISTOR_LEN = {0x00: 1, 0x01: 2,
                    0x02: 2, 0x06: 2,
                    0x07: 2, 0x10: 2,
                    0x11: 2, 0x12: 2,
                    0x13: 2, 0x20: 2,
                    0x21: 2, 0x22: 2,
                    0x23: 2, 0x28: 2,
                    0x29: 2, 0x2a: 2,
                    0x2b: 2, 0x03: 3,
                    0x04: 3, 0x30: 3,
                    0x31: 3, 0x32: 3,
                    0x33: 3, 0x38: 3,
                    0x39: 3, 0x3A: 3,
                    0x3B: 3}


class AD717XException(Exception):
    '''
    AD717XException shows the exception of AD717X
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


class AD717X(object):
    '''
    AD717X ADC function class. This is a base class of AD717X.

    :param spi:       instance,    if not given, spi emulator will be created.
    :param mvref:     float        reference voltage, unit is mV

    .. code-block:: python

               ft4222 = FT4222('4593')
               ft_spi = FTSPI(ft4222)
               ad717x = AD717X(ft_spi, 2500)

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

    '''

    def __init__(self, spi=None, mvref=2500, code_polar="bipolar",
                 reference="extern", buffer_flag="enable", clock="crystal"):
        self.spi = spi if spi is not None else MIXQSPISGEmulator('ad717x_spi_emulator', 64)
        self.mvref = mvref
        self.clock = AD717XDef.CLOCKSEL[clock]
        self.sample_rate_table = AD717XDef.SAMPLING_CONFIG_TABLE_AD7175

        self.resolution = 24

        self.channel_dict = {"ch0": 0, "ch1": 1, "ch2": 2, "ch3": 3}

        self.config = {
            "ch0": {"P": "AIN0", "N": "AIN1"},
            "ch1": {"P": "AIN2", "N": "AIN3"}
        }

        self.chip_id = AD717XDef.AD7175_CHIP_ID
        self.sampling_rates = {}
        self.code_polar = code_polar
        self.reference = reference
        self.buffer_flag = buffer_flag

    def channel_init(self):
        for channel in self.config:
            self.set_setup_register(channel, self.code_polar, self.reference, self.buffer_flag)

    def reset(self, register_state=None):
        '''
        AD717X reset chip

        :param register_state: dict/None the register state when reset,
                                             eg:{0x10:0x8001, 0x11:0x9043}
                                             None: all registers keep
                                             default state.
        :example:
                   ad717x.reset()
        '''
        # assert not register_state or isinstance(register_state, dict)
        filter_list = [x for x in [0x00, 0x03, 0x04] if register_state is not None and x in register_state]
        if register_state is not None and filter_list:
            raise AD717XException(
                "0x%2x is a read-only register, not allowed to write!"
                % (filter_list[0]))

        # At least 64 serial clock cycles need which can be found in datasheet
        wr_data = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        self.spi.write(wr_data)

        if register_state:
            for reg_addr, reg_data in register_state.items():
                self.write_register(reg_addr, reg_data)

    def read_register(self, reg_addr):
        '''
        AD717X read the register value

        :param reg_addr:    hex(0x00~0x3F)
        :returns:           int
        :raises keyError:   raises an AD717XException
        :example:
                            print(ad717x.read_register(0x00))
        '''
        assert isinstance(reg_addr, int)
        assert reg_addr in AD717XDef.REGISTOR_LEN

        # set ad717x comms register to read the other register
        # which register address is reg_addr
        com_data = (0x3F & reg_addr) | (0x1 << 6)
        reg_len = AD717XDef.REGISTOR_LEN[reg_addr & 0x3f]
        wr_data = [com_data]

        if reg_addr == 0x04 and self.resolution == 32:
            reg_len = 4

        data = self.spi.transfer(wr_data, reg_len, False)
        rd_data = 0
        for i in range(reg_len):
            rd_data = rd_data << 8
            rd_data |= data[i]

        return rd_data

    def write_register(self, reg_addr, reg_data):
        '''
        AD717X write the register value

        :param reg_addr:    hex(0x00~0x3F)
        :param reg_data:    int
        :raises keyError:   raises an AD717XException
        :example:
                            ad717x.write_register(0x10, 30)
        '''
        assert isinstance(reg_addr, int) and isinstance(reg_data, int)
        assert reg_addr in AD717XDef.REGISTOR_LEN
        if reg_addr in [0x00, 0x03, 0x04]:
            raise AD717XException("The register address is read only!")

        com_data = [(0x3F & reg_addr)]
        reg_len = AD717XDef.REGISTOR_LEN[reg_addr & 0x3f]
        data = DataOperate.int_2_list(reg_data, reg_len)
        data.reverse()
        wr_data = com_data + data

        self.spi.write(wr_data)

    def _value_2_mvolt(self, code, mvref, bits, gain=0x555555, offset=0x800000):
        '''
        translate the value to voltage value

        :param code:    int
        :param mvref:   float       unit is mV
        :param bits:    bits(16,24,32)
        :param gain:    int gain register value, nominal value 0x555555
        :param offset:  int offset register value, default value 0x800000
        :returns:       float    unit is mV
        '''

        tmp = float(code - (1 << bits - 1)) * 0x400000 / gain
        volt = float(tmp + (offset - 0x800000)) / (1 << bits - 1) * mvref / 0.75
        return volt

    def set_setup_register(self, channel, code_polar="bipolar", reference="extern", buffer_flag="enable"):
        '''
        AD717x setup register set, code polar,refrence, buffer

        :param channel:    string("ch0"/"ch1"/"ch2"/"ch3"),            The channel to config setup_register
        :param code_polar: string("unipolar"/"bipolar"),               "unipolar" for unipolar input,
                                                                       "bipolar" for bipolar input
        :param reference:  string("extern"/"internal"/"AVDD-AVSS"),    Select voltage reference
        :param buffer:     string("enable"/"disable"),                 Enable or disable input buffer
        :example:
                ad717x.set_setup_register("ch0", "bipolar", "extern", "enable")
        '''

        value = 0x0
        value |= AD717XDef.POLARS[code_polar] << 12 | AD717XDef.BUFFERS[buffer_flag] << 8 |\
            AD717XDef.REFERENCES[reference] << 4

        return self.write_register(AD717XDef.SETUP_REG_ADDR[channel], value)

    def set_sampling_rate(self, channel, rate):
        '''
        AD717X set sample rate of channel

        :param channel: str("ch0"~"ch3")/int(0-3)
        :param rate:    int
        :example:
                   ad717x.set_sampling_rate("ch0", 3000)
        '''
        assert channel in ["ch" + str(i) for i in range(4)] or channel in [i for i in range(4)]

        channel = CHAN(channel)
        filter_reg = (eval("AD717XDef.FILTER" + channel[-1] + "_REG_ADDR"))
        value = self.read_register(filter_reg)

        if rate not in self.sample_rate_table:
            raise AD717XException("Sample rate is out of range of AD717X capable.")

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
        AD717X get sample rate

        :param channel:    str("ch0"~"ch3")/int(0-3)
        :returns:  int         unit is sps
        :example:
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
            raise AD717XException("Register value invalid:0x%x" % (data))

        return result

    def set_channel_state(self, channel, state):
        '''
        AD717X set_channel_state

        :param channel:         str("ch0"~"ch3")/int(0-3)
        :param state:           str("enable", "disable")
        :example:
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
        AD717X select_single_channel

        :param channel:         str("ch0","ch1","ch2","ch3")/int(0-3)
        :example:
                   ad717x.select_single_channel("ch0")
        '''
        assert channel in AD717XDef.CHANNELS

        channel = CHAN(channel)
        # close all channeal
        for chan in self.config:
            self.set_channel_state(chan, "disable")

        # open one channel
        self.set_channel_state(channel, "enable")

    def read_volt(self, channel, timeout_sec=AD717XDef.DEFAULT_TIMEOUT):
        '''
        AD717X read voltage at single conversion mode

        :param channel:    str("ch0", "ch1", "ch2", "ch3")/int(0-3)
        :returns:           int         unit is mV
        :raises keyError:   raises an AD717XException
        :example:
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
            raise AD717XException(
                "Set ad717x to continuous conversion mode fail!")

        wr_data = rd_data & 0xFF0F | 0x0010
        wr_data &= ~AD717XDef.CLOCKSEL_MASK
        wr_data |= self.clock
        self.write_register(AD717XDef.ADC_MODE_REG_ADDR, wr_data)

        start_time = time.time()

        while True:
            reg_data = self.read_register(AD717XDef.STATUS_REG_ADDR)
            # check if convertion is ready
            if reg_data & (1 << 7) == 0:
                break
            if time.time() - start_time > timeout_sec:
                raise AD717XException('Wait convertion ready timeout')

        reg_data = self.read_register(AD717XDef.DATA_REG_ADDR)

        volt = self._value_2_mvolt(reg_data, self.mvref, self.resolution)
        return volt

    def is_communication_ok(self):
        '''
        AD717X read the id of AD717X and then confirm
        whether the communication of SPI bus is OK

        :returns:           bool
        :raises keyError:   raises an AD717XException
        :example:
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
            raise AD717XException(
                "An error occurred when communicating with AD717X fail.")
        return False

    def config_max_value_measure(self, channel, samples):
        '''
        AD717X config max value measure

        :param state:       string('enable'/'disable'), enable or disable max value  measure
        :param samples:     int(5-100), get max value in every samples data.
        '''
        raise NotImplementedError("Not support funtion")

    def enable_continuous_sampling(self, channel, rate, samples=1):
        '''
        AD717X enable continuous sampling

        :param channel:     str("ch0", "ch1", "ch2", "ch3")/int(0-3)
        :param rate:        int
        :param samples: int(0|5-100), 0 means not enable max sample function.
        :example:
                   ad717x.enable_continuous_sampling("ch0", 1000)
        '''

        raise NotImplementedError("Not support funtion")

    def disable_continuous_sampling(self, channel):
        '''
        AD717X disable continuous sampling

        :param channel:     str("ch0", "ch1")/int(0-1)
        :example:
                   ad717x.disable_continuous_sampling('ch0')
        '''
        raise NotImplementedError("Not support funtion")

    def get_continuous_sampling_voltage(self, channel, count):
        '''
        AD717X get continuous sampling voltage

        :param channel:    str("ch0", "ch1", "ch2", "ch3")/int(0-3)
        :param count:      int(1-512), how many data to get
        :returns:          list,        the unit of elements in the list is mV
        :raises keyError:  raises an AD717XException
        :example:
                            print(ad717x.get_voltage_at_continuous_sampling_mode("ch0", 30))
        '''

        raise NotImplementedError("Not support funtion")


class AD7175(AD717X):
    '''
    AD7175 ADC function class

    :param spi:       instance,    if not given, spi emulator will be created.
    :param mvref:     float        reference voltage, unit is mV
    :example:
               ft_spi = FTSPI(adapter_id='4129', ioLine='SPI', ssoMap='SS0O')
               ad7175 = AD7175(ft_spi, 5000)
    '''

    def __init__(self, spi=None, mvref=5000, code_polar="bipolar",
                 reference="extern", buffer_flag="enable", clock="crystal"):
        super(AD7175, self).__init__(spi, mvref, code_polar="bipolar",
                                     reference="extern", buffer_flag="enable", clock="crystal")
        self.sample_rate_table = AD717XDef.SAMPLING_CONFIG_TABLE_AD7175
        self.resolution = 24
        self.config = {
            "ch0": {"P": "AIN1", "N": "AIN0"},
            "ch1": {"P": "AIN2", "N": "AIN3"}
        }
        self.chip_id = AD717XDef.AD7175_CHIP_ID


class AD7177(AD717X):
    '''
    AD7177 ADC function class

    :param spi:       instance,    if not given, spi emulator will be created.
    :param mvref:     float        reference voltage, unit is mV
    :example:
               ft_spi = FTSPI(adapter_id='4129', ioLine='SPI', ssoMap='SS0O')
               ad7177 = AD7177(ft_spi, 2500)
    '''

    def __init__(self, spi=None, mvref=2500, code_polar="bipolar",
                 reference="extern", buffer_flag="enable", clock="crystal"):
        super(AD7177, self).__init__(spi, mvref, code_polar="bipolar",
                                     reference="extern", buffer_flag="enable", clock="crystal")
        self.sample_rate_table = AD717XDef.SAMPLING_CONFIG_TABLE_AD7177
        self.resolution = 32
        self.config = {
            "ch0": {"P": "AIN0", "N": "AIN1"},
            "ch1": {"P": "AIN2", "N": "AIN3"}
        }
        self.chip_id = AD717XDef.AD7177_CHIP_ID
