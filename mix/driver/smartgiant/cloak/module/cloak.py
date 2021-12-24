# -*- coding: utf-8 -*-
import math
import time
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.smartgiant.common.ipcore.mix_ad7177_sg_emulator import MIXAd7177SGEmulator
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7177SG
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.core.bus.pin import Pin


__author__ = 'yuanle@SmartGiant' + 'weiping.mo@SmartGiant'
__version__ = '0.2'


cloak_calibration_info = {
    'CURR_AVG': {
        'level1': {'unit_index': 0, 'unit': 'mA'},
        'level2': {'unit_index': 1, 'unit': 'mA'},
        'level3': {'unit_index': 2, 'unit': 'mA'},
        'level4': {'unit_index': 3, 'unit': 'mA'},
        'level5': {'unit_index': 4, 'unit': 'mA'},
        'level6': {'unit_index': 5, 'unit': 'mA'},
        'level7': {'unit_index': 6, 'unit': 'mA'},
        'level8': {'unit_index': 7, 'unit': 'mA'},
        'level9': {'unit_index': 8, 'unit': 'mA'},
        'level10': {'unit_index': 9, 'unit': 'mA'}
    },
    'VOLT_RMS': {
        'level1': {'unit_index': 10, 'unit': 'mV'},
        'level2': {'unit_index': 11, 'unit': 'mV'},
        'level3': {'unit_index': 12, 'unit': 'mV'},
        'level4': {'unit_index': 13, 'unit': 'mV'},
        'level5': {'unit_index': 14, 'unit': 'mV'},
        'level6': {'unit_index': 15, 'unit': 'mV'},
        'level7': {'unit_index': 16, 'unit': 'mV'},
        'level8': {'unit_index': 17, 'unit': 'mV'},
        'level9': {'unit_index': 18, 'unit': 'mV'},
        'level10': {'unit_index': 19, 'unit': 'mV'}
    },
    'VOLT_AVG': {
        'level1': {'unit_index': 20, 'unit': 'mV'},
        'level2': {'unit_index': 21, 'unit': 'mV'},
        'level3': {'unit_index': 22, 'unit': 'mV'},
        'level4': {'unit_index': 23, 'unit': 'mV'},
        'level5': {'unit_index': 24, 'unit': 'mV'},
        'level6': {'unit_index': 25, 'unit': 'mV'},
        'level7': {'unit_index': 26, 'unit': 'mV'},
        'level8': {'unit_index': 27, 'unit': 'mV'},
        'level9': {'unit_index': 28, 'unit': 'mV'},
        'level10': {'unit_index': 29, 'unit': 'mV'}
    }
}

cloak_range_table = {
    "CURR_AVG": 0,
    "VOLT_RMS": 1,
    "VOLT_AVG": 2
}


class CloakDef:
    EEPROM_DEV_ADDR = 0x56
    SENSOR_DEV_ADDR = 0x4E

    CURRENT_CHANNEL = 'CURR'
    CURRENT_GAIN = 7.6
    CURRENT_SAMPLE_RESISTOR = 0.2  # 'ohm'

    VOLTAGE_CHANNEL = 'VOLT'
    VOLTAGE_GAIN = 8.2

    ALL_CHANNEL = 'ALL'
    DEFAULT_SAMPLING_RATE = 1000
    SWITCH_DELAY_S = 0.001

    CHANNEL_CONFIG = {
        CURRENT_CHANNEL: {
            'adc_channel': 0
        },
        VOLTAGE_CHANNEL: {
            'adc_channel': 1
        },
        ALL_CHANNEL: {
            'adc_channel': 'all'
        },
    }

    AD7177_REG_SIZE = 256
    MIX_DAQT1_REG_SIZE = 65535
    AD7177_MVREF = 2500.0  # mv
    AD7177_CODE_POLAR = "bipolar"
    AD7177_BUFFER_FLAG = "enable"
    AD7177_REFERENCE_SOURCE = "extern"
    AD7177_CLOCK = "crystal"
    TAG_BASE_PIN = 4
    GPIO_OUTPUT_DIR = "output"
    DEFAULT_TAG = 0


