# -*- coding: utf-8 -*-
import math
import time
import struct
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.tca9538_emulator import TCA9538Emulator
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.tca9538 import TCA9538
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.smartgiant.common.module.mix_board import BoardArgCheckError


__author__ = 'haite.zhuang@SmartGiant'
__version__ = '0.3'


class DMM010Def:
    '''
    DMM010Def shows the coefficient of hardware defined in the software requirements document
    '''
    ATTENUATION = (8.2 / 10.2)
    VOLTAGE_6V_GAIN = 1.0
    CURRENT_1A_GAIN = 61.567
    RESISTOR_1ohm_GAIN = 990.609
    RESISTOR_20ohm_GAIN = 61.567
    CURRENT_1A_SAMPLE_RES = 0.1    # ohm
    RESISTOR_CONSTANT_CURR = 5.0   # mA

    VOLTAGE_6V_RANGE = '6V'
    CURRENT_1A_RANGE = '1A'
    RESISTOR_1ohm_RANGE = '1OHM'
    RESISTOR_20ohm_RANGE = '20OHM'

    SWITCH_DELAY = 0.001        # s
    DEFAULT_SAMPLING_RATE = 5   # Hz
    PLAD7175_REG_SIZE = 8192
    ADC_VREF_VOLTAGE_5000mV = 5000
    ADC_A_CHANNEL = 0
    ADC_B_CHANNEL = 1
    ADC_CHANNEL_LIST = (ADC_A_CHANNEL, ADC_B_CHANNEL)

    TAC9538_I2C_ADDR = 0x70
    CAT24C32_I2C_ADDR = 0x50
    NCT75_I2C_ADDR = 0x48

    CAL_DATA_LEN = 12
    WRITE_CAL_DATA_PACK_FORMAT = "2f4B"
    WRITE_CAL_DATA_UNPACK_FORMAT = "12B"

    READ_CAL_BYTE = 12
    READ_CAL_DATA_PACK_FORMAT = "12B"
    READ_CAL_DATA_UNPACK_FORMAT = "2f4B"

    MIX_DAQT1_REG_SIZE = 65535
    AD7175_CODE_POLAR = "bipolar"
    AD7175_BUFFER_FLAG = "enable"
    AD7175_REFERENCE_SOURCE = "extern"
    AD7175_CLOCK = "crystal"


dmm010_function_info = {
    DMM010Def.VOLTAGE_6V_RANGE: {
        'coefficient':
        1.0 / (DMM010Def.VOLTAGE_6V_GAIN * DMM010Def.ATTENUATION),
        'unit': 'mV',
        'bits':
            [(0, 0), (1, 0), (2, 1), (3, 0), (4, 0), (5, 0)]
    },
    DMM010Def.CURRENT_1A_RANGE: {
        'coefficient':
        1.0 / (DMM010Def.CURRENT_1A_SAMPLE_RES * DMM010Def.CURRENT_1A_GAIN *
               DMM010Def.ATTENUATION),
        'unit': 'mA',
        'bits':
            [(0, 0), (1, 1), (2, 0), (3, 1), (4, 0), (5, 0)]
    },
    DMM010Def.RESISTOR_1ohm_RANGE: {
        'coefficient':
        1.0 / (DMM010Def.RESISTOR_CONSTANT_CURR * DMM010Def.RESISTOR_1ohm_GAIN *
               DMM010Def.ATTENUATION),
        'unit': 'ohm',
        'bits':
            [(0, 1), (1, 0), (2, 0), (3, 0), (4, 1), (5, 1)]
    },
    DMM010Def.RESISTOR_20ohm_RANGE: {
        'coefficient':
        1.0 / (DMM010Def.RESISTOR_CONSTANT_CURR * DMM010Def.RESISTOR_20ohm_GAIN *
               DMM010Def.ATTENUATION),
        'unit': 'ohm',
        'bits':
            [(0, 1), (1, 0), (2, 0), (3, 0), (4, 0), (5, 1)]
    }
}


