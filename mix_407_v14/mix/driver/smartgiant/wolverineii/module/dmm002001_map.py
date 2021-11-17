# -*- coding: utf-8 -*-
import functools
import math
import time
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.ic.pca9536 import PCA9536
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.bus.pin import Pin
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR

__author__ = 'zicheng.huang@SmartGiant' + 'weiping.mo@gzseeing.com'
__version__ = '0.2.2'


class WolverineiiCoeffDef:
    # These coefficient obtained from WolverineII Driver ERS
    VOLT_2_REAL_GAIN1 = 1.0
    VOLT_2_REAL_GAIN2 = 199.393

    RES_LOAD_210ohm = 210.0
    RES_LOAD_10ohm = 10.0

    CAL_DATA_LEN = 13
    WRITE_CAL_DATA_PACK_FORMAT = '2f5B'
    WRITE_CAL_DATA_UNPACK_FORMAT = '13B'

    READ_CAL_BYTE = 13
    READ_CAL_DATA_PACK_FORMAT = '13B'
    READ_CAL_DATA_UNPACK_FORMAT = '2f5B'


wolverineii_function_info = {
    # bits output state definition can be found from 'WolverineII Driver ERS'
    '5V': {
        'coefficient': 1.0 / (WolverineiiCoeffDef.VOLT_2_REAL_GAIN1),
        'unit': 'mV',
        'bits': [(0, 0), (1, 0)],
        'channel': 'A',
        'suffix': 'v1'
    },
    '5VCH2': {
        'coefficient': 1.0 / (WolverineiiCoeffDef.VOLT_2_REAL_GAIN1),
        'unit': 'mV',
        'bits': [(0, 0), (1, 0)],
        'channel': 'B',
        'suffix': 'v2'
    },
    '100uA': {
        'coefficient':
        1.0 / (WolverineiiCoeffDef.RES_LOAD_210ohm * \
               WolverineiiCoeffDef.VOLT_2_REAL_GAIN2),
        'unit':
        'mA',
        'bits': [(0, 1), (1, 1)],
        'channel': 'B',
        'suffix': 'i'
    },
    '2mA': {
        'coefficient':
        1.0 / (WolverineiiCoeffDef.RES_LOAD_10ohm * \
               WolverineiiCoeffDef.VOLT_2_REAL_GAIN2),
        'unit':
        'mA',
        'bits': [(0, 0), (1, 1)],
        'channel': 'B',
        'suffix': 'i'
    }
}


wolverineii_range_table = {
    "5V": 0,
    "5VCH2": 1,
    "5V_AVG": 2,
    "5VCH2_AVG": 3,
    "5V_RMS": 4,
    "5VCH2_RMS": 5,
    "100uA": 6,
    "2mA": 7
}


class WolverineiiDef:

    ADC_A_CHANNEL = 'A'
    ADC_B_CHANNEL = 'B'

    DCV_5V_RANGE = "5V"
    DCV_5VCH2_RANGE = "5VCH2"

    DCI_2mA_RANGE = "2mA"
    DCI_100uA_RANGE = "100uA"
    CURRENT_RANGE_LIST = (DCI_2mA_RANGE, DCI_100uA_RANGE)
    SWITCH_DELAY_S = 0.001
    RELAY_DELAY_S = 0.005
    DEFAULT_SAMPLE_RATE = 1000
    SELECT_RANGE_KEY = 'range'
    UPLOAD_TIME = 1
    DEFAULT_RANGE = '5V'

    AD7175_MVREF = 5000
    AD7175_CODE_POLAR = 'bipolar'
    AD7175_REFERENCE = 'extern'
    AD7175_CLOCK = 'crystal'
    MIXDAQT1_REG_SIZE = 65536
    EMULATOR_REG_SIZE = 256
    ADC_CHANNEL_A = 0
    ADC_CHANNEL_B = 1
    ADC_CHANNEL_LIST = {'A': ADC_CHANNEL_A, 'B': ADC_CHANNEL_B}
    ADC_SINC_SEL = ["sinc5_sinc1", "sinc3"]

    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    IO_EXP_DEV_ADDR = 0x41
    TIME_OUT = 1.0

    DEFAULT_COUNT = 1
    DEFAULT_DOWN_SAMPLE = 1
    DEFAULT_SELECTION = 'max'

    TAG_BASE_PIN = 4
    GPIO_OUTPUT_DIR = "output"
    ADC_ERROR_BIT = (1 << 6)
    STATUS_REG_ADDR = 0x00
    DATA_REG_ADDR = 0x04
    VOLT_RANGE = 5.0  # V
    CURR_RANGE_2mA = 0.00250761  # A
    CURR_RANGE_100uA = 0.00011941  # A