class CloakException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class CloakBase(MIXBoard):
    '''
    Base class of Cloak and CloakCompatible.

    Providing common Cloak methods.

    Args:
        i2c:                instance(I2C), If not given, PLI2CBus emulator will be created.
        ad717x:             instance(ADC)/None, default None, If not given, PLI2CBus emulator will be created.
        ipcore:             instance(MIXDAQT1)/None, default None, If daqt1 given, then use MIXDAQT1's AD717x
        eeprom_dev_addr:    int, Eeprom device address.
        sensor_dev_addr:    int, NCT75 device address.

    Raise:
        CloakException:  Not allowed to use both aggregated IP and AD717X.

    '''

    rpc_public_api = ['module_init', 'get_sampling_rate', 'voltage_measure', 'multi_points_voltage_measure',
                      'current_measure', 'multi_points_current_measure', 'multi_points_measure_enable',
                      'multi_points_measure_disable'] + MIXBoard.rpc_public_api

    def __init__(self, i2c, ad717x=None, ipcore=None,
                 eeprom_dev_addr=CloakDef.EEPROM_DEV_ADDR, sensor_dev_addr=CloakDef.SENSOR_DEV_ADDR,
                 cal_info=None, range_table=None):

        if ipcore and ad717x:
            raise CloakException('Not allowed to use both aggregated IP and AD717X')
        if i2c:
            self.eeprom = CAT24C32(eeprom_dev_addr, i2c)
            self.sensor = NCT75(sensor_dev_addr, i2c)
        else:
            self.eeprom = EepromEmulator('eeprom_emulator')
            self.sensor = NCT75Emulator('nct75_emulator')

        if ipcore:
            self.ipcore = ipcore
            self.ad717x = self.ipcore.ad717x
        elif ad717x:
            self.ad717x = ad717x
        else:
            raise CloakException('Use one of aggregated IP or AD717X')

        super(CloakBase, self).__init__(self.eeprom, self.sensor, cal_table=cal_info,
                                        range_table=range_table)

    def module_init(self):
        '''
        Configure GPIO pin default direction.

        This needs to be outside of __init__();
        Because when GPIO expander is behind an i2c-mux, set_dir() will fail unless
        i2c-mux channel is set, and setting channel is an external action beyond module.
        See example below for usage.

        Returns:
            string, "done", api execution successful.

        Examples:
            # GPIO expander directly connected to xavier, not behind i2c-mux:
            cloak = Cloak(...)
            cloak.module_init()

            # GPIO expander is connected to downstream port of i2c-mux:
            cloak = Cloak(...)
            # some i2c_mux action
            ...
            cloak.module_init()

        '''
        self.ad717x.channel_init()
        self.set_sampling_rate('CURR', CloakDef.DEFAULT_SAMPLING_RATE)
        self.set_sampling_rate('VOLT', CloakDef.DEFAULT_SAMPLING_RATE)
        self.load_calibration()

        return 'done'

    def _check_channel(self, channel):
        '''
        Check the channel if it is valid.

        Args:
            channel:    string, ['CURR', 'VOLT', 'ALL'], the channel to check.

        Returns:
            string, ['CURR', 'VOLT', 'ALL'], the channel in specific format.

        Raise:
            CloakException:      If channel is invalid, exception will be raised.

        '''
        for ch in CloakDef.CHANNEL_CONFIG:
            if channel.lower() == ch.lower():
                return ch
        raise CloakException("channel {} is invalid".format(channel))

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        Cloak set sampling rate.

        AD717x output rate: 5 SPS to 10 kSPS.
        Note that sampling rate is not discontinuous, all support sampling
        rate can be found in ad717x datasheet.

        Args:
            channel:        string, ['CURR', 'VOLT'].
            sampling_rate:  int, [5~10000], Adc measure sampling rate, which is not continuous,
                                            please refer to ad717x datasheet.

        '''
        ch = channel.upper()
        assert ch in ['CURR', 'VOLT']

        if sampling_rate != self.get_sampling_rate(channel):
            self.ad717x.set_sampling_rate(CloakDef.CHANNEL_CONFIG[ch]['adc_channel'], sampling_rate)

    def get_sampling_rate(self, channel):
        '''
        Cloak get sampling rate of adc.

        Args:
            channel:  string, ['CURR', 'VOLT'].

        Returns:
            int, value, unit sps.

        '''
        ch = channel.upper()
        assert ch in ['CURR', 'VOLT']

        return self.ad717x.get_sampling_rate(CloakDef.CHANNEL_CONFIG[ch]['adc_channel'])

    def voltage_measure(self, sampling_rate=CloakDef.DEFAULT_SAMPLING_RATE):
        '''
        Cloak measure voltage once

        Args:
            sampling_rate:  float, [5~10000], not continuous, default 1000,
                                              please refer to ad717x datasheet.

        Returns:
            list, [value, "mV"], voltage value and unit.

        '''
        channel = CloakDef.CHANNEL_CONFIG['VOLT']['adc_channel']

        # Set sampling_rate
        self.set_sampling_rate(CloakDef.VOLTAGE_CHANNEL, sampling_rate)

        voltage = self.ad717x.read_volt(channel)

        voltage /= CloakDef.VOLTAGE_GAIN
        voltage = self.calibrate('VOLT_AVG', voltage)

        return [voltage, 'mV']

    def multi_points_voltage_measure(self, count):
        '''
        Cloak measure voltage in continuous mode.

        Before call this function, continuous votlage measure should have been started.

        Args:
            count:    int, [1~512], sampling numbers.

        Returns:
            dict, {"rms": (value, 'mVrms'), "voltage": (value, 'mV'), "max": (value, 'mV'), "min": (value, 'mV')}.
                  rms, max and min voltage with unit.
        '''
        assert isinstance(count, int) and count > 0 and count <= 512

        channel = CloakDef.CHANNEL_CONFIG['VOLT']['adc_channel']

        adc_volt_data_list = self.ad717x.get_continuous_sampling_voltage(channel, count)

        min_data = min(adc_volt_data_list)
        max_data = max(adc_volt_data_list)
        sum_Data = sum(adc_volt_data_list)
        avg_data = sum_Data / len(adc_volt_data_list)
        suqare_sum_data = sum([x**2 for x in adc_volt_data_list])
        rms_data = math.sqrt(suqare_sum_data / len(adc_volt_data_list))

        # mVrms
        rms_voltage = rms_data / CloakDef.VOLTAGE_GAIN
        # mV
        avg_voltage = avg_data / CloakDef.VOLTAGE_GAIN
        max_voltage = max_data / CloakDef.VOLTAGE_GAIN
        min_voltage = min_data / CloakDef.VOLTAGE_GAIN

        rms_voltage = self.calibrate('VOLT_RMS', rms_voltage)
        avg_voltage = self.calibrate('VOLT_AVG', avg_voltage)

        result = dict()
        result['rms'] = (rms_voltage, 'mVrms')
        result['voltage'] = (avg_voltage, 'mV')
        result['max'] = (max_voltage, 'mV')
        result['min'] = (min_voltage, 'mV')

        return result

    def current_measure(self, sampling_rate=CloakDef.DEFAULT_SAMPLING_RATE):
        '''
        Cloak measure current once.

        Args:
            sampling_rate:  int, [5~10000], default 1000, please refer to ad717x datasheet.

        Returns:
            list, [value, 'mA'],  current value and unit.

        '''
        channel = CloakDef.CHANNEL_CONFIG['CURR']['adc_channel']

        # Set sampling_rate
        self.set_sampling_rate(CloakDef.CURRENT_CHANNEL, sampling_rate)
        volt = self.ad717x.read_volt(channel)

        current = (volt / CloakDef.CURRENT_GAIN) / CloakDef.CURRENT_SAMPLE_RESISTOR
        current = self.calibrate('CURR_AVG', current)

        return [current, 'mA']

    def multi_points_current_measure(self, count):
        '''
        Cloak measure current in continuous mode.

        Before call this function, continuous current measure must be started first.

        Args:
            count:    int, [1~512], sampling numbers.

        Returns:
            dict, {"rms": (value, 'mArms'), "current": (value, 'mA'),, "max": (value, 'mA'),, "min": (value, 'mA')},
                  rms, max and min current with unit.

        '''
        assert isinstance(count, int) and count > 0 and count <= 512

        channel = CloakDef.CHANNEL_CONFIG['CURR']['adc_channel']

        adc_volt_data_list = self.ad717x.get_continuous_sampling_voltage(channel, count)

        min_data = min(adc_volt_data_list)
        max_data = max(adc_volt_data_list)
        sum_Data = sum(adc_volt_data_list)
        avg_data = sum_Data / len(adc_volt_data_list)
        suqare_sum_data = sum([x**2 for x in adc_volt_data_list])
        rms_data = math.sqrt(suqare_sum_data / len(adc_volt_data_list))

        # mArms
        rms_current = (rms_data / CloakDef.CURRENT_GAIN) / CloakDef.CURRENT_SAMPLE_RESISTOR
        # mA
        avg_current = (avg_data / CloakDef.CURRENT_GAIN) / CloakDef.CURRENT_SAMPLE_RESISTOR
        max_current = (max_data / CloakDef.CURRENT_GAIN) / CloakDef.CURRENT_SAMPLE_RESISTOR
        min_current = (min_data / CloakDef.CURRENT_GAIN) / CloakDef.CURRENT_SAMPLE_RESISTOR

        avg_current = self.calibrate('CURR_AVG', avg_current)

        result = dict()
        result['rms'] = (rms_current, 'mArms')
        result['current'] = (avg_current, 'mA')
        result['max'] = (max_current, 'mA')
        result['min'] = (min_current, 'mA')

        return result

    def multi_points_measure_enable(self, channel, sampling_rate=CloakDef.DEFAULT_SAMPLING_RATE, samples=1):
        '''
        Cloak start continuous measure.

        Note that sampling rate is not discontinuous, all support sampling
        rate can be found in ad717x datasheet.

        Args:
            channel:         string, ['CURR', 'VOLT', 'ALL'], the specific channel to enable continuous measure mode.
            sampling_rate:   float, [5~10000], default 1000, please refer to ad717x datasheet.
            samples:         int, default 1.

        Returns:
            string, "done", api execution successful.

        '''
        channel = self._check_channel(channel)
        assert 5 <= sampling_rate <= 10000

        self.multi_points_measure_disable(channel)
        time.sleep(CloakDef.SWITCH_DELAY_S)
        self.ad717x.enable_continuous_sampling(CloakDef.CHANNEL_CONFIG[channel]['adc_channel'],
                                               sampling_rate, samples)
        return "done"

    def multi_points_measure_disable(self, channel):
        '''
        Cloak stop continuous measure.

        Args:
            channel:    string, ['CURR', 'VOLT', 'ALL'], the specific channel to enable continuous measure mode.

        Returns:
            string, "done", api execution successful.

        '''
        channel = self._check_channel(channel)

        self.ad717x.disable_continuous_sampling(CloakDef.CHANNEL_CONFIG[channel]['adc_channel'])
        return "done"


class Cloak(CloakBase):
    '''
    This class is legacy driver for normal boot.

    compatible = ["GQQ-SCP002005-000"]

    Cloak(SCOPE-002) Module is used for high precision voltage (DC) and current (DC)
    measurement, simultaneously and continuously data recording, the raw data can be
    uploaded to PC real time through Ethernet. The module shall work together with integrated
    control unit (ICU), which could achieve high-precision, automatic measurement.
    Current Input Channel: 10uA ~ 1.5A
    Voltage Input Channel: -250mV ~ +250mV

    Args:
        i2c:        instance(I2C), If not given, PLI2CBus emulator will be created.
        ad7177:     instance(ADC),   If not given, PLI2CBus emulator will be created.
        ipcore:     instance(MIXDAQT1), If daqt1 given, then use MIXDAQT1's AD7177.

    Examples:
        If the params `ipcore` is valid, then use MIXDAQT1 aggregated IP;
        Otherwise, if the params `ad7177`, use non-aggregated IP.

        # use MIXDAQT1 aggregated IP
        i2c = PLI2CBus('/dev/MIX_I2C_0')
        ip_daqt1 = MIXDAQT1('/dev/MIX_DAQT1_0', ad717x_chip='AD7177', ad717x_mvref=2500,
                 use_spi=False, use_gpio=False)
        cloak = Cloak(i2c=i2c,
                      ad7177=None,
                      ipcore=ip_daqt1)
        # use non-aggregated IP
        ad7177 = PLAD7177('/dev/MIX_AD717x_0', 2500)
        i2c = PLI2CBus('/dev/MIX_I2C_1')
        cloak = Cloak(i2c=i2c,
                      ad7177=ad7177,
                      ipcore=None)

        # Cloak measure voltage once
        cloak.multi_points_measure_disable('VOLT')
        volt = cloak.voltage_measure()
        print(volt)
        # terminal show "[xx, 'mV']"

        # Cloak measure voltage in continuous mode
        cloak.multi_points_measure_enable('VOLT', 1000)
        result = cloak.multi_points_voltage_measure(10)
        print(result)
        # terminal show "{'rms': (xx, 'mVrms'), 'min': (xx, 'mV'),
                'voltage': (xx, 'mV'), 'max': (xx, 'mV')}"

        # Cloak measure current once
        cloak.multi_points_measure_disable('CURR')
        current = cloak.current_measure()
        print(current)
        # terminal show "[xx, 'mA']"

        # Cloak measure current in continuous mode
        cloak.multi_points_measure_enable('CURR', 1000)
        result = cloak.multi_points_current_measure(10)
        print(result)
        # terminal show "{'current': (xx, 'mA'), 'rms': (xx, 'mArms'),
                'min': (xx, 'mA'), 'max': (xx, 'mA')}"

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-SCP002005-000"]

    rpc_public_api = ['datalogger_start', 'datalogger_end'] + CloakBase.rpc_public_api

    def __init__(self, i2c, ad7177=None, ipcore=None):
        if ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, CloakDef.MIX_DAQT1_REG_SIZE)
                ipcore = MIXDAQT1SGR(axi4_bus, 'AD7177', ad717x_mvref=CloakDef.AD7177_MVREF,
                                     code_polar=CloakDef.AD7177_CODE_POLAR,
                                     reference=CloakDef.AD7177_REFERENCE_SOURCE,
                                     buffer_flag=CloakDef.AD7177_BUFFER_FLAG,
                                     clock=CloakDef.AD7177_CLOCK,
                                     use_spi=False, use_gpio=True)
            self.gpio = ipcore.gpio
            self.tag_pins = [Pin(self.gpio, CloakDef.TAG_BASE_PIN + x,
                                 CloakDef.GPIO_OUTPUT_DIR) for x in xrange(4)]
        elif ad7177:
            if isinstance(ad7177, basestring):
                axi4_bus = AXI4LiteBus(ad7177, CloakDef.AD7177_REG_SIZE)
                ad7177 = MIXAd7177SG(axi4_bus, mvref=CloakDef.AD7177_MVREF,
                                     code_polar=CloakDef.AD7177_CODE_POLAR,
                                     reference=CloakDef.AD7177_REFERENCE_SOURCE,
                                     buffer_flag=CloakDef.AD7177_BUFFER_FLAG,
                                     clock=CloakDef.AD7177_CLOCK)
        else:
            ad7177 = MIXAd7177SGEmulator('mix_ad7177_sg_emulator', 2500)

        super(Cloak, self).__init__(i2c, ad7177, ipcore,
                                    CloakDef.EEPROM_DEV_ADDR,
                                    CloakDef.SENSOR_DEV_ADDR,
                                    cloak_calibration_info,
                                    cloak_range_table)

    def datalogger_start(self, tag=CloakDef.DEFAULT_TAG):
        '''
        Cloak set tag value for upload data.

        Args:
            tag:    int, [0x0~0xf], the value is upper 4 bits are valid, default is 0x0.

        Returns:
            string, "done", api execution successful.

        Examples:
            cloak.datalogger_start()

        '''
        assert 0x0 <= tag <= 0xf

        for i in xrange(4):
            self.tag_pins[i].set_level((tag >> i) & 0x1)

        return 'done'

    def datalogger_end(self):
        '''
        Cloak clear tag value for upload data.

        Returns:
            string, "done", api execution successful.

        Examples:
            cloak.datalogger_end()

        '''
        for i in xrange(4):
            self.tag_pins[i].set_level(0)

        return 'done'