dmm010_calibration_info = {
    DMM010Def.VOLTAGE_6V_RANGE: {
        'level1': {'unit_index': 0, 'limit': (-1000, 'mV')},
        'level2': {'unit_index': 1, 'limit': (-100, 'mV')},
        'level3': {'unit_index': 2, 'limit': (-10, 'mV')},
        'level4': {'unit_index': 3, 'limit': (0, 'mV')},
        'level5': {'unit_index': 4, 'limit': (10, 'mV')},
        'level6': {'unit_index': 5, 'limit': (100, 'mV')},
        'level7': {'unit_index': 6, 'limit': (1000, 'mV')},
        'level8': {'unit_index': 7, 'limit': (6250, 'mV')}
    },
    DMM010Def.CURRENT_1A_RANGE: {
        'level1': {'unit_index': 8, 'limit': (-100, 'mA')},
        'level2': {'unit_index': 9, 'limit': (-10, 'mA')},
        'level3': {'unit_index': 10, 'limit': (0, 'mA')},
        'level4': {'unit_index': 11, 'limit': (10, 'mA')},
        'level5': {'unit_index': 12, 'limit': (100, 'mA')},
        'level6': {'unit_index': 13, 'limit': (1050, 'mA')}
    },
    DMM010Def.RESISTOR_1ohm_RANGE: {
        'level1': {'unit_index': 14, 'limit': (0.01, 'ohm')},
        'level2': {'unit_index': 15, 'limit': (0.1, 'ohm')},
        'level3': {'unit_index': 16, 'limit': (1.3, 'ohm')}
    },
    DMM010Def.RESISTOR_20ohm_RANGE: {
        'level1': {'unit_index': 17, 'limit': (1, 'ohm')},
        'level2': {'unit_index': 18, 'limit': (20.3, 'ohm')}
    }
}

dmm010_range_table = {
    DMM010Def.VOLTAGE_6V_RANGE: 0,
    DMM010Def.CURRENT_1A_RANGE: 1,
    DMM010Def.RESISTOR_1ohm_RANGE: 2,
    DMM010Def.RESISTOR_20ohm_RANGE: 3
}


