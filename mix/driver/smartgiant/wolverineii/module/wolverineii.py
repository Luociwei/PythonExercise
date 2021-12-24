# -*- coding: utf-8 -*-
import functools
import math
import time
import struct
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.smartgiant.common.module.mix_board import BoardArgCheckError
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator
from mix.driver.smartgiant.common.ic.pca9536 import PCA9536
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ic.pca9536_emulator import PCA9536 as PCA9536Emulator
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR

__author__ = 'zicheng.huang@SmartGiant'
__version__ = '0.1'


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
    '5V_CH1': {
        'coefficient':
        1.0 / (WolverineiiCoeffDef.VOLT_2_REAL_GAIN1),
        'unit': 'mV',
        'bits': [(0, 0), (1, 0)],
        'channel': 'A'
    },
    '5V_CH2': {
            'coefficient':
            1.0 / (WolverineiiCoeffDef.VOLT_2_REAL_GAIN1),
            'unit': 'mV',
            'bits': [(0, 0), (1, 0)],
            'channel': 'B'
    },
    '100uA': {
            'coefficient':
            1.0 / (WolverineiiCoeffDef.RES_LOAD_210ohm * WolverineiiCoeffDef.VOLT_2_REAL_GAIN2),
            'unit': 'mA',
            'bits': [(0, 1), (1, 1)],
            'channel': 'B'
    },
    '2mA': {
            'coefficient':
            1.0 / (WolverineiiCoeffDef.RES_LOAD_10ohm * WolverineiiCoeffDef.VOLT_2_REAL_GAIN2),
            'unit': 'mA',
            'bits': [(0, 0), (1, 1)],
            'channel': 'B'
    }
}

wolverineii_calibration_info = {
    '5V_CH1': {
        'level1': {'unit_index': 0, 'limit': (-1000, 'mV')},
        'level2': {'unit_index': 1, 'limit': (-100, 'mV')},
        'level3': {'unit_index': 2, 'limit': (-10, 'mV')},
        'level4': {'unit_index': 3, 'limit': (0, 'mV')},
        'level5': {'unit_index': 4, 'limit': (10, 'mV')},
        'level6': {'unit_index': 5, 'limit': (100, 'mV')},
        'level7': {'unit_index': 6, 'limit': (1000, 'mV')},
        'level8': {'unit_index': 7, 'limit': (6000, 'mV')}
    },
    '5V_CH2': {
        'level1': {'unit_index': 8, 'limit': (-1000, 'mV')},
        'level2': {'unit_index': 9, 'limit': (-100, 'mV')},
        'level3': {'unit_index': 10, 'limit': (-10, 'mV')},
        'level4': {'unit_index': 11, 'limit': (0, 'mV')},
        'level5': {'unit_index': 12, 'limit': (10, 'mV')},
        'level6': {'unit_index': 13, 'limit': (100, 'mV')},
        'level7': {'unit_index': 14, 'limit': (1000, 'mV')},
        'level8': {'unit_index': 15, 'limit': (6000, 'mV')}
    },

    '5V_CH1_avg_volt': {
        'level1': {'unit_index': 16, 'limit': (6000, 'mV')}
    },
    '5V_CH2_avg_volt': {
        'level1': {'unit_index': 17, 'limit': (6000, 'mV')}
    },

    '5V_CH1_rms_volt': {
        'level1': {'unit_index': 18, 'limit': (6000, 'mV')}
    },
    '5V_CH2_rms_volt': {
        'level1': {'unit_index': 19, 'limit': (6000, 'mV')}
    },

    '100uA': {
        'level1': {'unit_index': 20, 'limit': (-0.01, 'mA')},
        'level2': {'unit_index': 21, 'limit': (0, 'mA')},
        'level3': {'unit_index': 22, 'limit': (0.01, 'mA')},
        'level4': {'unit_index': 23, 'limit': (0.12, 'mA')}
    },
    '2mA': {
        'level1': {'unit_index': 24, 'limit': (-1, 'mA')},
        'level2': {'unit_index': 25, 'limit': (0.09, 'mA')},
        'level3': {'unit_index': 26, 'limit': (1, 'mA')},
        'level4': {'unit_index': 27, 'limit': (2.5, 'mA')}
    }
}