class WolverineiiException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class WolverineII(SGModuleDriver):
    '''
    WolverineII is a compact version of the digital multimeter which internal ADC resolution is 24 bit.

    It can be used as high performance DMM to measure DC voltage and small signal DC current. In this class,
    adc channel 0 is Voltage channel, adc channel 1 is current and voltage channel. WolverineII support
    signal measurement and continuous measurement. Note that if pca9536 io control range. Note that
    calibration default is enabled.

    Args:
        i2c:     instance(I2C)/None, which is used to control nct75, cat24c32 and pca9536. If not given,
                                     emulator will be created.
        ip:      instance(MIXDAQT1)/None, MIXDAQT1 ip driver instance, if given, user should not use ad7175.

    Examples:
        Example for using aggregate IP:
            i2c = I2C('/dev/i2c-1')
            daqt1 = MIXDAQT1('/dev/MIX_DAQT1', ad717x_chip='AD7175', ad717x_mvref=5000, use_spi=False, use_gpio=True)
            wolverineii = WolverineII(i2c, ip=daqt1)

        Example for current/voltage measuring:
            dmm.disable_continuous_sampling()
            wolverineii.set_measure_path('5V')
            result = wolverineii.read_measure_value()
            print("voltage={}, unit is mV".format(result))
            result = wolverineii.read_measure_list(count=5)
            print("voltage_list={}, unit is mV".format(result))

            wolverineii.set_measure_path('2mA')
            result = wolverineii.read_measure_value()
            print("voltage={}, unit is mA".format(result))
            result = wolverineii.read_measure_list(count=5)
            print("voltage_list={}, unit is mA".format(result))

        Example for continuous measuring:
            wolverineii.set_measure_path('5V')
            dmm.enable_continuous_sampling('5VBOTH')
            result = read_continuous_sampling_statistics(256)

            print("5V Result: average={}, max={}, min={}, rms={}".format(result['avg_v1'],
            result['max_v1'], result['min_v1'], result['rms_v1']))

            print("5VCH2 Result: average={}, max={}, min={}, rms={}".format(result['avg_v2'],
            result['max_v2'], result['min_v2'], result['rms_v2']))

            wolverineii.set_measure_path('2mA')
            dmm.enable_continuous_sampling('2mA')
            result = read_continuous_sampling_statistics(256)

            print("2mA Result: average={}, max={}, min={}, rms={}".format(result['avg_i'],
            result['max_i'], result['min_i'], result['rms_i']))

    '''

    compatible = ['GQQ-Q178-5-01A', 'GQQ-Q178-5-010']

    rpc_public_api = [
        'set_sinc', 'get_sampling_rate', 'set_measure_path', 'get_measure_path',
        'read_measure_value', 'read_measure_list',
        'enable_continuous_sampling',
        'disable_continuous_sampling',
        'read_continuous_sampling_statistics', 'datalogger_start',
        'datalogger_end'
    ] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, ipcore):

        self.eeprom = CAT24C32(WolverineiiDef.EEPROM_DEV_ADDR, i2c)
        self.sensor = NCT75(WolverineiiDef.SENSOR_DEV_ADDR, i2c)
        self.pca9536 = PCA9536(WolverineiiDef.IO_EXP_DEV_ADDR, i2c)

        if isinstance(ipcore, basestring):
            axi4_bus = AXI4LiteBus(ipcore, WolverineiiDef.MIXDAQT1_REG_SIZE)
            ipcore = MIXDAQT1SGR(axi4_bus,
                                 'AD7175',
                                 ad717x_mvref=WolverineiiDef.AD7175_MVREF,
                                 code_polar=WolverineiiDef.AD7175_CODE_POLAR,
                                 reference=WolverineiiDef.AD7175_REFERENCE,
                                 clock=WolverineiiDef.AD7175_CLOCK,
                                 use_gpio=True)

        self.ipcore = ipcore
        self.ad7175 = self.ipcore.ad717x
        self.ad7175.config = {
            'ch0': {
                'P': 'AIN0',
                'N': 'AIN1'
            },
            'ch1': {
                'P': 'AIN2',
                'N': 'AIN3'
            }
        }

        self.measure_path = dict()

        self.continuous_sample_mode = None

        self.gpio = ipcore.gpio
        self.tag_pins = [
            Pin(self.gpio, WolverineiiDef.TAG_BASE_PIN + x,
                WolverineiiDef.GPIO_OUTPUT_DIR) for x in range(4)
        ]

        super(WolverineII, self).__init__(self.eeprom,
                                          self.sensor,
                                          range_table=wolverineii_range_table)

    def post_power_on_init(self, timeout=WolverineiiDef.TIME_OUT):
        '''
        Init WolverineII module to a know harware state.

        This function will set pca9536 io direction to output and set default range to '5V'.
        This function will be called by launcher. User should not call this function.

        Args:
            timeout:      float, (>=0), unit Second, default 1.0, execute timeout

        '''
        self.reset(timeout)

    def pre_power_down(self, timeout=WolverineiiDef.TIME_OUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set pca9536 io direction to output and set pin level to 0.
        This function will be called by launcher. User should not call this function.

        Args:
            timeout:      float, (>=0), unit Second, default 1.0, execute timeout

        '''
        start_time = time.time()
        while True:
            try:
                self.pca9536.set_pins_dir([0x00])
                self.pca9536.set_ports([0x00])
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise WolverineiiException("Timeout: {}".format(e.message))

    def reset(self, timeout=WolverineiiDef.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), unit Second, default 1.0, execute timeout.

        '''

        start_time = time.time()
        while True:
            try:
                self.pca9536.set_pins_dir([0x00])
                self.pca9536.set_ports([0x00])
                self.ad7175.reset()
                time.sleep(0.01)
                self.ad7175.channel_init()
                self.ad7175.set_sampling_rate(WolverineiiDef.ADC_CHANNEL_A,
                                              WolverineiiDef.DEFAULT_SAMPLE_RATE)
                self.ad7175.set_sampling_rate(WolverineiiDef.ADC_CHANNEL_B,
                                              WolverineiiDef.DEFAULT_SAMPLE_RATE)
                self.set_measure_path(WolverineiiDef.DEFAULT_RANGE)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise WolverineiiException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get wolverine II driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def write_module_calibration(self, channel, calibration_vectors):
        '''
        Calculate module calibration and write to eeprom.

        Xavier timestamp must be synced with host first before call this function.
        All channels must be calibrated in one day.

        Args:
            channel:        string, ['5V', '5VCH2', '100uA', '2mA'], voltage or current channel
            calibration_vectors: list, [[raw1, benchmark1], ...,[rawN, ...,benchmarkN]], it contains value
                                 pairs of module reading and benchmark
                                 value got from external equipemnets. [[module_raw1,benchmark1],
                                 [module_raw1,benchmark1],
                                 ...
                                 [module_rawN,benchmarkN]]

        Returns:
            string, 'done', execute successful.

        '''
        assert channel in ['5V', '5VCH2', '100uA', '2mA']
        return super(WolverineII, self).write_module_calibration(channel, calibration_vectors)

    def set_sinc(self, channel, sinc):
        '''
        wolverineii set digtal filter.

        Args:
            channel:    string, ['100uA', '2mA', '5V', '5VCH2'], set range for different channel.
            sinc:       string, ["sinc5_sinc1", "sinc3"]

        Example:
            wolverineii.set_sinc("100uA", "sinc5_sinc1")

        '''
        assert channel in wolverineii_function_info.keys()
        assert sinc in WolverineiiDef.ADC_SINC_SEL

        adc_channel = wolverineii_function_info[channel]['channel']
        self.ad7175.set_sinc(WolverineiiDef.ADC_CHANNEL_LIST[adc_channel], sinc)

    def set_sampling_rate(self, sampling_rate):
        '''
        WolverineII set sampling rate.

        Note that sampling rate is not discontinuous, all support sampling
        rate can be found in ad7175 datasheet. This is private function.

        Args:
            sampling_rate:      float, [5~250000], adc measure sampling rate, which is not continuous,
                                                   please refer to ad7175 datasheet.

        Returns:
            string, "done", api execution successful.

        '''
        channel = self.measure_path['range']
        adc_channel = wolverineii_function_info[channel]['channel']

        if sampling_rate != self.get_sampling_rate(channel):
            self.ad7175.set_sampling_rate(
                WolverineiiDef.ADC_CHANNEL_LIST[adc_channel], sampling_rate)

    def get_sampling_rate(self, channel=WolverineiiDef.DEFAULT_RANGE):
        '''
        WolverineII Read the sampling rate setting of specific channel

        Args:
            channel:   string, ['100uA', '2mA', '5V', '5VCH2'], default '5V' set range for different channel.

        Returns:
            int, value, current module sampling rate in SPS.

        '''
        assert channel in wolverineii_function_info.keys()

        adc_channel = wolverineii_function_info[channel]['channel']

        return self.ad7175.get_sampling_rate(
            WolverineiiDef.ADC_CHANNEL_LIST[adc_channel])

    def _volt_to_target_unit(self, channel, volt):
        '''
        WolverineII get target unit value (wolverineii_function_info) from measured voltage

        Args:
            channel:  string, ['100uA', '2mA', '5V', '5VCH2'], the range of channel measure.
            volt:       float, the measured voltage by ad7175.

        Returns:
            float, value.

        '''
        assert channel in wolverineii_function_info.keys()

        return volt * wolverineii_function_info[channel]['coefficient']

    def set_measure_path(self, channel=WolverineiiDef.DEFAULT_RANGE):
        '''
        WolverineII set measure path.

        Args:
            channel:   string, ['100uA', '2mA', '5V', '5VCH2'], default '5V', set range for different channel.

        Returns:
            string, "done", api execution successful.

        '''
        assert channel in wolverineii_function_info.keys()

        if channel != self.get_measure_path().get(WolverineiiDef.SELECT_RANGE_KEY, ''):
            bits = wolverineii_function_info[channel]['bits']
            for bit in bits:
                self.pca9536.set_pin(bit[0], bit[1])

            time.sleep(WolverineiiDef.RELAY_DELAY_S)

        self.measure_path.clear()
        self.measure_path[WolverineiiDef.SELECT_RANGE_KEY] = channel

        return "done"

    def get_measure_path(self):
        '''
        WolverineII get measure path. This is a private function.

        Returns:
            dict, current channel and range.

        '''
        return self.measure_path

    def read_measure_value(self,
                           sample_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE,
                           count=WolverineiiDef.DEFAULT_COUNT):
        '''
        Read current average value. The returned value is calibrated if calibration mode is `cal`

        Args:
            sample_rate:    int, [5~250000], unit Hz, default 1000, set sampling rate of data acquisition, in SPS.
            count:          int, (>0), default 1, samples count taken for averaging.

        Returns:
            int, value, measured value defined by set_measure_path()
                        Voltage Channel always in mV
                        Current Channel always in mA
        '''
        assert isinstance(count, int) and count >= 1

        measure_path = self.get_measure_path()
        adc_channel = wolverineii_function_info[
            measure_path['range']]['channel']

        self.set_sampling_rate(sample_rate)

        target_data = list()
        for x in range(count):
            try:
                voltage = self.ad7175.read_volt(
                    WolverineiiDef.ADC_CHANNEL_LIST[adc_channel])
            except Exception as e:
                if (WolverineiiDef.ADC_ERROR_BIT & self.ad7175.read_register(WolverineiiDef.STATUS_REG_ADDR)):
                    reg_data = self.ad7175.read_register(WolverineiiDef.DATA_REG_ADDR)

                    if measure_path['range'] == '100uA':
                        curr_range = WolverineiiDef.CURR_RANGE_100uA
                        adc_range = str(curr_range) + 'A'
                    elif measure_path['range'] == '2mA':
                        curr_range = WolverineiiDef.CURR_RANGE_2mA
                        adc_range = str(curr_range) + 'A'
                    elif measure_path['range'] in ['5V', '5VCH2']:
                        volt_range = WolverineiiDef.VOLT_RANGE
                        adc_range = str(volt_range) + 'V'
                    else:
                        raise WolverineiiException('No measure path is set')

                    if reg_data == 0xFFFFFF:
                        raise WolverineiiException('Overrange! the value exceeds the {} range'.format(adc_range))
                    elif reg_data == 0x000000:
                        raise WolverineiiException('Underrange! the value is lower than \
                                             negative {} range'.format(adc_range))
                    else:
                        raise WolverineiiException("{}".format(e.message))
                else:
                    raise WolverineiiException("{}".format(e.message))

            adc_value = self._volt_to_target_unit(measure_path['range'],
                                                  voltage)
            cal_infor = measure_path['range']
            adc_value = self.calibrate(cal_infor, adc_value)
            target_data.append(adc_value)

        target_value = sum(target_data) / count

        return target_value

    def read_measure_list(self,
                          sample_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE,
                          count=WolverineiiDef.DEFAULT_COUNT):
        '''
        Read measured data in list.

        For example if count is 5, the return list can be: [3711, 3712, 3709, 3703, 3702].
        The returned value is calibrated if calibration mode is `cal`

        Args:
            sample_rate:    float, [5~250000], unit Hz, default 1000, set sampling rate of data acquisition, in SPS.
            count:          int, (>0), defualt 1, samples count taken for averaging. Default 1

        Returns:
            list, [value1, ..., valueN], measured value defined by set_measure_path()
                    Voltage Channel always in mV
                    Current Channel always in mA
        '''
        assert isinstance(count, int) and count >= 1

        measure_path = self.get_measure_path()
        adc_channel = wolverineii_function_info[
            measure_path['range']]['channel']

        self.set_sampling_rate(sample_rate)

        target_data = list()
        for x in range(count):
            try:
                voltage = self.ad7175.read_volt(
                    WolverineiiDef.ADC_CHANNEL_LIST[adc_channel])
            except Exception as e:
                if (WolverineiiDef.ADC_ERROR_BIT & self.ad7175.read_register(WolverineiiDef.STATUS_REG_ADDR)):
                    reg_data = self.ad7175.read_register(WolverineiiDef.DATA_REG_ADDR)

                    if measure_path['range'] == '100uA':
                        curr_range = WolverineiiDef.CURR_RANGE_100uA
                        adc_range = str(curr_range) + 'A'
                    elif measure_path['range'] == '2mA':
                        curr_range = WolverineiiDef.CURR_RANGE_2mA
                        adc_range = str(curr_range) + 'A'
                    elif measure_path['range'] in ['5V', '5VCH2']:
                        volt_range = WolverineiiDef.VOLT_RANGE
                        adc_range = str(volt_range) + 'V'
                    else:
                        raise WolverineiiException('No measure path is set')

                    if reg_data == 0xFFFFFF:
                        raise WolverineiiException('Overrange! the value exceeds the {} range'.format(adc_range))
                    elif reg_data == 0x000000:
                        raise WolverineiiException('Underrange! the value is lower than \
                                             negative {} range'.format(adc_range))
                    else:
                        raise WolverineiiException("{}".format(e.message))
                else:
                    raise WolverineiiException("{}".format(e.message))

            adc_value = self._volt_to_target_unit(measure_path['range'],
                                                  voltage)
            cal_infor = measure_path['range']
            adc_value = self.calibrate(cal_infor, adc_value)
            target_data.append(adc_value)

        return target_data

    def enable_continuous_sampling(
            self,
            channel=WolverineiiDef.DEFAULT_RANGE,
            sample_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE,
            down_sample=WolverineiiDef.DEFAULT_DOWN_SAMPLE,
            selection=WolverineiiDef.DEFAULT_SELECTION):
        '''
        This function enables continuous sampling and data throughput upload to upper stream.

        Down sampling is supported. For example, when down_sample =5, selection=max,
        select the maximal value from every 5 samples, so the actual data rate is reduced by 5.
        The output data inflow is calibrated if calibration mode is `cal`
        During continuous sampling, the setting functions, like set_calibration_mode(),
        set_measure_path(), cannot be called.

        Args:
            channel:    string, ['5V', '5VCH2', '5VBOTH', '100uA', '2mA'], default '5V', '5V' is voltage channel1.
                                '5VCH2' is voltage channel 2. '5VBOTH' is both voltage channels
                                '100uA' is 100uA current channel.
                                '2mA' is 2mA current channel.
            sample_rate:    float, [5~250000], unit Hz, default 1000, set sampling rate of data acquisition in SPS.
                                               please refer to AD7175 data sheet for more.
            down_sample:    int, (>0), default 1, down sample rate for decimation.
            selection:      string, ['max', 'min'], default 'max'. This parameter takes effect as long as down_sample is
                                    higher than 1. Default 'max'

        Returns:
            Str, 'done'
        '''
        assert channel in wolverineii_function_info.keys() + ['5VBOTH']

        if channel == '5VBOTH':
            adc_channel = 'all'
            # when enable 5VBOTH, channel 2 should be changed to voltage mode
            self.set_measure_path('5VCH2')
        else:
            adc_channel = WolverineiiDef.ADC_CHANNEL_LIST[
                wolverineii_function_info[channel]['channel']]
            self.set_measure_path(channel)

        self.ad7175.disable_continuous_sampling(adc_channel)
        time.sleep(WolverineiiDef.SWITCH_DELAY_S)
        self.ad7175.enable_continuous_sampling(adc_channel, sample_rate,
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

        if self.continuous_sample_mode == '5VBOTH':
            adc_channel = 'all'
        else:
            measure_path = self.get_measure_path()
            measure_scope = measure_path['range']
            adc_channel = WolverineiiDef.ADC_CHANNEL_LIST[
                wolverineii_function_info[measure_scope]['channel']]

        self.ad7175.disable_continuous_sampling(adc_channel)

        self.continuous_sample_mode = None

        return "done"

    def _volt_to_result(self, channel, adc_volt):
        '''
        This function converts the adc sample data to the user format result

        Args:
            channel (string):   '5V':       voltage channel #1
                                '5VCH2':    voltage channel #2
                                '5VBOTH':   both voltage channels
                                '100uA':    100uA current channel
                                '2mA':      2mA current channel
            adc_volt (list):    AD7175 sample data list

        Returns:
            Dict: {
                (rms_v1, <RMS in mVrms>),
                (avg_v1, <average in mVrms>),
                (max_v1, <maximal in mV>),
                (min_v1, <minimal in mV>),
                (rms_v2, <RMS in mVrms>),
                (avg_v2, <average in mVrms>),
                (max_v2, <maximal in mV>),
                (min_v2, <minimal in mV>),
                (rms_i, <RMS in mArms>),
                (avg_i, <average in mArms>),
                (max_i, <maximal in mA>),
                (min_i, <minimal in mA>)
            }
            for voltage voltage channel #1 and #2.
        '''
        assert channel in wolverineii_function_info.keys()

        target_data = []

        unit = wolverineii_function_info[channel]['unit']

        volt_to_target_unit = functools.partial(self._volt_to_target_unit,
                                                channel)
        target_data = [map(volt_to_target_unit, adc_volt), unit]
        temp_data = target_data[0]
        calibrate = functools.partial(self.calibrate, channel)
        temp_data = map(calibrate, temp_data)

        min_data = min(temp_data)
        max_data = max(temp_data)
        sum_data = sum(temp_data)
        avg_data = sum_data / len(temp_data)
        square_sum_data = sum([x**2 for x in temp_data])
        rms_data = math.sqrt(square_sum_data / len(temp_data))

        unit = target_data[1]
        suffix = wolverineii_function_info[channel]['suffix']
        result = dict()
        result['rms_' + suffix] = (rms_data, unit + 'rms')
        result['avg_' + suffix] = (avg_data, unit)
        result['max_' + suffix] = (max_data, unit)
        result['min_' + suffix] = (min_data, unit)

        return result

    def read_continuous_sampling_statistics(self,
                                            count=WolverineiiDef.DEFAULT_COUNT
                                            ):
        '''
        This function takes a number of samples to calculate RMS/average/max/min value of the set of sampled value.

        This function can only be called in continuous mode, a.k.a, after
        continuous_sampling_enable() function is called. Return 0 for the channels that are not enabled.
        The returned value is calibrated if calibration mode is `cal`

        Args:
            count:  int, (>0), defualt 1, samples count taken for calculation.

        Returns:
            dict, the channel data to be measured. {
                (rms_v1, <RMS in mVrms>),
                (avg_v1, <average in mVrms>),
                (max_v1, <maximal in mV>),
                (min_v1, <minimal in mV>),
                (rms_v2, <RMS in mVrms>),
                (avg_v2, <average in mVrms>),
                (max_v2, <maximal in mV>),
                (min_v2, <minimal in mV>),
                (rms_i, <RMS in mArms>),
                (avg_i, <average in mArms>),
                (max_i, <maximal in mA>),
                (min_i, <minimal in mA>)
            },
            for voltage voltage channel #1 and #2.
        '''
        assert isinstance(count, int) and count >= 1

        if self.continuous_sample_mode is None:
            return 0

        measure_path = self.get_measure_path()
        measure_scope = measure_path['range']

        channel_data = list()

        if self.continuous_sample_mode == "5VBOTH":
            try:
                channel_data = self.ad7175.get_continuous_sampling_voltage(
                    'all', count)
            except Exception as e:
                if (WolverineiiDef.ADC_ERROR_BIT & self.ad7175.read_register(WolverineiiDef.STATUS_REG_ADDR)):
                    reg_data = self.ad7175.read_register(WolverineiiDef.DATA_REG_ADDR)

                    if measure_path['range'] == '100uA':
                        curr_range = WolverineiiDef.CURR_RANGE_100uA
                        adc_range = str(curr_range) + 'A'
                    elif measure_path['range'] == '2mA':
                        curr_range = WolverineiiDef.CURR_RANGE_2mA
                        adc_range = str(curr_range) + 'A'
                    elif measure_path['range'] in ['5V', '5VCH2']:
                        volt_range = WolverineiiDef.VOLT_RANGE
                        adc_range = str(volt_range) + 'V'
                    else:
                        raise WolverineiiException('No measure path is set')

                    if reg_data == 0xFFFFFF:
                        raise WolverineiiException('Overrange! the value exceeds the {} range'.format(adc_range))
                    elif reg_data == 0x000000:
                        raise WolverineiiException('Underrange! the value is lower than \
                                             negative {} range'.format(adc_range))
                    else:
                        raise WolverineiiException("{}".format(e.message))
                else:
                    raise WolverineiiException("{}".format(e.message))

            result_ch1 = self._volt_to_result('5V', channel_data[0])
            result_ch2 = self._volt_to_result('5VCH2', channel_data[1])

            result = dict(result_ch1, **result_ch2)
        else:
            adc_channel = WolverineiiDef.ADC_CHANNEL_LIST[
                wolverineii_function_info[measure_scope]['channel']]

            try:
                channel_data = self.ad7175.get_continuous_sampling_voltage(
                    adc_channel, count)
            except Exception as e:
                if (WolverineiiDef.ADC_ERROR_BIT & self.ad7175.read_register(WolverineiiDef.STATUS_REG_ADDR)):
                    reg_data = self.ad7175.read_register(WolverineiiDef.DATA_REG_ADDR)

                    if measure_path['range'] == '100uA':
                        curr_range = WolverineiiDef.CURR_RANGE_100uA
                        adc_range = str(curr_range) + 'A'
                    elif measure_path['range'] == '2mA':
                        curr_range = WolverineiiDef.CURR_RANGE_2mA
                        adc_range = str(curr_range) + 'A'
                    elif measure_path['range'] in ['5V', '5VCH2']:
                        volt_range = WolverineiiDef.VOLT_RANGE
                        adc_range = str(volt_range) + 'V'
                    else:
                        raise WolverineiiException('No measure path is set')

                    if reg_data == 0xFFFFFF:
                        raise WolverineiiException('Overrange! the value exceeds the {} range'.format(adc_range))
                    elif reg_data == 0x000000:
                        raise WolverineiiException('Underrange! the value is lower than \
                                             negative {} range'.format(adc_range))
                    else:
                        raise WolverineiiException("{}".format(e.message))
                else:
                    raise WolverineiiException("{}".format(e.message))

            result = self._volt_to_result(measure_scope, channel_data)

        return result

    def datalogger_start(self, tag=0):
        '''
        Start labeling the samples for on a period of time for calculation.

        This function can only be called in continuous mode, a.k.a, after
        continuous_sampling_enable() function is called.
        Lable shall be on both channels if they are both enabled.

        Args:
            tag:    int, [0~0x0f], default 0, the value is upper 4 bits are valid, from 0x00 to 0x0f.

        Returns:
            Str: 'done'
        '''
        assert isinstance(tag, int) and 0 <= tag <= 0x0f

        for i in range(4):
            self.tag_pins[i].set_level((tag >> i) & 0x1)

        return "done"

    def datalogger_end(self):
        '''
        Stop labeling the samples.

        This function can only be called after
        continuous_sampling_enable() and datalogger_start() are called.

        Returns:
            Str: 'done'
        '''

        for i in range(4):
            self.tag_pins[i].set_level(0)

        return "done"