class Dmm010Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class DMM010001(MIXBoard):
    '''
    DMM010001 function class.

    compatible = ["GQQ-DMM010001-000"]

    The dmm010001 has the functions of DC voltage, DC current and resistor measurement.
    The DC voltage's input range is +/-6V, DC current's input range is +/-1A, resistor range is 1ohm and 20ohm.

    Args:
        ad7175:                 instance(ADC)/string/None,    Class instance of AD7175, if not using this parameter,
                                                         will create emulator.
        i2c:                    instance(I2C)/None,        which is used to control nct75 and cat24c32. If not given,
                                                         emulator will be created.
        ipcore:                 instance(MIXDAQT1)/string, MIXDAQT1 ipcore driver instance or device name string,
                                                         if given, user should not use ad7175.

    Examples:
        If the params `ipcore` is valid, then use MIXDAQT1 aggregated IP;
        Otherwise, if the params `ad7175`, use non-aggregated IP.

        # use MIXDAQT1 aggregated IP
        i2c = I2C('/dev/i2c-1')
        ip_daqt1 = MIXDAQT1('/dev/MIX_DAQT1_0', ad717x_chip='AD7175', ad717x_mvref=5000,
                            use_spi=False, use_gpio=False)
        dmm010001 = DMM010001(ad7175=None,
                              i2c=i2c,
                              ipcore=ip_daqt1)

        # use non-aggregated IP
        ad7175 = PLAD7175('/dev/MIX_AD717X_0', 5000)
        i2c = I2C('/dev/i2c-1')
        dmm010001 = DMM010001(ad7175=ad7175, i2c=i2c, ipcore=None)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-DMM010001-000"]

    rpc_public_api = ['module_init', 'get_sampling_rate', 'get_measure_path',
                      'voltage_measure', 'current_measure', 'resistor_measure', 'multi_points_measure',
                      'multi_points_measure_enable', 'multi_points_measure_disable'] + MIXBoard.rpc_public_api

    def __init__(self, ad7175=None, i2c=None, ipcore=None):
        if ipcore and ad7175:
            raise Dmm010Exception('Not allowed to use both aggregated IP and AD717X')

        if i2c:
            self.tca9538 = TCA9538(DMM010Def.TAC9538_I2C_ADDR, i2c)
            self.eeprom = CAT24C32(DMM010Def.CAT24C32_I2C_ADDR, i2c)
            self.sensor = NCT75(DMM010Def.NCT75_I2C_ADDR, i2c)
        else:
            self.tca9538 = TCA9538Emulator(DMM010Def.TAC9538_I2C_ADDR)
            self.eeprom = EepromEmulator("eeprom_emulator")
            self.sensor = NCT75Emulator("nct75_emulator")

        if ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, DMM010Def.MIX_DAQT1_REG_SIZE)
                ipcore = MIXDAQT1SGR(axi4_bus, "AD7175", ad717x_mvref=DMM010Def.ADC_VREF_VOLTAGE_5000mV,
                                     code_polar=DMM010Def.AD7175_CODE_POLAR,
                                     reference=DMM010Def.AD7175_REFERENCE_SOURCE,
                                     buffer_flag=DMM010Def.AD7175_BUFFER_FLAG,
                                     clock=DMM010Def.AD7175_CLOCK,
                                     use_spi=False, use_gpio=False)
            self.ad7175 = ipcore.ad717x
        elif ad7175:
            if isinstance(ad7175, basestring):
                axi4_bus = AXI4LiteBus(ad7175, DMM010Def.PLAD7175_REG_SIZE)
                ad7175 = MIXAd7175SG(axi4_bus, mvref=DMM010Def.ADC_VREF_VOLTAGE_5000mV,
                                     code_polar=DMM010Def.AD7175_CODE_POLAR,
                                     reference=DMM010Def.AD7175_REFERENCE_SOURCE,
                                     buffer_flag=DMM010Def.AD7175_BUFFER_FLAG,
                                     clock=DMM010Def.AD7175_CLOCK)
            self.ad7175 = ad7175
        else:
            self.ad7175 = MIXAd7175SGEmulator('ad7175_emulator', DMM010Def.ADC_VREF_VOLTAGE_5000mV)

        self.ad7175.config = {
            "ch0": {"P": "AIN0", "N": "AIN1"},
            "ch1": {"P": "AIN2", "N": "AIN3"}
        }

        super(DMM010001, self).__init__(self.eeprom, self.sensor, cal_table=dmm010_calibration_info,
                                        range_table=dmm010_range_table)
        self.continuous_sample_channel = None
        self.measure_path = None

    def module_init(self):
        '''
        Do module initialization.

        Set the initial tca9538 pin direction to output. Set the default sample rate for ad7175.
        Set the default measure path to 6V voltage range.
        This cannot be in __init__() because i2c and spi may not be ready.
        User need to call this function once after module instance is created.

        Returns:
            string, "done", api execution successful.

        Examples:
            ret = dmm010001.module_init()   # ret == "done"

        '''
        self.load_calibration()
        self.tca9538.set_pins_dir([0x00])
        self.ad7175.channel_init()
        for channel in DMM010Def.ADC_CHANNEL_LIST:
            self.set_sampling_rate(channel, DMM010Def.DEFAULT_SAMPLING_RATE)

        self.set_measure_path(DMM010Def.VOLTAGE_6V_RANGE)
        return "done"

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        Set adc channel sampling rate

        Args:
            channel:        int, [0, 1], 0 for 6V channel, 1 for others channel.
            sampling_rate:  float, [5~250000], unit Hz, 1000 means 1000Hz.

        Returns:
            string, "done", api execution successful, raise Exception at failure.

        Raise:
            AssertionError:  channel or sampling_rate param out of range
            AD717XException: set sampling rate failure

        Examples:
            # setting the sampling rate of adc channel 1 to 1000Hz
            ret = dmm010001.set_sampling_rate(1, 1000)   # ret == "done"

        '''
        assert channel in DMM010Def.ADC_CHANNEL_LIST
        assert 5 <= sampling_rate <= 250000

        if sampling_rate != self.get_sampling_rate(channel):
            self.ad7175.set_sampling_rate(channel, sampling_rate)

    def get_sampling_rate(self, channel):
        '''
        Get adc channel sampling rate

        Args:
            channel:    int, [0, 1], 0 for 6V channel, 1 for others channel.

        Returns:
            int, value, unit Hz, sampling rate.

        Raise:
            AssertionError:  channel param out of range.
            AD717XException: get sampling rate failure.

        Examples:
            # get adc channel 1 sampling rate
            sampling_rate = dmm010001.set_sampling_rate(1)  # sampling_rate == 1000

        '''
        assert channel in DMM010Def.ADC_CHANNEL_LIST

        return self.ad7175.get_sampling_rate(channel)

    def _volt_to_target_unit(self, sel_range, volt):
        '''
        Get target unit value from measured adc voltage

        Args:
            sel_range:    string, ['6V', '1A', '1ohm', '20ohm'], selected measurement range.
            volt:         float, the measured voltage by ad7175.

        Returns:
            float, value, the target unit value.

        Raise:
            AssertionError:  sel_range param invalid.

        Examples:
            # set voltage 6V measure path
            dmm010001.set_measure_path('6V')
            # get the adc channel 0 voltage
            volt = ad7175.read_volt(0)
            # get the target unit value
            value = dmm010001._volt_to_target_unit('6V',volt)   # type(value) == float

        '''
        assert sel_range.upper() in dmm010_function_info

        return volt * dmm010_function_info[sel_range.upper()]['coefficient']

    def set_measure_path(self, sel_range):
        '''
        Set measure path by sel_range input, related io will be set.

        Args:
            sel_range:   string, ['6V', '1A', '1ohm', '20ohm'], '6V' for voltage, '1A' for current,
                                                                '1ohm', '20ohm' for resistor.

        Returns:
            string, "done", api execution successful, raise Exception at failure.

        Raise:
            AssertionError:  sel_range param invalid.
            Exception:   contorl tca9538 error.

        Examples:
            # set 6V voltage measure path
            ret = dmm010001.set_measure_path('6V')  # ret == "done"

        '''
        sel_range = sel_range.upper()
        assert sel_range in dmm010_function_info

        if self.measure_path != sel_range:
            record_bits = 0
            bits = dmm010_function_info[sel_range]['bits']
            for bit, value in bits:
                record_bits |= (value << bit)

            self.tca9538.set_ports([record_bits])
            self.measure_path = sel_range

    def get_measure_path(self):
        '''
        Get selected measurement path.

        Returns:
            string, ['6V', '1A', '1ohm', '20ohm'], selected measurement range.

        Examples:
            path = dmm010001.get_measure_path()     # path == '6V'

        '''
        return self.measure_path

    def voltage_measure(self, sampling_rate=DMM010Def.DEFAULT_SAMPLING_RATE):
        '''
        Do one time sample from adc, return the voltage measurement result.

        Args:
            sampling_rate:   float, [5~250000], default 5, not continuous,
                                                           please refer to ad7175 datasheet.
        Returns:
            list,  [value, unit],  unit default is 'mV'.

        Raise:
            Dmm010Exception:   error voltage range.
            AD717XException:   get ad7175 voltage error.

        Examples:
            # get the single voltage meausrement result
            volt = dmm010001.single_voltage_measure()
            print(volt)  # (100.123456, 'mV')

        '''

        # Slect range
        self.set_measure_path(DMM010Def.VOLTAGE_6V_RANGE)

        # Set sampling_rate
        self.set_sampling_rate(DMM010Def.ADC_A_CHANNEL, sampling_rate)

        voltage = self.ad7175.read_volt(DMM010Def.ADC_A_CHANNEL)
        voltage = self._volt_to_target_unit(self.measure_path, voltage)
        unit = dmm010_function_info[self.measure_path]['unit']

        voltage = self.calibrate(self.measure_path, voltage)

        return [voltage, unit]

    def current_measure(self, sampling_rate=DMM010Def.DEFAULT_SAMPLING_RATE):
        '''
        Do one time sample from adc, return the current measurement result.

        Args:
            sampling_rate:   float, [5~250000], default 5, not continuous,
                                                           please refer to ad7175 datasheet.

        Returns:
            list,  [value, unit],  unit default is 'mA'.

        Raise:
            Dmm010Exception:   error current range.
            AD717XException:   get ad7175 voltage error.

        Examples:
            # set 1A current measure path
            dmm010001.set_measure_path('1A')
            # get the single current meausrement result
            curr = dmm010001.single_current_measure()
            print(curr)  # (100.123456, 'mA')

        '''

        # Slect range
        self.set_measure_path(DMM010Def.CURRENT_1A_RANGE)

        # Set sampling_rate
        self.set_sampling_rate(DMM010Def.ADC_B_CHANNEL, sampling_rate)

        voltage = self.ad7175.read_volt(DMM010Def.ADC_B_CHANNEL)
        current = self._volt_to_target_unit(self.measure_path, voltage)
        unit = dmm010_function_info[self.measure_path]['unit']

        current = self.calibrate(self.measure_path, current)

        return [current, unit]

    def resistor_measure(self, sel_range,
                         sampling_rate=DMM010Def.DEFAULT_SAMPLING_RATE):
        '''
        Do one time sample from adc, return the resistor measurement result.

        Args:
            sel_range:       string, ['1ohm', '20ohm']
            sampling_rate:   float, [5~250000], default 5, not continuous,
                                                           please refer to ad7175 datasheet.

        Returns:
            list,  [value, unit],  unit default is 'ohm'.

        Raise:
            Dmm010Exception:   error current range.
            AD717XException:   get ad7175 voltage error.

        Examples:
            # set 1ohm resistor measure path
            dmm010001.set_measure_path('1ohm')
            # get the resistor meausrement result
            res = dmm010001.resistor_measure()
            print(res)  # (0.123456, 'ohm')

        '''
        sel_range = sel_range.upper()

        if sel_range not in (DMM010Def.RESISTOR_1ohm_RANGE, DMM010Def.RESISTOR_20ohm_RANGE):
            raise Dmm010Exception("error resistor range: %s" % (sel_range))

        # Slect range
        self.set_measure_path(sel_range)

        # Set sampling_rate
        self.set_sampling_rate(DMM010Def.ADC_B_CHANNEL, sampling_rate)

        voltage = self.ad7175.read_volt(DMM010Def.ADC_B_CHANNEL)
        resistor = self._volt_to_target_unit(sel_range, voltage)
        unit = dmm010_function_info[sel_range]['unit']

        resistor = self.calibrate(sel_range, resistor)

        return [resistor, unit]

    def multi_points_measure(self, sel_range, count,
                             sampling_rate=DMM010Def.DEFAULT_SAMPLING_RATE):
        '''
        Measure voltage/current/resistor rms, average, max, min value in continuous mode.

        Notice that before call this function, continuous voltage measure has been started.

        Args:
            sel_range:      string, ['6V', '1A', '1ohm', '20ohm'], '6V' for voltage, '1A' for current,
                                                                   '1ohm', '20ohm' for resistor.
            count:           int, the number of sampling points.
            sampling_rate:   float, [5~250000], default 5, not continuous,
                                                           please refer to ad7175 datasheet.

        Returns:
            dict, {"rms": [value, unit], "average": [value, unit], "max": [value, unit], "min": [value, unit]}.

        Raise:
            AssertionError:  count param is not int type or count <= 0.
            Dmm010Exception: the measure path is invalid or ad7175 is not in continuous mode.
            AD717XException: get the ad7175 continuous sampling voltage error.

        Examples:
            # get the countinuous measure result at 10 sampling points
            result = dmm010001.multi_points_measure('6V', 10)
            # result = {"rms": (10.1, 'mV'), "average": (10.1, 'mV'), "max": (10.2, 'mV'), "min": (9.9, 'mV')}
            print(result)

        '''
        sel_range = sel_range.upper()
        assert isinstance(count, int) and count > 0

        if sel_range not in dmm010_function_info:
            raise Dmm010Exception("the measure path is invalid: %s" % (sel_range))

        if self.continuous_sample_channel not in DMM010Def.ADC_CHANNEL_LIST:
            raise Dmm010Exception("the ad7175 is not in continuous measure mode")

        unit = dmm010_function_info[sel_range]['unit']

        adc_channel = DMM010Def.ADC_A_CHANNEL if \
            sel_range == DMM010Def.VOLTAGE_6V_RANGE else \
            DMM010Def.ADC_B_CHANNEL

        # Slect range
        self.set_measure_path(sel_range)

        adc_volt = self.ad7175.get_continuous_sampling_voltage(
            adc_channel, count)

        min_data = min(adc_volt)
        max_data = max(adc_volt)
        sum_Data = sum(adc_volt)
        avg_data = float(sum_Data) / len(adc_volt)
        suqare_sum_data = sum([x**2 for x in adc_volt])
        rms_data = math.sqrt(float(suqare_sum_data) / len(adc_volt))

        rms = self._volt_to_target_unit(sel_range, rms_data)
        average = self._volt_to_target_unit(sel_range, avg_data)
        max_voltage = self._volt_to_target_unit(sel_range, max_data)
        min_voltage = self._volt_to_target_unit(sel_range, min_data)

        average = self.calibrate(sel_range, average)

        result = dict()
        result['rms'] = [rms, unit + 'rms']
        result['average'] = [average, unit]
        result['max'] = [max_voltage, unit]
        result['min'] = [min_voltage, unit]

        return result

    def multi_points_measure_enable(self, channel,
                                    sampling_rate=DMM010Def.DEFAULT_SAMPLING_RATE):
        '''
        Enable adc channel to continuous measure mode

        Args:
            channel:         int, [0, 1], 0 for 6V voltage channel, 1 for others channel.
            sampling_rate:   float, [5~250000], default 5, not continuous,
                                                           please refer to ad7175 datasheet.

        Returns:
            string, "done", api execution successful, raise Exception at failure.

        Raise:
            AssertionError:  channel param is invalid.
            AD717XException: contorl the ad7175 error.

        Examples:
            # enable adc channel 0 to continuous measure mode
            ret = dmm010001.multi_points_measure_enable(0) # ret == "done"

        '''
        assert channel in DMM010Def.ADC_CHANNEL_LIST

        self.ad7175.disable_continuous_sampling(channel)
        time.sleep(DMM010Def.SWITCH_DELAY)
        self.ad7175.enable_continuous_sampling(channel, sampling_rate)
        self.continuous_sample_channel = channel

        return "done"

    def multi_points_measure_disable(self, channel):
        '''
        Disable continuous measure

        Args:
            channel:  int, [0, 1], 0 for 6V voltage channel, 1 for others channel.

        Returns:
            string, "done", api execution successful, raise Exception at failure.

        Raise:
            AssertionError:  channel param is invalid.
            AD717XException: contorl the ad7175 error.

        Examples:
            # disable adc channel 0 to continuous measrue mode
            ret = dmm010001.multi_points_measure_disable(0) # ret == "done"

        '''
        assert channel in DMM010Def.ADC_CHANNEL_LIST

        self.ad7175.disable_continuous_sampling(channel)
        self.continuous_sample_channel = None

        return "done"

    def legacy_write_calibration_cell(self, unit_index, gain, offset):
        '''
        Calibration data write function

        Args:
            unit_index:   int,    calibration unit index.
            gain:         float,  calibration gain.
            offset:       float,  calibration offset.

        Returns:
            string, "done", api execution successful, raise Exception at failure.

        Raise:
            BoardArgCheckError:  unit_index < 0 or type is not int.

        :Examples:
            # write calibration gain 1.1, offset 0.1 to unit index 0
            ret = dmm010001.legacy_write_calibration_cell(0, 1.1, 0.1) # ret == "done"

        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        use_flag = self.calibration_info["use_flag"]
        data = (gain, offset, use_flag, 0xff, 0xff, 0xff)
        s = struct.Struct(DMM010Def.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(DMM010Def.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = self.calibration_info["unit_start_addr"] + \
            DMM010Def.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)

        return "done"

    def legacy_read_calibration_cell(self, unit_index):
        '''
        Read calibration data function

        Args:
            unit_index:   int, calibration unit index.

        Returns:
            dict, {"gain": value, "offset": value, "threshold": value, "is_use": value}.

        Raise:
            BoardArgCheckError: unit_index < 0 or type is not int.

        :Examples:
            # read unit_index 0 calibration value
            data = dmm010001.legacy_read_calibration_cell(0)
            # data = {"gain": 1.1, "offset": 0.1, "threshold": -1000, "is_use": true}
            print(data)

        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        address = self.calibration_info["unit_start_addr"] + \
            DMM010Def.CAL_DATA_LEN * unit_index
        data = self.read_eeprom(address, DMM010Def.READ_CAL_BYTE)

        s = struct.Struct(DMM010Def.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(DMM010Def.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        threshold = 0.0
        for cal_item in dmm010_calibration_info.keys():
            for level in dmm010_calibration_info[cal_item].keys():
                if unit_index == dmm010_calibration_info[cal_item][level]["unit_index"]:
                    threshold = dmm010_calibration_info[cal_item][level]["limit"][0]
                    break

        if self.calibration_info["use_flag"] != result[2]:
            return {"gain": 1.0, "offset": 0.0, "threshold": 0, "is_use": False}
        else:
            return {"gain": result[0], "offset": result[1], "threshold": threshold, "is_use": True}

    def legacy_erase_calibration_cell(self, unit_index):
        '''
        Erase calibration value in eeprom

        Args:
            unit_index:   int, calibration unit index.

        Returns:
            string, "done", api execution successful, raise Exception at failure.

        Raise:
            BoardArgCheckError: unit_index < 0 or type is not int.

        :Examples:
            # erase the unit_index 0 calibration value in eeprom
            ret = dmm010001.erase_calibration_cell(0) # ret == "done"

        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        data = [0xff for i in range(DMM010Def.CAL_DATA_LEN)]
        address = self.calibration_info["unit_start_addr"] + DMM010Def.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)

        return "done"
