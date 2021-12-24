# -*- coding: utf-8 -*-
import time
import bisect
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.tca9538 import TCA9538
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_dmm007_sg_r import MIXDMM007SGR
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver


__author__ = 'dongdong.zhang@SmartGiant'
__version__ = 'V0.0.4'


class MoonstarDef:
    # These coefficient obtained from Moonstar Driver ERS
    VOLT_2_REAL_GAIN_5mV = 801.0
    VOLT_2_REAL_GAIN_5V = 1.0

    # current source gain
    CURRENT_2_REAL_GAIN = 21.0
    RES_GAIN_1mA = 222.2
    RES_GAIN_10mA = 20.2
    RES_GAIN_1000mA = 0.2

    VOLTAGE_5mV_RANGE = '5mV'
    VOLTAGE_5V_RANGE = '5V'

    CURRENT_1mA_RANGE = '1mA'
    CURRENT_10mA_RANGE = '10mA'
    CURRENT_1000mA_RANGE = '1000mA'

    SWITCH_DELAY_S = 0.001
    RELAY_DELAY_MS = 5
    DEFAULT_SAMPLING_RATE = 5  # Hz

    ADC_CHANNEL = 0
    ADC_VREF_VOLTAGE_5000mV = 5000
    MIXDAQT1_REG_SIZE = 0x8000
    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    CAT9538_DEV_ADDR = 0x70

    DEFAULT_TIMEOUT = 1  # s
    MAX_INPUT_VOLTAGE = 5  # V
    MAX_INPUT_CURRENT = 1  # A

    ERR_STR = 'Warning, the voltage value exceeds the range.'
    VOLTAGE_MAX_VALUE_TABLE = [0.005, 5]
    CURRENT_MAX_VALUE_TABLE = [0.001, 0.01, 1]
    VOLTAGE_RANGE_TABLE = [VOLTAGE_5mV_RANGE, VOLTAGE_5V_RANGE]
    CURRENT_RANGE_TABLE = [CURRENT_1mA_RANGE,
                           CURRENT_10mA_RANGE,
                           CURRENT_1000mA_RANGE]


moonstar_function_info = {
    MoonstarDef.VOLTAGE_5mV_RANGE: {
        'coefficient':
        1.0 / MoonstarDef.VOLT_2_REAL_GAIN_5mV,
        'bits':
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 1), (7, 0)]
    },
    MoonstarDef.VOLTAGE_5V_RANGE: {
        'coefficient':
        1.0 / MoonstarDef.VOLT_2_REAL_GAIN_5V,
        'bits':
            [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)]
    },
    MoonstarDef.CURRENT_1mA_RANGE: {
        'coefficient':
        1.0 / (MoonstarDef.CURRENT_2_REAL_GAIN * MoonstarDef.RES_GAIN_1mA),
        'bits':
            [(0, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 0), (7, 0)]
    },
    MoonstarDef.CURRENT_10mA_RANGE: {
        'coefficient':
        1.0 / (MoonstarDef.CURRENT_2_REAL_GAIN * MoonstarDef.RES_GAIN_10mA),
        'bits':
            [(0, 1), (2, 0), (3, 1), (4, 1), (5, 1), (6, 0), (7, 0)]
    },
    MoonstarDef.CURRENT_1000mA_RANGE: {
        'coefficient':
        1.0 / (MoonstarDef.CURRENT_2_REAL_GAIN * MoonstarDef.RES_GAIN_1000mA),
        'bits':
            [(0, 0), (2, 0), (3, 1), (4, 1), (5, 1), (6, 0), (7, 0)]
    }
}


moonstar_range_table = {
    '5mV': 0,
    '5V': 1,
    '1mA': 2,
    '10mA': 3,
    '1000mA': 4
}


class MoonstarException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class InvalidHardwareChannel(Exception):
    pass


class InvalidHardwareChannelType(Exception):
    pass


class InvalidRange(Exception):
    pass


class InvalidSampleCount(Exception):
    pass


class InvalidTimeout(Exception):
    pass


class MoonstarTimeout(Exception):
    pass


