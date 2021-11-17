# -*- coding: utf-8 -*-
import math
import time
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver


__author__ = 'jihuajiang@SmartGiant' + 'wenqiang.gao@gzseeing.com'
__version__ = '0.1.2'

wolverine_range_table = {
    "VOLT_5V": 0,
    "CURR_100uA": 1,
    "CURR_2mA": 2
}


class WolverineDef:
    CURRENT_CHANNEL = "CURR"
    VOLTAGE_CHANNEL = "VOLT"
    CURRENT_100UA_GAIN = 200.0
    CURRENT_100UA_OFFSET = 0
    CURRENT_100UA_SAMPLE_RES = 210   # ohm
    CURRENT_2MA_GAIN = 200.0
    CURRENT_2MA_OFFSET = 0
    CURRENT_2MA_SAMPLE_RES = 10   # ohm
    VOLTAGE_5V_GAIN = 1.0
    VOLTAGE_5V_OFFSET = 0
    SWITCH_DELAY = 0.001
    RELAY_DELAY_S = 0.003
    CURR_100UA = '100uA'
    CURR_2MA = '2mA'
    VOLT_5V = '5V'

    CHANNEL_CONFIG = {
        CURR_100UA: {
            "path": [("range_sel_bit", 1), ("meter_sel_bit", 1)],
            'adc_channel': 0,
            'suffix': 'i'
        },
        CURR_2MA: {
            "path": [("range_sel_bit", 0), ("meter_sel_bit", 1)],
            'adc_channel': 0,
            'suffix': 'i'
        },
        VOLT_5V: {
            "path": [("meter_sel_bit", 0), ],
            'adc_channel': 1,
            'suffix': 'v1'
        }
    }

    CAL_DATA_LEN = 9
    WRITE_CAL_DATA_PACK_FORMAT = "2fB"
    WRITE_CAL_DATA_UNPACK_FORMAT = "9B"

    READ_CAL_BYTE = 9
    READ_CAL_DATA_PACK_FORMAT = "9B"
    READ_CAL_DATA_UNPACK_FORMAT = "2fB"

    EEPROM_DEV_ADDR = 0x50
    NCT75_DEV_ADDR = 0x48
    COMPATIBLE_EEPROM_DEV_ADDR = 0x50
    COMPATIBLE_SENSOR_DEV_ADDR = 0x48

    # this is defined by MIXDAQT1SGR
    RANGE_SEL_BIT = 1
    METER_SEL_BIT = 3

    # default sampling rate is 1000 Hz which is defined in Driver ERS
    DEFAULT_SAMPLE_RATE = 1000

    # AD7175 reference voltage is 5V
    MVREF = 5000.0

    # Using crystal as AD7175 clock
    CLOCK = 'crystal'

    # AD7175 input voltage is bipolar
    POLAR = 'bipolar'

    ADC_SINC_SEL = ["sinc5_sinc1", "sinc3"]
    PLAD7175_REG_SIZE = 256
    MIX_DAQT1_REG_SIZE = 65535
    TIME_OUT = 0

    DEFAULT_COUNT = 1
    DEFAULT_SELECTION = 'max'
    DEFAULT_DOWN_SAMPLE = 5
    SELECT_RANGE_KEY = 'range'

    TAG_BASE_PIN = 4
    GPIO_OUTPUT_DIR = "output"


