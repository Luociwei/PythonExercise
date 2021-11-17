# -*- coding: utf-8 -*-
import math
import time
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.bus.pin import Pin


__author__ = 'jiebin.zheng@SmartGiant'
__version__ = '0.1.4'


scope002006_range_table = {
    "CURR_AVG": 0
}


class Scope002006Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Scope002006Def:
    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    MAX = 'max'
    MIN = 'min'
    CURRENT_CHANNEL = 0
    CURRENT_GAIN = 7.6
    CURRENT_SAMPLE_RESISTOR = 0.2  # 'ohm'
    DEFAULT_TAG = 0
    DEFAULT_COUNT = 1
    DEFAULT_SAMPLING_RATE = 1000
    DEFAULT_DOWN_SAMPLE = 1
    DEFAULT_SELECTION = MAX
    MIX_DAQT1_REG_SIZE = 65535
    AD7175_REG_SIZE = 256
    AD7175_MVREF = 2500.0  # mv
    AD7175_CODE_POLAR = "bipolar"
    AD7175_BUFFER_FLAG = "enable"
    AD7175_REFERENCE_SOURCE = "extern"
    AD7175_CLOCK = "crystal"
    TAG_BASE_PIN = 4
    GPIO_OUTPUT_DIR = "output"
    SWITCH_DELAY_S = 0.001
    ADC_SINC_SEL = ["sinc5_sinc1", "sinc3"]
    TIME_OUT = 0.1