wolverineii_range_table = {
    "5V_CH1": 0,
    "5V_CH2": 1,
    "5V_CH1_avg_volt": 2,
    "5V_CH2_avg_volt": 3,
    "5V_CH1_rms_volt": 4,
    "5V_CH2_rms_volt": 5,
    "100uA": 6,
    "2mA": 7
}


class WolverineiiDef:

    ADC_A_CHANNEL = 'A'
    ADC_B_CHANNEL = 'B'

    DCV_5V_CH1_RANGE = "5V_CH1"
    DCV_5V_CH2_RANGE = "5V_CH2"
    VOLTAGE_RANGE_LIST = (DCV_5V_CH1_RANGE, DCV_5V_CH2_RANGE)

    ACV_5V_CH1_AVG_VOLTAGE = "5V_CH1_avg_volt"
    ACV_5V_CH2_AVG_VOLTAGE = "5V_CH2_avg_volt"
    ACV_5V_CH1_RMS_VOLTAGE = "5V_CH1_rms_volt"
    ACV_5V_CH2_RMS_VOLTAGE = "5V_CH2_rms_volt"

    DCI_2mA_RANGE = "2mA"
    DCI_100uA_RANGE = "100uA"
    CURRENT_RANGE_LIST = (DCI_2mA_RANGE, DCI_100uA_RANGE)
    SWITCH_DELAY_S = 0.001
    RELAY_DELAY_S = 0.005
    DEFAULT_SAMPLE_RATE = 5
    SELECT_RANGE_KEY = 'range'
    UPLOAD_TIME = 1
    DEFAULT_RANGE = '5V_CH1'

    AD7175_MVREF = 5000
    AD7175_CODE_POLAR = 'bipolar'
    AD7175_REFERENCE = 'extern'
    AD7175_CLOCK = 'crystal'
    MIXDAQT1_REG_SIZE = 65536
    EMULATOR_REG_SIZE = 256
    ADC_CHANNEL_LIST = {'A': 0, 'B': 1}

    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    IO_EXP_DEV_ADDR = 0x41