class WolverineException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Wolverine(SGModuleDriver):
    '''
    Wolverine is a compact version of the digital multimeter which internal ADC resolution is 24 bit.

    It can be used as
    high performance DMM to measure DC voltage and small signal DC current. In this class, adc channel 0 is current
    channel, adc channel 1 is voltage channel. DMM001 support signal measurement and continuous measurement. Note that
    if range_ctrl0 and range_ctrl1 not given, internal submodule GPIO device of MIX_DAQT1 will be used to control range.
    Note that calibration default is enabled. This class is legacy driver for normal boot.

    Args:
        i2c:             instance(I2C)/None,   which is used to control nct75 and cat24c32. If not given,
                                               emulator will be created.
        ad7175:          instance(ADC)/None,   Class instance of AD7175, if not using this parameter,
                                               will create emulator
        range_ctrl_pin:  instance(GPIO),       This can be Pin or xilinx gpio, used to control range.
        meter_ctrl_pin:  instance(GPIO),       This can be Pin or xilinx gpio, used to control measure channel
        ipcore:          instance(MIXDAQT1SGR)/string,  MIXDAQT1SGR ipcore driver instance or device name string,
                                                        if given, user should not use ad7175.


    Examples:
        Example for using no-aggregate IP:
            # normal init
            ad7175 = MIXAd7175SG('/dev/MIX_AD717X_0', 5000)
            i2c = I2C('/dev/i2c-1')
            gpio = GPIO(i2c)
            range_ctrl_pin = Pin(gpio, 1)
            meter_ctrl_pin = Pin(gpio, 3)
            wolverine = Wolverine(i2c, ad7175, range_ctrl_pin=range_ctrl_pin, meter_ctrl_pin=meter_ctrl_pin)

            # using ipcore device name string
            i2c = I2C('/dev/i2c-1')
            gpio = GPIO(i2c)
            range_ctrl_pin = Pin(gpio, 1)
            meter_ctrl_pin = Pin(gpio, 3)
            wolverine = Wolverine(i2c, '/dev/MIX_AD717X_0', range_ctrl_pin=range_ctrl_pin,
                                  meter_ctrl_pin=meter_ctrl_pin)

        Example for using aggregate IP:
            # normal init
            i2c = I2C('/dev/i2c-1')
            daqt1 = MIXDAQT1SGR('/dev/MIX_DAQT1', ad717x_chip='AD7175', ad717x_mvref=5000, use_spi=False, use_gpio=True)
            wolverine = Wolverine(i2c, ipcore=daqt1)

            # using ipcore device name
            i2c = I2C('/dev/i2c-1')
            wolverine = Wolverine(i2c, ipcore='/dev/MIX_DAQT1')

        Example for measuring voltage/current:
            wolverine.disable_continuous_sampling()
            wolverine.set_measure_path('5V')
            result = wolverine.read_measure_value()
            print("voltage={}, unit is mV".format(result))
            result = wolverine.read_measure_list(count=5)
            print("voltage_list={}, unit is mV".format(result))

            wolverine.set_measure_path('2mA')
            result = wolverine.read_measure_value()
            print("voltage={}, unit is mA".format(result))
            result = wolverine.read_measure_list(count=5)
            print("voltage_list={}, unit is mA".format(result))

        Example for continuous measuring:
            wolverine.enable_continuous_sampling('5V')
            result = wolverine.read_continuous_sampling_statistics(256)
            print("5V Result: average={}, max={}, min={}, rms={}".format(result['avg_v1'],
            result['max_v1'], result['min_v1'], result['rms_v1']))

            wolverine.enable_continuous_sampling('2mA')
            result = wolverine.read_continuous_sampling_statistics(256)
            print("2mA Result: average={}, max={}, min={}, rms={}".format(result['avg_i'],
            result['max_i'], result['min_i'], result['rms_i']))

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-LTJW-5-030"]

    rpc_public_api = [
        'set_sinc', 'get_sampling_rate', 'set_measure_path', 'get_measure_path',
        'read_measure_value', 'read_measure_list',
        'enable_continuous_sampling',
        'disable_continuous_sampling',
        'read_continuous_sampling_statistics', 'datalogger_start',
        'datalogger_end'
    ] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, ad7175=None, range_ctrl_pin=None,
                 meter_ctrl_pin=None, ipcore=None):

        if ad7175 and range_ctrl_pin and meter_ctrl_pin and not ipcore:
            if isinstance(ad7175, basestring):
                axi4 = AXI4LiteBus(ad7175, WolverineDef.PLAD7175_REG_SIZE)
                self.ad7175 = MIXAd7175SG(axi4, mvref=WolverineDef.MVREF, code_polar=WolverineDef.POLAR,
                                          clock=WolverineDef.CLOCK)
            else:
                self.ad7175 = ad7175
            self.range_ctrl_pin = range_ctrl_pin
            self.meter_ctrl_pin = meter_ctrl_pin
        elif not ad7175 and not range_ctrl_pin and not meter_ctrl_pin and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, WolverineDef.MIX_DAQT1_REG_SIZE)
                self.ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=WolverineDef.MVREF,
                                          code_polar=WolverineDef.POLAR, clock=WolverineDef.CLOCK, use_gpio=True)
            else:
                self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x
            gpio = self.ipcore.gpio
            self.range_ctrl_pin = Pin(gpio, WolverineDef.RANGE_SEL_BIT)
            self.meter_ctrl_pin = Pin(gpio, WolverineDef.METER_SEL_BIT)
            self.tag_pins = [
                Pin(gpio, WolverineDef.TAG_BASE_PIN + x,
                    WolverineDef.GPIO_OUTPUT_DIR) for x in range(4)
            ]
        elif not ad7175 and range_ctrl_pin and meter_ctrl_pin and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, WolverineDef.MIX_DAQT1_REG_SIZE)
                self.ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=WolverineDef.MVREF,
                                          code_polar=WolverineDef.POLAR, clock=WolverineDef.CLOCK, use_gpio=True)
            else:
                self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x
            self.range_ctrl_pin = range_ctrl_pin
            self.meter_ctrl_pin = meter_ctrl_pin
            gpio = self.ipcore.gpio
            self.tag_pins = [
                Pin(gpio, WolverineDef.TAG_BASE_PIN + x,
                    WolverineDef.GPIO_OUTPUT_DIR) for x in range(4)
            ]
        else:
            raise WolverineException("Invalid parameter, please check")

        eeprom = CAT24C32(WolverineDef.EEPROM_DEV_ADDR, i2c)
        nct75 = NCT75(WolverineDef.NCT75_DEV_ADDR, i2c)
        super(Wolverine, self).__init__(eeprom, nct75, range_table=wolverine_range_table)

        self.channel_path = {'range_sel_bit': self.range_ctrl_pin, 'meter_sel_bit': self.meter_ctrl_pin}
        self.measure_path = dict()
        self.measure_path['range'] = WolverineDef.VOLT_5V

    def post_power_on_init(self, timeout=WolverineDef.TIME_OUT):
        '''
        Init wolverine module to a know harware state.

        This function will set io direction to output and set default range to '5V'.

        Args:
            timeout:      float, unit Second, execute timeout

        '''
        self.reset(timeout)
        self.load_calibration()
        return "done"

    def reset(self, timeout=WolverineDef.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, unit Second, execute timeout.

        '''
        self.range_ctrl_pin.set_dir('output')
        self.meter_ctrl_pin.set_dir('output')
        self.set_measure_path(WolverineDef.VOLT_5V)
        self.ad7175.channel_init()
        self.set_sampling_rate(WolverineDef.DEFAULT_SAMPLE_RATE)

    def get_driver_version(self):
        '''
        Get wolverine driver version.

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
            channel:        string, ['5V', '2mA', '100uA'], voltage or current channel
            calibration_vectors: list, it contains value pairs of module reading and benchmark
                                 value got from external equipemnets. [[module_raw1,benchmark1],
                                 [module_raw1,benchmark2],
                                 ...
                                 [module_rawN,benchmarkN]]

        Returns:
            string, 'done', execute successful.

        '''
        assert channel in ['5V', '100uA', '2mA']
        return super(Wolverine, self).write_module_calibration(channel, calibration_vectors)

    def set_sinc(self, channel, sinc):
        '''
        wolverineii set digtal filter.

        Args:
            channel:    string, ['100uA', '2mA', '5V'], set range for different channel.
            sinc:       string, ["sinc5_sinc1", "sinc3"]

        Example:
            wolverineii.set_sinc("100uA", "sinc5_sinc1")

        '''
        assert channel in WolverineDef.CHANNEL_CONFIG.keys()
        assert sinc in WolverineDef.ADC_SINC_SEL

        self.ad7175.set_sinc(WolverineDef.CHANNEL_CONFIG[channel]['adc_channel'], sinc)

    def set_sampling_rate(self, sampling_rate):
        '''
        wolverine set sampling rate.

        Note that sampling rate is not discontinuous, all support sampling
        rate can be found in ad7175 datasheet.

        Args:
            sampling_rate:      float, [5~250000], adc measure sampling rate, which is not continuous,
                                                        please refer to ad7175 datasheet.

        Returns:
            string, "done", api execution successful.

        '''
        assert 5 <= sampling_rate <= 250000

        channel = self.measure_path['range']
        if sampling_rate != self.get_sampling_rate(channel):
            self.ad7175.set_sampling_rate(WolverineDef.CHANNEL_CONFIG[channel]['adc_channel'], sampling_rate)

    def get_sampling_rate(self, channel=WolverineDef.VOLT_5V):
        '''
        wolverine Read the sampling rate setting

        Args:
            channel:            string, ['5V', '2mA', '100uA'], get sampling rate for different channel.

        Returns:
            int, value, current module sampling rate in SPS.

        '''
        assert channel in WolverineDef.CHANNEL_CONFIG.keys()

        return self.ad7175.get_sampling_rate(WolverineDef.CHANNEL_CONFIG[channel]['adc_channel'])

    def set_measure_path(self, channel=WolverineDef.VOLT_5V):
        '''
        wolverine set measure path.

        Args:
            channel:       string, ['100uA', '2mA', '5V'], set range for different channel

        Returns:
            string, "done", api execution successful.

        '''
        assert channel in WolverineDef.CHANNEL_CONFIG.keys()

        if channel != self.get_measure_path():
            path_bits = WolverineDef.CHANNEL_CONFIG[channel]['path']
            for bits in path_bits:
                self.channel_path[bits[0]].set_level(bits[1])

            time.sleep(WolverineDef.RELAY_DELAY_S)

        self.measure_path.clear()
        self.measure_path[WolverineDef.SELECT_RANGE_KEY] = channel

        return "done"

    def get_measure_path(self):
        '''
        wolverine get measure path.

        Returns:
            dict, current channel and range.

        '''
        return self.measure_path

    def read_measure_value(self, sample_rate=WolverineDef.DEFAULT_SAMPLE_RATE,
                           count=WolverineDef.DEFAULT_COUNT):
        '''
        Read current average value. The returned value is calibrated if calibration mode is `cal`

        Args:
            sample_rate (int, optional): set sampling rate of data acquisition, in SPS. Default 1000
            count (int, optional): samples count taken for averaging. Default 1

        Returns:
            Int:   measured value defined by set_measure_path() 
                   Voltage Channel always in mV 
                   Current Channel always in mA
        '''
        assert isinstance(sample_rate, int)
        assert isinstance(count, int) and count >= 1

        measure_path = self.get_measure_path()
        adc_channel = WolverineDef.CHANNEL_CONFIG[measure_path['range']]['adc_channel']

        self.set_sampling_rate(sample_rate)

        cal_item = WolverineDef.CURRENT_CHANNEL + "_" + measure_path['range']
        if measure_path['range'] == WolverineDef.VOLT_5V:
            gain = WolverineDef.VOLTAGE_5V_GAIN
            cal_item = WolverineDef.VOLTAGE_CHANNEL + "_" + measure_path['range']
        elif measure_path['range'] == WolverineDef.CURR_100UA:
            gain = WolverineDef.CURRENT_100UA_GAIN
            sample_res = WolverineDef.CURRENT_100UA_SAMPLE_RES
        else:
            gain = WolverineDef.CURRENT_2MA_GAIN
            sample_res = WolverineDef.CURRENT_2MA_SAMPLE_RES

        target_data = list()
        for x in range(count):
            voltage = self.ad7175.read_volt(adc_channel)
            adc_value = (voltage / gain) if \
                measure_path['range'] == WolverineDef.VOLT_5V else \
                voltage / gain / sample_res
            adc_value = self.calibrate(cal_item, adc_value)
            target_data.append(adc_value)

        target_value = sum(target_data) / count

        return target_value

    def read_measure_list(self, sample_rate=WolverineDef.DEFAULT_SAMPLE_RATE,
                          count=WolverineDef.DEFAULT_COUNT):
        '''
        For example if count is 5, the return list can be: [3711, 3712, 3709, 3703, 3702]. 
        The returned value is calibrated if calibration mode is `cal`

        Args:
            sample_rate (int, optional): set sampling rate of data acquisition, in SPS. Default 1000
            count (int, optional): samples count taken for averaging. Default 1

        Returns:
            List:   measured value defined by set_measure_path()
                    Voltage Channel always in mV
                    Current Channel always in mA
        '''
        assert isinstance(sample_rate, int)
        assert isinstance(count, int) and count >= 1

        measure_path = self.get_measure_path()
        adc_channel = WolverineDef.CHANNEL_CONFIG[measure_path['range']]['adc_channel']

        self.set_sampling_rate(sample_rate)

        cal_item = WolverineDef.CURRENT_CHANNEL + "_" + measure_path['range']
        if measure_path['range'] == WolverineDef.VOLT_5V:
            gain = WolverineDef.VOLTAGE_5V_GAIN
            cal_item = WolverineDef.VOLTAGE_CHANNEL + "_" + measure_path['range']
        elif measure_path['range'] == WolverineDef.CURR_100UA:
            gain = WolverineDef.CURRENT_100UA_GAIN
            sample_res = WolverineDef.CURRENT_100UA_SAMPLE_RES
        else:
            gain = WolverineDef.CURRENT_2MA_GAIN
            sample_res = WolverineDef.CURRENT_2MA_SAMPLE_RES

        target_data = list()
        for x in range(count):
            voltage = self.ad7175.read_volt(adc_channel)
            adc_value = (voltage / gain) if \
                measure_path['range'] == WolverineDef.VOLT_5V else \
                (voltage / gain / sample_res)
            adc_value = self.calibrate(cal_item, adc_value)
            target_data.append(adc_value)

        return target_data

    def enable_continuous_sampling(self, channel=WolverineDef.VOLT_5V,
                                   sample_rate=WolverineDef.DEFAULT_SAMPLE_RATE,
                                   down_sample=WolverineDef.DEFAULT_DOWN_SAMPLE,
                                   selection=WolverineDef.DEFAULT_SELECTION):
        '''
        This function enables continuous sampling and data throughput upload to upper stream.
        Down sampling is supported.
        For example: when down_sample =5, selection=max, select the maximal value from every 5
            samples, so the actual data rate is reduced by 5.
        The output data inflow is calibrated if calibration mode is `cal`
        During continuous sampling, the setting functions, like set_calibration_mode(),
            set_measure_path(), cannot be called.

        Args:
            channel (string):   '5V':       voltage channel #1
                                '100uA':    100uA current channel
                                '2mA':      2mA current channel
                                Default:    5V
            sample_rate (int):  set sampling rate of data acquisition, in SPS. Default 1000
            down_sample (int):  down sample rate for decimation.
            selection (string): 'max'|'min'. This parameter takes effect as long as down_sample is
                                    higher than 1. Default 'max'

        Returns:
            Str: 'done'
        '''
        assert channel in WolverineDef.CHANNEL_CONFIG.keys()

        adc_channel = WolverineDef.CHANNEL_CONFIG[channel]['adc_channel']
        self.ad7175.disable_continuous_sampling(adc_channel)
        time.sleep(WolverineDef.SWITCH_DELAY)
        self.ad7175.enable_continuous_sampling(adc_channel, sample_rate,
                                               down_sample, selection)

        self.measure_path[WolverineDef.SELECT_RANGE_KEY] = channel

        return "done"

    def disable_continuous_sampling(self):
        '''
        This function disables continuous sampling and data throughput upload to upper stream.
        This function can only be called in continuous mode, a.k.a, after enable_continuous_sampling()
            function is called.

        Returns:
            Str: 'done'
        '''

        measure_path = self.get_measure_path()
        adc_channel = WolverineDef.CHANNEL_CONFIG[measure_path['range']]['adc_channel']
        self.ad7175.disable_continuous_sampling(adc_channel)

        return "done"

    def read_continuous_sampling_statistics(self,
                                            count=WolverineDef.DEFAULT_COUNT):
        '''
        This function takes a number of samples to calculate RMS/average/max/min value of the set of
            sampled value.This function can only be called in continuous mode, a.k.a, after
            enable_continuous_sampling() function is called. Return 0 for the channels that are not enabled. 
        The returned value is calibrated if calibration mode is `cal`

        Args:
            count (int): samples count taken for calculation. Default 1

        Returns:
            Dict: {
                (rms_v1, <RMS in mVrms>),
                (avg_v1, <average in mVrms>),
                (max_v1, <maximal in mV>),
                (min_v1, <minimal in mV>),
                (rms_i, <RMS in mArms>),
                (avg_i, <average in mArms>),
                (max_i, <maximal in mA>),
                (min_i, <minimal in mA>)
            }
            for voltage voltage channel #1 and #2.
        '''

        assert isinstance(count, int) and count >= 1

        measure_path = self.get_measure_path()
        adc_channel = WolverineDef.CHANNEL_CONFIG[measure_path['range']]['adc_channel']

        channel_data = list()
        try:
            channel_data = self.ad7175.get_continuous_sampling_voltage(
                adc_channel, count)
        except Exception:
            raise

        min_data = min(channel_data)
        max_data = max(channel_data)
        sum_Data = sum(channel_data)
        avg_data = sum_Data / len(channel_data)
        suqare_sum_data = sum([x**2 for x in channel_data])
        rms_data = math.sqrt(suqare_sum_data / len(channel_data))

        result = dict()
        cal_item = WolverineDef.CURRENT_CHANNEL + "_" + measure_path['range']
        suffix = WolverineDef.CHANNEL_CONFIG[measure_path['range']]['suffix']
        if measure_path['range'] == WolverineDef.VOLT_5V:
            gain = WolverineDef.VOLTAGE_5V_GAIN
            rms = rms_data / gain
            voltage = avg_data / gain
            max_voltage = max_data / gain
            min_voltage = min_data / gain
            cal_item = WolverineDef.VOLTAGE_CHANNEL + "_" + measure_path['range']
            voltage = self.calibrate(cal_item, voltage)

            result['rms_' + suffix] = (rms, 'mVrms')
            result['avg_' + suffix] = (voltage, 'mV')
            result['max_' + suffix] = (max_voltage, 'mV')
            result['min_' + suffix] = (min_voltage, 'mV')
            return result
        elif measure_path['range'] == WolverineDef.CURR_100UA:
            gain = WolverineDef.CURRENT_100UA_GAIN
            sample_res = WolverineDef.CURRENT_100UA_SAMPLE_RES
        else:
            gain = WolverineDef.CURRENT_2MA_GAIN
            sample_res = WolverineDef.CURRENT_2MA_SAMPLE_RES

        rms = (rms_data / gain) / sample_res
        current = (avg_data / gain) / sample_res
        max_current = (max_data / gain) / sample_res
        min_current = (min_data / gain) / sample_res
        current = self.calibrate(cal_item, current)

        result['rms_' + suffix] = (rms, 'mArms')
        result['avg_' + suffix] = (current, 'mA')
        result['max_' + suffix] = (max_current, 'mA')
        result['min_' + suffix] = (min_current, 'mA')
        return result

    def datalogger_start(self, tag=0):
        '''
        Start labeling the samples for on a period of time for calculation.
        This function can only be called in continuous mode, a.k.a, after
        enable_continuous_sampling() function is called. 
        Lable shall be on both channels if they are both enabled.

        Args:
            tag (int,  [0, 0x0f]): the value is low 4 bits are valid, from 0x00 to 0x0f.

        Returns:
            Str: 'done'
        '''

        assert tag & 0x0f == tag
        for i in range(4):
            self.tag_pins[i].set_level((tag >> i) & 0x1)

        return "done"

    def datalogger_end(self):
        '''
        Stop labeling the samples. This function can only be called after
            enable_continuous_sampling() and datalogger_start() are called.

        Returns:
            Str: 'done'
        '''

        for i in range(4):
            self.tag_pins[i].set_level(0)

        return "done"