class Scope002006(SGModuleDriver):
    '''
    Scope002006 Module is used for high precision current (DC) measurement.

    compatible = ["GQQ-ML3G-5-06A", "GQQ-ML3G-5-06B", "GQQ-ML3G-5-06C", "GQQ-ML3G-5-060"]

    simultaneously and continuously data recording, the raw data can be
    uploaded to PC real time through Ethernet. The module shall work together with integrated
    control unit (ICU), which could achieve high-precision, automatic measurement.
    Current Input Channel: 15uA ~ 1.5A

    Note:This class is legacy driver for normal boot.

    Args:
        i2c:        instance(I2C)/None,       If not given, PLI2CBus emulator will be created.
        ipcore:     instance(MIXDAQT1)/None,  If daqt1 given, then use MIXDAQT1's AD7175.

    Examples:
        If the params `ipcore` is valid, then use MIXDAQT1 aggregated IP;
        Otherwise, if the params `ad7175`, use non-aggregated IP.

        # use MIXDAQT1 aggregated IP
        i2c = PLI2CBus('/dev/MIX_I2C_0')
        ip_daqt1 = MIXDAQT1('/dev/MIX_DAQT1_0', ad717x_chip='AD7175', ad717x_mvref=2500,
                 use_spi=False, use_gpio=False)
        scope002006 = Scope002006(i2c=i2c,
                                  ad7175=None,
                                  ipcore=ip_daqt1)

        # use non-aggregated IP
        ad7175 = PLAD7175('/dev/MIX_AD717x_0', 2500)
        i2c = PLI2CBus('/dev/MIX_I2C_1')
        scope002006 = Scope002006(i2c=i2c,
                                  ad7175=ad7175,
                                  ipcore=None)

        # Scope002006 measure current once
        current_value = scope002006.read_mesure_value()
        print current_value

        # Scope002006 measure current in continuous mode
        scope002006.enable_continuous_sampling(sample_rate=125000)
        current_value = scope002006.read_continuous_sampling_statistics(512)
        print current_value
    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-ML3G-5-06A", "GQQ-ML3G-5-06B", "GQQ-ML3G-5-06C", "GQQ-ML3G-5-060", "GQQ-ML3G-5-06D"]

    rpc_public_api = ['get_sampling_rate', 'read_measure_value', 'read_measure_list', 'set_sinc',
                      'enable_continuous_sampling', 'disable_continuous_sampling',
                      'read_continuous_sampling_statistics', 'datalogger_start',
                      'datalogger_end'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, ad7175=None, ipcore=None):

        self.eeprom = CAT24C32(Scope002006Def.EEPROM_DEV_ADDR, i2c)
        self.sensor = NCT75(Scope002006Def.SENSOR_DEV_ADDR, i2c)

        if ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, Scope002006Def.MIX_DAQT1_REG_SIZE)
                ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=Scope002006Def.AD7175_MVREF,
                                     code_polar=Scope002006Def.AD7175_CODE_POLAR,
                                     reference=Scope002006Def.AD7175_REFERENCE_SOURCE,
                                     buffer_flag=Scope002006Def.AD7175_BUFFER_FLAG,
                                     clock=Scope002006Def.AD7175_CLOCK,
                                     use_spi=False, use_gpio=True)
            ipcore.ad717x.config = {
                "ch0": {"P": "AIN0", "N": "AIN1"}
            }
            self.ad7175 = ipcore.ad717x
            self.gpio = ipcore.gpio
            self.tag_pins = [Pin(self.gpio, Scope002006Def.TAG_BASE_PIN + x,
                                 Scope002006Def.GPIO_OUTPUT_DIR) for x in xrange(4)]
        elif ad7175:
            if isinstance(ad7175, basestring):
                axi4_bus = AXI4LiteBus(ad7175, Scope002006Def.AD7175_REG_SIZE)
                ad7175 = MIXAd7175SG(axi4_bus, mvref=Scope002006Def.AD7175_MVREF,
                                     code_polar=Scope002006Def.AD7175_CODE_POLAR,
                                     reference=Scope002006Def.AD7175_REFERENCE_SOURCE,
                                     buffer_flag=Scope002006Def.AD7175_BUFFER_FLAG,
                                     clock=Scope002006Def.AD7175_CLOCK)

            ad7175.config = {
                "ch0": {"P": "AIN0", "N": "AIN1"}
            }
            self.ad7175 = ad7175
        else:
            raise Scope002006Exception('Use one of aggregated IP or AD717X')

        super(Scope002006, self).__init__(self.eeprom, self.sensor,
                                          range_table=scope002006_range_table)

    def post_power_on_init(self, timeout=Scope002006Def.TIME_OUT):
        '''
        Init Scope002006 module to a know harware state.

        This function will reset ad7175.

        Args:
            timeout:      float, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=Scope002006Def.TIME_OUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, unit Second, execute timeout.

        '''
        start_time = time.time()
        while True:
            try:
                self.ad7175.reset()
                self.ad7175.channel_init()
                self.ad7175.set_sampling_rate(Scope002006Def.CURRENT_CHANNEL, Scope002006Def.DEFAULT_SAMPLING_RATE)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise Scope002006Exception("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get Scope002006 driver version.

        Returns:
            string, current driver version.

        Examples:
            version = scope002006.get_driver_version()
            print(version)

        '''
        return __version__

    def get_sampling_rate(self):
        '''
        Scope002006 get sampling rate of adc.

        Returns:
            float, adc measure sampling rate, which is not continuous,
                   please refer to ad7175 datasheet.

        Examples:
            sampling_rate = scope002006.get_sampling_rate()
            print(sampling_rate)

        '''
        return self.ad7175.get_sampling_rate(Scope002006Def.CURRENT_CHANNEL)

    def write_module_calibration(self, calibration_vectors):
        '''
        This module function calculates module level calibration parameters and write them into EEPROM.

        For module level calibration, MacSW just needs to get raw reading from module and benchmark value from
        trustable equipments, and give all the values to module driver for calculation, doesn’t have to know how
        many the calibration parameters are needed by the particular module, or how they get stored and used
        by module drivers.

        Args:
            calibration_vectors:    list, It contains value pairs of module raw reading and benchmark value
                                          got from external equipments. for example, [[module_raw1,benchmark1],
                                          [module_raw1,benchmark2], …, [module_rawN,benchmarkN]]

        Returns:
            string, "done", api execution successful.

        '''
        return super(Scope002006, self).write_module_calibration('CURR_AVG', calibration_vectors)

    def set_sinc(self, sinc):
        '''
        Scope002006 set digtal filter.

        Args:
            sinc:       string, ["sinc5_sinc1", "sinc3"]

        Example:
            Scope002006.set_sinc(sinc5_sinc1")

        '''
        assert sinc in Scope002006Def.ADC_SINC_SEL

        self.ad7175.set_sinc(Scope002006Def.CURRENT_CHANNEL, sinc)

    def read_measure_value(self, sample_rate=Scope002006Def.DEFAULT_SAMPLING_RATE, count=Scope002006Def.DEFAULT_COUNT):
        '''
        Scope002006 read measure current.

        Args:
            sample_rate:    float, [5~250000], adc measure sampling rate, which is not continuous,
                                               please refer to ad7175 datasheet.
            count:          int, samples count taken for averaging. Default 1.

        Returns:
            float, current value, unit is mA.

        Examples:
            current = scope002006.read_measure_value()
            print(current)

        '''
        assert 5 <= sample_rate <= 250000
        assert isinstance(count, int) and (count > 0)

        # Set sampling_rate
        if sample_rate != self.get_sampling_rate():
            self.ad7175.set_sampling_rate(Scope002006Def.CURRENT_CHANNEL, sample_rate)

        # Calculate current value
        sum = 0
        for i in range(count):
            volt = self.ad7175.read_volt(Scope002006Def.CURRENT_CHANNEL)
            current = (volt / Scope002006Def.CURRENT_GAIN) / Scope002006Def.CURRENT_SAMPLE_RESISTOR
            sum += current
        avg_current = sum / count
        avg_current = self.calibrate('CURR_AVG', avg_current)

        return avg_current

    def read_measure_list(self, sample_rate=Scope002006Def.DEFAULT_SAMPLING_RATE, count=Scope002006Def.DEFAULT_COUNT):
        '''
        Scope002006 read measure currents.

        Args:
            sample_rate:    float, [5~250000], adc measure sampling rate, which is not continuous,
                                               please refer to ad7175 datasheet.
            count:          int, samples count taken for averaging. Default 1.

        Returns:
            list, return a list of current values, unit is mA.

        Examples:
            current_list = scope002006.read_measure_list()
            print(current_list)

        '''
        assert 5 <= sample_rate <= 250000
        assert isinstance(count, int) and (count > 0)

        return [self.read_measure_value(sample_rate, Scope002006Def.DEFAULT_COUNT) for i in range(count)]

    def enable_continuous_sampling(self, sample_rate=Scope002006Def.DEFAULT_SAMPLING_RATE,
                                   down_sample=Scope002006Def.DEFAULT_DOWN_SAMPLE,
                                   selection=Scope002006Def.DEFAULT_SELECTION):
        '''
        Scope002006 enables continuous sampling and data throughput upload to upper stream.

        Args:
            sample_rate:    float, [5~250000], adc measure sampling rate, which is not continuous,
                                               please refer to ad7175 datasheet.
            down_sample:    int, [0]|[1, 5~100], 0 means not enable max sample function.Default 1.
            selection:      string, 'max'|'min", This parameter takes effect as long as down_sample
                                     is higher than 1. Default ‘max’.

        Returns:
            string, 'done', api execution successful.

        Examples:
            scope002006.enable_continuous_sampling()

        '''
        assert 5 <= sample_rate <= 250000
        assert down_sample == 1 or down_sample in [i for i in range(5, 101)]
        assert selection in [Scope002006Def.MAX, Scope002006Def.MIN]

        self.disable_continuous_sampling()
        time.sleep(Scope002006Def.SWITCH_DELAY_S)
        self.ad7175.enable_continuous_sampling(Scope002006Def.CURRENT_CHANNEL, sample_rate, down_sample, selection)

        return 'done'

    def disable_continuous_sampling(self):
        '''
        Scope002006 stop continuous measure.

        Returns:
            string, "done", api execution successful.

        Examples:
            scope002006.disable_continuous_sampling()

        '''
        self.ad7175.disable_continuous_sampling(Scope002006Def.CURRENT_CHANNEL)

        return "done"

    def read_continuous_sampling_statistics(self, count=Scope002006Def.DEFAULT_COUNT):
        '''
        Scope002006 measure current in continuous mode.
        Before call this function, continuous current measure must be started first.

        Args:
            count:    int, [1~512], sampling numbers.

        Returns:
            dict, {"rms": (value, 'mArms'), "avg": (value, 'mA'), "max": (value, 'mA'), "min": (value, 'mA')},
                  rms, avg, max and min current with unit.

        Examples:
            # input a 1khz, 2vpp, sine wave to current channel.
            scope002006.enable_continuous_sampling(sample_rate=10000)
            current_dict = scope002006.read_continuous_sampling_statistics(512)
            print(current_dict)
        '''
        assert isinstance(count, int) and count > 0 and count <= 512

        adc_volt_data_list = self.ad7175.get_continuous_sampling_voltage(Scope002006Def.CURRENT_CHANNEL, count)

        min_data = min(adc_volt_data_list)
        max_data = max(adc_volt_data_list)
        sum_Data = sum(adc_volt_data_list)
        avg_data = sum_Data / len(adc_volt_data_list)
        suqare_sum_data = sum([x**2 for x in adc_volt_data_list])
        rms_data = math.sqrt(suqare_sum_data / len(adc_volt_data_list))

        # mArms
        rms_current = (rms_data / Scope002006Def.CURRENT_GAIN) / Scope002006Def.CURRENT_SAMPLE_RESISTOR
        # mA
        avg_current = (avg_data / Scope002006Def.CURRENT_GAIN) / Scope002006Def.CURRENT_SAMPLE_RESISTOR
        max_current = (max_data / Scope002006Def.CURRENT_GAIN) / Scope002006Def.CURRENT_SAMPLE_RESISTOR
        min_current = (min_data / Scope002006Def.CURRENT_GAIN) / Scope002006Def.CURRENT_SAMPLE_RESISTOR

        avg_current = self.calibrate('CURR_AVG', avg_current)

        result = dict()
        result['rms'] = (rms_current, 'mArms')
        result['avg'] = (avg_current, 'mA')
        result['max'] = (max_current, 'mA')
        result['min'] = (min_current, 'mA')

        return result

    def datalogger_start(self, tag=Scope002006Def.DEFAULT_TAG):
        '''
        Scope002006 set tag value for upload data.

        Args:
            tag:    int, [0x0~0xf], the value is upper 4 bits are valid, default is 0x0.

        Returns:
            string, "done", api execution successful.

        Examples:
            scope002006.datalogger_start()

        '''
        assert 0x0 <= tag <= 0xf

        for i in xrange(4):
            self.tag_pins[i].set_level((tag >> i) & 0x1)

        return 'done'

    def datalogger_end(self):
        '''
        Scope002006 clear tag value for upload data.

        Returns:
            string, "done", api execution successful.

        Examples:
            scope002006.datalogger_end()

        '''
        for i in xrange(4):
            self.tag_pins[i].set_level(0)

        return 'done'