class WolverineiiException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class WolverineII(MIXBoard):
    '''
    Wolverineii is a compact version of the digital multimeter which internal ADC resolution is 24 bit.

    compatible = ['GQQ-DMM002001-000']

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

        Example for measuring voltage:
            result = wolverineii.voltage_measure('5V_CH1', 5)
            print("voltage={}, unit={}".format(result[0], result[1]))

            result = wolverineii.multi_points_voltage_measure(100, '5V_CH1', 5)
            print("average={}, max={}, min={}, rms={}".format(result['average'], result['max'],
            result['min'], result['rms']))

        Example for measuring current:
            result = wolverineii.current_measure('2mA', 5)
            print("current={}, unit={}".format(result[0], result[1]))

            result = wolverineii.multi_points_current_measure(100, '2mA', 5)
            print("average={}, max={}, min={}, rms={}".format(result['average'], result['max'],
            result['min'], result['rms']))

    '''

    compatible = ['GQQ-DMM002001-000']

    rpc_public_api = ['get_sampling_rate', 'get_measure_path',
                      'voltage_measure',
                      'multi_points_voltage_measure', 'current_measure',
                      'multi_points_current_measure'] + MIXBoard.rpc_public_api

    def __init__(self, i2c, ipcore=None):

        if i2c:
            self.eeprom = CAT24C32(WolverineiiDef.EEPROM_DEV_ADDR, i2c)
            self.sensor = NCT75(WolverineiiDef.SENSOR_DEV_ADDR, i2c)
            self.pca9536 = PCA9536(WolverineiiDef.IO_EXP_DEV_ADDR, i2c)
        else:
            self.eeprom = EepromEmulator('eeprom_emulator')
            self.sensor = NCT75Emulator('nct75_emulator')
            self.pca9536 = PCA9536Emulator('pca9536_emulator')
        if ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, WolverineiiDef.MIXDAQT1_REG_SIZE)
                ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=WolverineiiDef.AD7175_MVREF,
                                     code_polar=WolverineiiDef.AD7175_CODE_POLAR,
                                     reference=WolverineiiDef.AD7175_REFERENCE,
                                     clock=WolverineiiDef.AD7175_CLOCK)
                self.ipcore = ipcore
            else:
                self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x
            self.ad7175.config = {
                'ch0': {'P': 'AIN0', 'N': 'AIN1'},
                'ch1': {'P': 'AIN2', 'N': 'AIN3'}
            }
        else:
            self.ad7175 = MIXAd7175SGEmulator(
                'mix_ad7175_sg_emulator', WolverineiiDef.EMULATOR_REG_SIZE)

        self.mode = 'cal'
        self.measure_path = dict()

        super(WolverineII, self).__init__(self.eeprom, self.sensor,
                                          cal_table=wolverineii_calibration_info,
                                          range_table=wolverineii_range_table)

    def post_power_on_init(self, timeout_s):
        '''
        Init Wolverineii module to a know harware state.

        This function will set pca9536 io direction to output and set default range to '5V'

        Args:
            timeout_s:      float, unit Second, execute timeout

        Returns:
            string, "done", api execution successful.

        '''
        self.reset(timeout_s)
        self.load_calibration()
        return 'done'

    def reset(self, timeout_s):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout_s:      float, unit Second, execute timeout.

        Returns:
            string, "done", if no error, "done" will be returned
        '''
        self.pca9536.set_pins_dir([0x00])
        self.pca9536.set_ports([0x00])
        self.ad7175.channel_init()
        self.set_measure_path(WolverineiiDef.DEFAULT_RANGE)
        self.set_sampling_rate('A', WolverineiiDef.DEFAULT_SAMPLE_RATE)
        self.set_sampling_rate('B', WolverineiiDef.DEFAULT_SAMPLE_RATE)
        return "done"

    def get_driver_version(self):
        '''
        Get wolverine II driver version.

        Returns:
            string, current driver version.
        '''
        return __version__
        # really the pythonic way is to make version a read-only property.
        # However that doesn't travel well across the wire in RPC.
        # Also this seems to be the only way for property to pick up
        # functions defined in derived classes.
    driver_version = property(fget=lambda self: self.get_driver_version())

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        Wolverineii set sampling rate.

        Note that sampling rate is not discontinuous, all support sampling
        rate can be found in ad7175 datasheet.

        Args:
            channel:            string, ['A', 'B'], the channel to change sampling rate,
                                                    channel 'A' only can input voltage through VIN_P1&VIN_N.
                                                    channel 'B' can input voltage through VIN_P2&VIN_N
                                                    or current through CUR_P&CUR_N.
            sampling_rate:      float, [5~250000], adc measure sampling rate, which is not continuous,
                                                   please refer to ad7175 datasheet.

        Returns:
            string, "done", api execution successful.

        Examples:
            wolverineii.set_sampling_rate('A', 50000)

        '''
        assert channel in WolverineiiDef.ADC_CHANNEL_LIST.keys()
        assert 5 <= sampling_rate <= 250000

        if sampling_rate != self.get_sampling_rate(channel):
            self.ad7175.set_sampling_rate(WolverineiiDef.ADC_CHANNEL_LIST[channel], sampling_rate)

    def get_sampling_rate(self, channel):
        '''
        Wolverineii get sampling rate of adc

        Args:
            channel:    string, ['A', 'B'],  the channel to get sampling rate.

        Returns:
            int, value, current module sampling rate.

        Examples:
            sampling_rate = wolverineii.get_sampling_rate('A')
            print(sampling_rate)

        '''
        assert channel in WolverineiiDef.ADC_CHANNEL_LIST.keys()

        return self.ad7175.get_sampling_rate(WolverineiiDef.ADC_CHANNEL_LIST[channel])

    def _volt_to_target_unit(self, sel_range, volt):
        '''
        Wolverineii get target unit value (wolverineii_function_info) from measured voltage

        Args:
            sel_range:  string, ['100uA', '2mA', '5V_CH1', '5V_CH2'], the range of channel measure.
            volt:       float, the measured voltage by ad7175.

        Returns:
            float, value.

        '''
        assert sel_range in wolverineii_function_info.keys()

        return volt * wolverineii_function_info[sel_range]['coefficient']

    def set_measure_path(self, sel_range, delay_time=WolverineiiDef.RELAY_DELAY_S):
        '''
        Wolverineii set measure path.

        Args:
            sel_range:   string, ['100uA', '2mA', '5V_CH1', '5V_CH2'], set range for different channel.
            delay_time:  float, set the bit delay time.

        Returns:
            string, "done", api execution successful.

        Examples:
            wolverineii.set_measure_path('5V_CH1')

        '''
        assert sel_range in wolverineii_function_info.keys()

        if sel_range != self.get_measure_path().get(WolverineiiDef.SELECT_RANGE_KEY, ''):
            bits = wolverineii_function_info[sel_range]['bits']
            for bit in bits:
                self.pca9536.set_pin(bit[0], bit[1])

            time.sleep(delay_time)

        self.measure_path.clear()
        self.measure_path[WolverineiiDef.SELECT_RANGE_KEY] = sel_range

        return "done"

    def get_measure_path(self):
        '''
        Wolverineii get measure path.

        Returns:
            dict, current channel and range.

        Examples:
            path = wolverineii.get_measure_path()
            print(path)

        '''
        return self.measure_path

    def single_measure(self, sampling_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverineii measure voltage/current once

        Args:
            sampling_rate:     float, [5~250000], default 5, not continuous please refer to ad7175 datasheet.

        Returns:
            list, [value, unit].

        Examples:
            target = wolverineii.single_measure(5)

        '''
        measure_path = self.get_measure_path()

        adc_channel = WolverineiiDef.ADC_CHANNEL_LIST['A'] if \
            measure_path['range'] == '5V_CH1' else \
            WolverineiiDef.ADC_CHANNEL_LIST['B']

        # Set sampling rate
        self.set_sampling_rate(wolverineii_function_info[measure_path['range']]['channel'], sampling_rate)

        voltage = self.ad7175.read_volt(adc_channel)
        target_value = self._volt_to_target_unit(measure_path['range'], voltage)
        unit = wolverineii_function_info[measure_path['range']]['unit']

        cal_infor = measure_path['range']
        target_value = self.calibrate(cal_infor, target_value)

        return [target_value, unit]

    def continuous_sample(self, count, sampling_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverineii get measure data in continuous mode and return list of data without any calculation

        station sw could do further analysis base on raw data returned.

        Args:
            count:          int, [1~512], count of voltage/current data points
                                          to get in continuous mode; from FPGA internal buffer not from DMA.
            sampling_rate:  float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.

        Returns:
            list, [[xxx,xxx,...], unit].

        Examples:
            result = wolverineii.continuous_sample(100)
            print(result)

        '''
        assert isinstance(count, int) and count >= 1

        measure_path = self.get_measure_path()

        if measure_path == {}:
            raise WolverineiiException('error continuous measure channel')

        measure_scope = measure_path['range']

        adc_channel = WolverineiiDef.ADC_CHANNEL_LIST[wolverineii_function_info[measure_scope]['channel']]

        self.ad7175.disable_continuous_sampling(adc_channel)
        time.sleep(WolverineiiDef.SWITCH_DELAY_S)

        self.ad7175.enable_continuous_sampling(adc_channel, sampling_rate)

        unit = wolverineii_function_info[measure_scope]['unit']
        target_data = []
        try:
            adc_volt = self.ad7175.get_continuous_sampling_voltage(adc_channel, count)
        except Exception:
            raise
        else:
            cal_infor = measure_scope
            calibrate = functools.partial(self.calibrate, cal_infor)
            adc_volt = map(calibrate, adc_volt)

            volt_to_target_unit = functools.partial(self._volt_to_target_unit, measure_scope)
            target_data = [map(volt_to_target_unit, adc_volt), unit]

        finally:
            self.ad7175.disable_continuous_sampling(adc_channel)

        return target_data

    def _continuous_sample(self, count, sampling_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverineii get measure data in continuous mode and return list of data without any calculation

        station sw could do further analysis base on raw data returned.

        Args:
            count:          int, [0~512], count of voltage/current data points
                                          to get in continuous mode; from FPGA internal buffer not from DMA.
            sampling_rate:  float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.

        Returns:
            list, [[xxx,xxx,...], unit].

        Examples:
            result = wolverineii._continuous_sample(100)
            print(result)

        '''
        assert isinstance(count, int) and count >= 1

        measure_path = self.get_measure_path()

        if measure_path == {}:
            raise WolverineiiException('error continuous measure channel')

        measure_scope = measure_path['range']

        adc_channel = WolverineiiDef.ADC_CHANNEL_LIST[wolverineii_function_info[measure_scope]['channel']]

        self.ad7175.disable_continuous_sampling(adc_channel)
        time.sleep(WolverineiiDef.SWITCH_DELAY_S)

        self.ad7175.enable_continuous_sampling(adc_channel, sampling_rate)

        unit = wolverineii_function_info[measure_scope]['unit']
        target_data = []
        try:
            adc_volt = self.ad7175.get_continuous_sampling_voltage(adc_channel, count)
        except Exception:
            raise
        else:
            volt_to_target_unit = functools.partial(self._volt_to_target_unit, measure_scope)
            target_data = [map(volt_to_target_unit, adc_volt), unit]

        finally:
            self.ad7175.disable_continuous_sampling(adc_channel)

        return target_data

    def multi_points_measure(self, count, sel_range, sampling_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE,
                             upload_time=WolverineiiDef.UPLOAD_TIME):
        '''
        Wolverineii measure voltage/current in continuous mode

        Args:
            count:         int, [1~512], Get count voltage/current in continuous mode.
            sel_range:     string, ['5V_CH1', '5V_CH2', '100uA', '2mA'], select channel to measure.
            sampling_rate: float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.
            upload_time:   int, default 1,set the upload time.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
            result = wolverineii.multi_points_measure(100, '5V_CH1', 200)
            print(result)

        '''
        assert isinstance(count, int) and count >= 1
        assert sel_range in wolverineii_function_info.keys()
        assert 5 <= sampling_rate <= 250000

        # Select measure range
        self.set_measure_path(sel_range)

        target_data = self._continuous_sample(count, sampling_rate)
        min_data = min(target_data[0])
        max_data = max(target_data[0])
        sum_Data = sum(target_data[0])
        avg_data = sum_Data / len(target_data[0])
        square_sum_data = sum([x**2 for x in target_data[0]])
        rms_data = math.sqrt(square_sum_data / len(target_data[0]))

        if wolverineii_function_info[sel_range]['channel'] == 'A':
            rms_data = self.calibrate('5V_CH1_rms_volt', rms_data)
            avg_data = self.calibrate('5V_CH1_avg_volt', avg_data)
        else:
            rms_data = self.calibrate('5V_CH2_rms_volt', rms_data)
            avg_data = self.calibrate('5V_CH2_avg_volt', avg_data)

        unit = target_data[1]
        result = dict()
        result['rms'] = (rms_data, unit + 'rms')
        result['avg'] = (avg_data, unit)
        result['max'] = (max_data, unit)
        result['min'] = (min_data, unit)

        return result

    def voltage_measure(self, volt_range, sampling_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverineii measure voltage once

        Args:
            volt_range:     string, ['5V_CH1', '5V_CH2'], select channel to measure.
            sampling_rate:  float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.

        Returns:
            list, [value, unit], voltage value and unit.

        Examples:
            volt = wolverineii.voltage_measure('5V_CH2')
            print(volt)

        '''
        assert 5 <= sampling_rate <= 250000

        if volt_range not in WolverineiiDef.VOLTAGE_RANGE_LIST:
            raise WolverineiiException("error voltage scope")

        # Select measure range
        self.set_measure_path(volt_range)

        return self.single_measure(sampling_rate)

    def multi_points_voltage_measure(self, count, volt_range,
                                     sampling_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverineii measure voltage in continuous mode

        Args:
            count:          int, [1~512], Get count voltage in continuous mode.
            volt_range:     string, ['5V_CH1', '5V_CH2'], measure range string.
            sampling_rate:  float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
            voltage = wolverineii.multi_points_voltage_measure(100, '5V_CH1')
            print(voltage)

        '''
        assert isinstance(count, int) and count >= 1
        assert 5 <= sampling_rate <= 250000

        if volt_range not in WolverineiiDef.VOLTAGE_RANGE_LIST:
            raise WolverineiiException("error voltage scope")

        return self.multi_points_measure(count, volt_range, sampling_rate)

    def current_measure(self, curr_range,
                        sampling_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverineii measure current once

        Args:
            curr_range:     string, ['2mA', '100uA'],  measure range string.
            sampling_rate:  float, [5~250000], default 5, not continuous,please refer to ad7175 datasheet.

        Returns:
            list, [value, unit], current value and unit, eg:[value, unit].

        Examples:
            current = wolverineii.current_measure('2mA')
            print(current)

        '''
        assert 5 <= sampling_rate <= 250000

        if curr_range not in WolverineiiDef.CURRENT_RANGE_LIST:
            raise WolverineiiException("error voltage scope")

        # Select measure range
        self.set_measure_path(curr_range)

        return self.single_measure(sampling_rate)

    def multi_points_current_measure(self, count, curr_range,
                                     sampling_rate=WolverineiiDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverineii measure current in continuous mode

        Args:
            count:           int, [1~512], number current value to be get.
            curr_range:      string, ['2mA', '100uA'], measure range string.
            sampling_rate:   float, [5~250000], default 5, not continuous,please refer to ad7175 datasheet.

        Returns:
            dict, {"rms":[value, unit], "avg":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
            current = wolverineii.multi_points_current_measure(100, '2mA')
            print(current)

        '''
        assert isinstance(count, int) and count >= 1
        assert 5 <= sampling_rate <= 250000

        if curr_range not in WolverineiiDef.CURRENT_RANGE_LIST:
            raise WolverineiiException("error current scope")

        return self.multi_points_measure(count, curr_range, sampling_rate)

    def legacy_write_calibration_cell(self, unit_index, gain, offset, threshold):
        '''
        MIXBoard calibration data write.
        Note: This function will not be used if ICI is support by module.

        Args:
            unit_index:   int,    calibration unit index.
            gain:         float,  calibration gain.
            offset:       float,  calibration offset.
            threshold:    float,  if value < threshold, use this calibration unit data.

        Returns:
            string, "done", api execution successful.

        Examples:
            board.write_calibration_cel(0, 1.1, 0.1, 100)

        Raise:
            BoardArgCheckError: unit_index data type is not int type or unit_index < 0.
            calibration unit format:
                Meaning:    Gain,     Offset,   threshold value, Use flag
                Mem size:   4Bytes,   4Bytes,   4Bytes,            Byte
                Data type:  float,    float,    float,            uint8_t
                Formula:    Y = Gain * X  + Offset

        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                'calibration unit memory unit_index data type is not int type or unit_index < 0')

        use_flag = self.calibration_info['use_flag']
        data = (gain, offset, use_flag, 0xff, 0xff, 0xff, 0xff)
        s = struct.Struct(WolverineiiCoeffDef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(WolverineiiCoeffDef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = self.calibration_info['unit_start_addr'] + \
            WolverineiiCoeffDef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)
        return 'done'

    def legacy_read_calibration_cell(self, unit_index):
        '''
        MIXBoard read calibration data
        Note: This function will not be used if ICI is support by module.

        Args:
            unit_index: int, calibration unit index.

        Returns:
            dict, {"gain": value, "offset":value, "threshold": value, "is_use": value}.

        Examples:
            data = board.read_calibration_cel(0)
            print(data)

        Raise:
            BoardArgCheckError: unit_index data type is not int type or unit_index < 0.
            calibration unit format:
                Meaning:    Gain,     Offset,   threshold value, Use flag
                Mem size:   4Bytes,   4Bytes,   4Bytes,            Byte
                Data type:  float,    float,    float,            uint8_t
                Formula:    Y = Gain * X  + Offset

        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                'calibration unit memory unit_index data type is not int type or unit_index < 0')

        address = self.calibration_info['unit_start_addr'] + \
            WolverineiiCoeffDef.CAL_DATA_LEN * unit_index
        data = self.read_eeprom(address, WolverineiiCoeffDef.READ_CAL_BYTE)

        s = struct.Struct(WolverineiiCoeffDef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(WolverineiiCoeffDef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        threshold = 0.0
        for cal_type in wolverineii_calibration_info.keys():
            for level in wolverineii_calibration_info[cal_type].keys():
                if unit_index == wolverineii_calibration_info[cal_type][level]['unit_index']:
                    threshold = wolverineii_calibration_info[cal_type][level]['limit'][0]
                    break

        if self.calibration_info['use_flag'] != result[2]:
            return {'gain': 1.0, 'offset': 0.0, 'threshold': 0, 'is_use': False}
        else:
            return {'gain': result[0], 'offset': result[1], 'threshold': threshold, 'is_use': True}

    def legacy_erase_calibration_cell(self, unit_index):
        '''
        MIXBoard erase calibration unit
        Note: This function will not be used if ICI is support by module.

        Args:
            unit_index:  int, calibration unit index.

        Returns:
            string, "done", api execution successful.

        Examples:
            board.erase_calibration_cell(1)

        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                'calibration unit memory unit_index data type is not int type or unit_index < 0')

        data = [0xff for i in range(WolverineiiCoeffDef.CAL_DATA_LEN)]
        address = self.calibration_info['unit_start_addr'] + \
            WolverineiiCoeffDef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)
        return 'done'