class MoonstarBase(SGModuleDriver):
    '''
    Base class of Moonstar and MimicCompatible.

    Providing common Moonstar methods.

    Args:
        i2c:             instance(I2C)/None,  instance of I2CBus, which is used to control tca9538, eeprom and nct75.
        ipcore:          instance(MIXDMM007SGR)/string/None, instance of MIXDMM007SGR, which is used to control AD7175.
        range_table:     dict, which is ICI calibration range table.

    '''

    rpc_public_api = ['configure_channel', 'get_channel_configuration', 'set_sampling_rate',
                      'get_sampling_rate', 'read', 'enable_continuous_sampling',
                      'disable_continuous_sampling'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, ipcore, range_table=moonstar_range_table, function_info=moonstar_function_info):

        self.tca9538 = TCA9538(MoonstarDef.CAT9538_DEV_ADDR, i2c)
        self.eeprom = CAT24C32(MoonstarDef.EEPROM_DEV_ADDR, i2c)
        self.sensor = NCT75(MoonstarDef.SENSOR_DEV_ADDR, i2c)

        if isinstance(ipcore, basestring):
            daqt1_axi4_bus = AXI4LiteBus(ipcore, MoonstarDef.MIXDAQT1_REG_SIZE)
            ipcore = MIXDMM007SGR(axi4_bus=daqt1_axi4_bus, ad717x_chip='AD7175',
                                  ad717x_mvref=MoonstarDef.ADC_VREF_VOLTAGE_5000mV,
                                  use_spi=False, use_gpio=False)

        self.ipcore = ipcore
        self.ad7175 = self.ipcore.ad717x

        self.ad7175.config = {
            'ch0': {'P': 'AIN0', 'N': 'AIN1'}
        }
        super(MoonstarBase, self).__init__(self.eeprom, self.sensor, range_table=range_table)
        self.config = {}
        self.function_info = function_info
        self.protect = False

    def post_power_on_init(self, timeout=MoonstarDef.DEFAULT_TIMEOUT):
        '''
        Init Moonstar module to a know harware state.

        This is to handle the case when gpio pin used for sample-rate
        is behind an I2C mux, and when module instance is created the
        I2C mux is not configured so i2c to module is not working.
        User software need to switch i2c mux if there is, and call this function once
        Before using the module.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=MoonstarDef.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                self.tca9538.set_ports([0x00])
                self.tca9538.set_pins_dir([0x00])
                self.ad7175.channel_init()
                self.configure_channel(1, 'voltage', 5)
                self.set_sampling_rate(MoonstarDef.DEFAULT_SAMPLING_RATE)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise MoonstarException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get Moonstar driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def configure_channel(self, channel, type, max_expected_value):
        '''
        Configures the specified channel to the input type and range provided.

        Args:
            channel:    int, the numeric id of the channel. 1 or greater depending on capabilities.
                             For this module, channel can only be one
            type:       string, ['voltage', 'current'], the type of measurement.
                                Valid Values: "voltage", or "current"
            max_expected_value: float, the absolute maximum value you expect to read from the specified channel.
                                       The device driver will set the appropriate range based on this value.
                                       Valid maximums are: voltage 5mV, 5V current 1mA, 10mA, 1000mA

        Returns:
            dict, the actual channel configuration as a dictionary: {"channel": 1, "type": "voltage", "range": 5.0}.

        Examples:
            print(module.configure_channel(1, 'voltage', 5))
            {"channel": 1, "type": "voltage", "range": 5.0}

        Exception:
            InvalidHardwareChannel() if provided channel is out of range
            InvalidHardwareChannelType() if provided type is not supported
            InvalidRange() if the provided max expected value is outside of the supported ranges.

        '''
        current_channel = self.config.get('channel', None)
        current_type = self.config.get('type', None)
        current_range = self.config.get('range', None)

        if channel != 1:
            raise InvalidHardwareChannel('channel must be 1')

        if type not in ['voltage', 'current']:
            raise InvalidHardwareChannelType('type should be "voltage" or "current"')

        if type == 'voltage':
            if max_expected_value > MoonstarDef.MAX_INPUT_VOLTAGE:
                raise InvalidRange('max_excepted_value should not over 5 V')
            index = bisect.bisect_left(MoonstarDef.VOLTAGE_MAX_VALUE_TABLE, max_expected_value)
            if index >= len(MoonstarDef.VOLTAGE_MAX_VALUE_TABLE):
                index = len(MoonstarDef.VOLTAGE_MAX_VALUE_TABLE) - 1
            range_value = MoonstarDef.VOLTAGE_MAX_VALUE_TABLE[index]
            measure_range = MoonstarDef.VOLTAGE_RANGE_TABLE[index]
        elif type == 'current':
            if max_expected_value > MoonstarDef.MAX_INPUT_CURRENT:
                raise InvalidRange('max_expected_value should not over 1 A')
            index = bisect.bisect_left(MoonstarDef.CURRENT_MAX_VALUE_TABLE, max_expected_value)
            if index >= len(MoonstarDef.CURRENT_MAX_VALUE_TABLE):
                index = len(MoonstarDef.CURRENT_MAX_VALUE_TABLE) - 1
            range_value = MoonstarDef.CURRENT_MAX_VALUE_TABLE[index]
            measure_range = MoonstarDef.CURRENT_RANGE_TABLE[index]

        if (current_channel == channel and current_type == type and
                current_range == range_value and self.protect is False):
            return self.config

        if type == 'current':
            self.tca9538.set_pin(1, 0)
            time.sleep(MoonstarDef.SWITCH_DELAY_S)

        bits = self.function_info[measure_range]['bits']
        for bit in bits:
            self.tca9538.set_pin(bit[0], bit[1])

        if type == 'current':
            time.sleep(MoonstarDef.SWITCH_DELAY_S)
            self.tca9538.set_pin(1, 1)

        time.sleep(MoonstarDef.RELAY_DELAY_MS / 1000.0)

        self.config = {
            "channel": channel,
            "type": type,
            "range": range_value
        }
        self.protect = False
        return self.config

    def get_channel_configuration(self, channel):
        '''
        Returns the configuration of specified channel.

        Args:
            channel:    int, the desired channel. channel must be 1.

        Returns:
            dict, the channel configurationas dictionary:  {"channel": 1, "type": "voltage", "range": 5.0}.

        Examples:
            print(module.get_channel_configuration(1))

        Exception:
            InvalidHardwareChannel() if provided channel is not supported
        '''
        if channel != 1:
            raise InvalidHardwareChannel('channel must be 1')
        return self.config

    def set_sampling_rate(self, sampling_rate):
        '''
        Moonstar set sampling rate. This is private function.

        Args:
            sampling_rate:     float, [5~250000], adc measure sampling rate, which not continuouse,
                                                  please refer ad7175 datasheet.

        Returns:
            string, "done", api execution successful.

        Examples:
           moonstar.set_sampling_rate(10000)

        '''
        assert 5 <= sampling_rate <= 250000

        if sampling_rate != self.get_sampling_rate():
            self.ad7175.set_sampling_rate(MoonstarDef.ADC_CHANNEL, sampling_rate)

        return "done"

    def get_sampling_rate(self):
        '''
        Moonstar get sampling rate of adc.

        Returns:
            string, "done", api execution successful.

        Examples:
            sampling_rate = moonstar.get_sampling_rate()
            print(sampling_rate)

        '''

        return self.ad7175.get_sampling_rate(MoonstarDef.ADC_CHANNEL)

    def _volt_to_target_unit(self, scope, volt):
        '''
        Moonstar get target unit value (mimic_function_info) from measured voltage

        Args:
            scope:      string, ['5mV', '5V', '1mA', '10mA', '1000mA'], AD7175 measurement range.
            volt:       float, the measured voltage by ad7175.

        Returns:
            float, value.

        '''
        assert scope in self.function_info

        return volt * self.function_info[scope]['coefficient']

    def read(self, channels, samples_per_channel=1, timeout=10.0):
        '''
        Performs an on-demand read.

        Reads the specified number of samples from each channel.
        Values read are in standard SI units (Volts and Amps).

        Args:
            channels:   list, the desired channel(s) to read
            samples_per_channel: int, default 1, the number of samples to read from each channel.
            timeout:    float, default 10.0, the maximum duration the acquisition can take, in seconds,
                        before returning an exception.

        Returns:
            int/list, the return is dynamic based on the 'channels' and 'samples_per_channel' specified.
            If len(channels) is 1 and samples_per_channel is 1,
            returns a float representing the single value read from the channel.
            If len(channels) is 1 and samples_per_channel is >1,
            returns a list of floats representing the multiple values read from the channel.
            If len(channels) is >1 and samples_per_channel is 1,
            returns a list of floats representing the single value read from the multiple channels.
            If len(channels) is >1 and samples_per_channel is >1,
            returns a list of lists of floats representing the multiple values read from the multiple channels

        Examples:
            # read channel 1, default 1 sample & 10s timeout
            print(module.read([1]))
            1.234
        '''
        if not isinstance(channels, list):
            raise InvalidHardwareChannel('Channel "{}" is not supported!'.format(channels))
        for channel in channels:
            if channel != 1:
                raise InvalidHardwareChannel('Channel "{}" is not supported!'.format(channel))
        if not isinstance(samples_per_channel, int) or samples_per_channel < 1:
            raise InvalidSampleCount('samples_per_channel should be integer and larger than 0')
        if timeout < 0:
            raise InvalidTimeout('timeout should not be negative')

        range_value = self.config['range']
        measure_type = self.config['type']
        if measure_type == 'current':
            index = MoonstarDef.CURRENT_MAX_VALUE_TABLE.index(range_value)
            measure_range = MoonstarDef.CURRENT_RANGE_TABLE[index]
        elif measure_type == 'voltage':
            index = MoonstarDef.VOLTAGE_MAX_VALUE_TABLE.index(range_value)
            measure_range = MoonstarDef.VOLTAGE_RANGE_TABLE[index]

        chan_value_table = []
        start_time = time.time()
        for channel in channels:
            value_table = []
            for i in range(samples_per_channel):
                current_time = time.time()
                if current_time - start_time > timeout:
                    raise MoonstarTimeout('Sampling data timeout')
                try:
                    if self.protect:
                        value_table.append(9999999)
                    else:
                        volt = self.ad7175.read_volt(MoonstarDef.ADC_CHANNEL)
                        value = self._volt_to_target_unit(measure_range, volt)
                        # Note that: calibration unit is mV and mA
                        value = self.calibrate(measure_range, value)
                        value_table.append(value / 1000.0)
                except Exception as ex:
                    if str(ex) == MoonstarDef.ERR_STR:
                        self.tca9538.set_pin(1, 0)
                        value_table.append(9999999)
                        self.protect = True
                    else:
                        raise ex
            chan_value_table.append(value_table)
        if len(channels) == 1 and samples_per_channel == 1:
            return chan_value_table[0][0]
        elif len(channels) == 1 and samples_per_channel > 1:
            return chan_value_table[0]
        elif len(channels) > 1 and samples_per_channel == 1:
            return_value = []
            for i in range(len(chan_value_table)):
                return_value.append(chan_value_table[i][0])
            return return_value
        elif len(channels) > 1 and samples_per_channel > 1:
            return chan_value_table

    def enable_continuous_sampling(
            self,
            channel=1,
            sample_rate=1000,
            down_sample=1,
            selection='max'):
        '''
        This function enables continuous sampling and data throughput upload to upper stream.

        Down sampling is supported. For example, when down_sample =5, selection=max,
        select the maximal value from every 5 samples, so the actual data rate is reduced by 5.
        The output data inflow is calibrated if calibration mode is `cal`
        During continuous sampling, the setting functions, like set_calibration_mode(),
        set_measure_path(), cannot be called.

        Args:
            channel:        int,   the numeric id of the channel. 1 or greater depending on capabilities.
            sample_rate:    float, [5~250000], unit Hz, default 1000, set sampling rate of data acquisition in SPS.
                                               please refer to AD7175 data sheet for more.
            down_sample:    int, (>0), default 1, down sample rate for decimation.
            selection:      string, ['max', 'min'], default 'max'. This parameter takes effect as long as down_sample is
                                    higher than 1. Default 'max'

        Returns:
            Str, 'done'
        '''

        self.ad7175.disable_continuous_sampling(MoonstarDef.ADC_CHANNEL)
        time.sleep(MoonstarDef.SWITCH_DELAY_S)
        self.ad7175.enable_continuous_sampling(MoonstarDef.ADC_CHANNEL, sample_rate,
                                               down_sample, selection)

        self.continuous_sample_mode = channel

        return "done"

    def disable_continuous_sampling(self):
        '''
        This function disables continuous sampling and data throughput upload to upper stream.

        This function can only be called in continuous mode, a.k.a, after continuous_sampling_enable()
            function is called.

        Returns:
            Str: 'done'
        '''

        self.ad7175.disable_continuous_sampling(MoonstarDef.ADC_CHANNEL)

        self.continuous_sample_mode = None

        return "done"


class DMM007001(MoonstarBase):
    '''
    This driver is used for DMM007001 and DMM007002 board cards.

    compatible = ["GQQ-1085-5-010", "GQQ-1085-5-020"]

    Args:
        i2c:        instance(I2C),  instance of I2CBus, which is used to control tca9538, eeprom and nct75.
        ipcore:     instance(MIXDMM007SGR)/string,  instance of MIXDMM007SGR, which is used to control AD7175.

    Examples:
        vref = 5000
        i2c_bus = I2C('/dev/i2c-0')
        ip = MIXDMM007SGR('/dev/AXI4_DMM007_SG_R_0', ad717x_mvref=vref, use_spi=False, use_gpio=False)
        dmm007 = DMM007001(i2c_bus, ip)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-1085-5-010", "GQQ-1085-5-020"]

    def __init__(self, i2c, ipcore):
        super(DMM007001, self).__init__(i2c, ipcore)
