# -*- coding: utf-8 -*-
import math
import time
import struct
from mix.driver.core.bus.pin import Pin
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard, BoardArgCheckError


__author__ = 'jihuajiang@SmartGiant'
__version__ = '0.2'

wolverine_calibration_info = {
    'VOLT_5V': {
        'level1': {'unit_index': 0, 'limit': (-1000, 'mV')},
        'level2': {'unit_index': 1, 'limit': (-100, 'mV')},
        'level3': {'unit_index': 2, 'limit': (-10, 'mV')},
        'level4': {'unit_index': 3, 'limit': (0, 'mV')},
        'level5': {'unit_index': 4, 'limit': (10, 'mV')},
        'level6': {'unit_index': 5, 'limit': (100, 'mV')},
        'level7': {'unit_index': 6, 'limit': (1000, 'mV')},
        'level8': {'unit_index': 7, 'limit': (6000, 'mV')}
    },
    'CURR_100uA': {
        'level1': {'unit_index': 8, 'limit': (-0.01, 'mA')},
        'level2': {'unit_index': 9, 'limit': (0, 'mA')},
        'level3': {'unit_index': 10, 'limit': (0.01, 'mA')},
        'level4': {'unit_index': 11, 'limit': (0.12, 'mA')}
    },
    'CURR_2mA': {
        'level1': {'unit_index': 12, 'limit': (-1, 'mA')},
        'level2': {'unit_index': 13, 'limit': (-0.09, 'mA')},
        'level3': {'unit_index': 14, 'limit': (0.09, 'mA')},
        'level4': {'unit_index': 15, 'limit': (1, 'mA')},
        'level5': {'unit_index': 16, 'limit': (2.5, 'mA')}
    }
}

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
    EMULATOR_REG_SIZE = 256
    CURR_100UA = '100uA'
    CURR_2MA = '2mA'
    VOLT_5V = '5V'
    CHANNEL_CONFIG = {
        CURRENT_CHANNEL: {
            'adc_channel': 0,
            'range': {
                CURR_100UA: {
                    "path": [("range_sel_bit", 1), ("meter_sel_bit", 1)],
                },
                CURR_2MA: {
                    "path": [("range_sel_bit", 0), ("meter_sel_bit", 1)],
                },
            }
        },
        VOLTAGE_CHANNEL: {
            'adc_channel': 1,
            'range': {
                VOLT_5V: {
                    "path": [("meter_sel_bit", 0), ]
                }
            }
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

    # default sampling rate is 5 Hz which is defined in Driver ERS
    DEFAULT_SAMPLE_RATE = 5

    # AD7175 reference voltage is 5V
    MVREF = 5000.0

    # Using crystal as AD7175 clock
    CLOCK = 'crystal'

    # AD7175 input voltage is bipolar
    POLAR = 'bipolar'

    PLAD7175_REG_SIZE = 256
    MIX_DAQT1_REG_SIZE = 65535


class WolverineException(Exception):

    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Wolverine(MIXBoard):

    '''
    DMM001 is a compact version of the digital multimeter which internal ADC resolution is 24 bit.

    compatible = ["GQQ-DMM001003-000"]

    It can be used as
    high performance DMM to measure DC voltage and small signal DC current. In this class, adc channel 0 is current
    channel, adc channel 1 is voltage channel. DMM001 support signal measurement and continuous measurement. Note that
    if range_ctrl0 and range_ctrl1 not given, internal submodule GPIO device of MIX_DAQT1 will be used to control range.
    Note that calibration default is enabled. This class is legacy driver for normal boot.

    Args:
        i2c:             instance(I2C)/None, which is used to control nct75 and cat24c32. If not given,
                                            emulator will be created.
        ad7175:          instance(ADC)/None, Class instance of AD7175, if not using this parameter, will create emulator
        range_sel:       instance(GPIO),       This can be Pin or xilinx gpio, used to control range.
        meter_sel:       instance(GPIO),       This can be Pin or xilinx gpio, used to control measure channel
        ipcore:          instance(MIXDAQT1SGR)/string,  MIXDAQT1SGR ipcore driver instance or device name string,
                                              if given, user should not use ad7175.


    Examples:
        Example for using no-aggregate IP:
            # normal init
            ad7175 = MIXAd7175SG('/dev/MIX_AD717X_0', 5000)
            i2c = I2C('/dev/i2c-1')
            gpio = GPIO(i2c)
            range_sel = Pin(gpio, 1)
            meter_sel = Pin(gpio, 3)
            wolverine = Wolverine(i2c, ad7175, range_sel=range_sel, meter_sel=meter_sel)

            # using ipcore device name string
            i2c = I2C('/dev/i2c-1')
            gpio = GPIO(i2c)
            range_sel = Pin(gpio, 1)
            meter_sel = Pin(gpio, 3)
            wolverine = Wolverine(i2c, '/dev/MIX_AD717X_0', range_sel=range_sel, meter_sel=meter_sel)


        Example for using aggregate IP:
            # normal init
            i2c = I2C('/dev/i2c-1')
            daqt1 = MIXDAQT1SGR('/dev/MIX_DAQT1', ad717x_chip='AD7175', ad717x_mvref=5000, use_spi=False, use_gpio=True)
            wolverine = Wolverine(i2c, ipcore=daqt1)

            # using ipcore device name
            i2c = I2C('/dev/i2c-1')
            wolverine = Wolverine(i2c, ipcore='/dev/MIX_DAQT1')

        Example for measuring voltage:
            result = wolverine.voltage_measure(5)
            print("voltage={}, unit={}".format(result[0], result[1]))

            result = wolverine.multi_points_voltage_measure(3, 5)
            print("average={}, max={}, min={}, rms={}".format(result['average'], result['max'],
            result['min'], result['rms']))

        Example for measuring current:
            result = wolverine.current_measure('2mA', 5)
            print("current={}, unit={}".format(result[0], result[1]))

            result = wolverine.multi_points_current_measure(3, '2mA', 5)
            print("average={}, max={}, min={}, rms={}".format(result['average'], result['max'],
            result['min'], result['rms']))

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-DMM001003-000"]

    rpc_public_api = ['module_init', 'get_sampling_rate', 'set_measure_path', 'get_measure_path',
                      'voltage_measure', 'multi_points_voltage_measure', 'current_measure',
                      'multi_points_current_measure'] + MIXBoard.rpc_public_api

    def __init__(self, i2c, ad7175=None, range_sel=None,
                 meter_sel=None, ipcore=None):

        if i2c and ad7175 and range_sel and meter_sel and not ipcore:
            if isinstance(ad7175, basestring):
                axi4 = AXI4LiteBus(ad7175, WolverineDef.PLAD7175_REG_SIZE)
                self.ad7175 = MIXAd7175SG(axi4, mvref=WolverineDef.MVREF, code_polar=WolverineDef.POLAR,
                                          clock=WolverineDef.CLOCK)
            else:
                self.ad7175 = ad7175
            self.range_sel = range_sel
            self.meter_sel = meter_sel
        elif i2c and not ad7175 and not range_sel and not meter_sel and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, WolverineDef.MIX_DAQT1_REG_SIZE)
                self.ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=WolverineDef.MVREF,
                                          code_polar=WolverineDef.POLAR, clock=WolverineDef.CLOCK, use_gpio=True)
            else:
                self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x
            gpio = self.ipcore.gpio
            self.range_sel = Pin(gpio, WolverineDef.RANGE_SEL_BIT)
            self.meter_sel = Pin(gpio, WolverineDef.METER_SEL_BIT)
        elif i2c and not ad7175 and range_sel and meter_sel and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, WolverineDef.REG_SIZE)
                self.ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=WolverineDef.MVREF,
                                          code_polar=WolverineDef.POLAR, clock=WolverineDef.CLOCK, use_gpio=False)
            else:
                self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x
            self.range_sel = range_sel
            self.meter_sel = meter_sel
        elif not i2c and not ad7175 and not range_sel and not meter_sel and not ipcore:
            self.ad7175 = MIXAd7175SGEmulator("ad7175_emulator", WolverineDef.EMULATOR_REG_SIZE)
            self.range_sel = Pin(None, WolverineDef.RANGE_SEL_BIT)
            self.meter_sel = Pin(None, WolverineDef.METER_SEL_BIT)
        else:
            raise WolverineException("Invalid parameter, please check")
        if i2c:
            eeprom = CAT24C32(WolverineDef.EEPROM_DEV_ADDR, i2c)
            nct75 = NCT75(WolverineDef.NCT75_DEV_ADDR, i2c)
            super(Wolverine, self).__init__(eeprom, nct75, cal_table=wolverine_calibration_info,
                                            range_table=wolverine_range_table)
        else:
            super(Wolverine, self).__init__(None, None, cal_table=wolverine_calibration_info,
                                            range_table=wolverine_range_table)

        self.channel_path = {'range_sel_bit': self.range_sel, 'meter_sel_bit': self.meter_sel}
        self.measure_path = {"channel": None, "range": None}

    def _check_channel(self, channel):
        '''
        Check the channel if it is valid.

        Args:
            channel:  string, ['CURR', 'VOLT'], the channel to check.

        Returns:
            string, ['CURR', 'VOLT'], the channel in specific format.

        Raise:
            WolverineException:  If channel is invalid, exception will be raised.

        '''
        for ch in WolverineDef.CHANNEL_CONFIG:
            if channel.lower() == ch.lower():
                return ch
        raise WolverineException("channel {} is invalid".format(channel))

    def _check_scope(self, channel, scope):
        '''
        Check valid of the specific scope.

        Args:
            channel:     string, the channel to change scope.
            scope:       string, the scope string to be checked.

        Returns:
            string, str, the scope in specific format.

        Raise:
            WolverineException:  If the scope is invalid, exception will be raised.

        '''
        range_config = WolverineDef.CHANNEL_CONFIG[channel]['range']
        for rng in range_config:
            if rng.lower() == scope.lower():
                return rng
        raise WolverineException('scope {} in channel {} is not invalid'.format(channel, scope))

    def module_init(self):
        '''
        Init wolverine module. This function will set io direction to output and set default range to '5V'

        Returns:
            string, "done", api execution successful.

        '''
        self.range_sel.set_dir('output')
        self.meter_sel.set_dir('output')
        self.set_measure_path(WolverineDef.VOLT_5V)
        self.ad7175.channel_init()
        self.set_sampling_rate(WolverineDef.VOLTAGE_CHANNEL, WolverineDef.DEFAULT_SAMPLE_RATE)
        self.set_sampling_rate(WolverineDef.CURRENT_CHANNEL, WolverineDef.DEFAULT_SAMPLE_RATE)
        self.load_calibration()
        return "done"

    def set_sampling_rate(self, channel, sampling_rate):
        '''
        Wolverine set sampling rate.

        Note that sampling rate is not discontinuous, all support sampling
        rate can be found in ad7175 datasheet.

        Args:
            channel:            string, ['VOLT', 'CURR'], the channel to change sampling rate.
            sampling_rate:      float, [5~250000], adc measure sampling rate, which is not continuous,
                                                        please refer to ad7175 datasheet.

        Returns:
            string, "done", api execution successful.

        Examples:
            wolverine.set_sampling_rate('VOLT', 10000)

        '''
        assert 5 <= sampling_rate <= 250000
        channel = self._check_channel(channel)

        if sampling_rate != self.get_sampling_rate(channel):
            self.ad7175.set_sampling_rate(WolverineDef.CHANNEL_CONFIG[channel]['adc_channel'], sampling_rate)

    def get_sampling_rate(self, channel):
        '''
        Wolverine get sampling rate of adc

        Args:
            channel:            string, ['VOLT', 'CURR'], the channel to get sampling rate.

        Returns:
            int, value, current module sampling rate.

        Examples:
            sampling_rate = wolverine.set_sampling_rate('VOLT')
            print(sampling_rate)

        '''
        channel = self._check_channel(channel)

        return self.ad7175.get_sampling_rate(WolverineDef.CHANNEL_CONFIG[channel]['adc_channel'])

    def _get_channel_from_scope(self, scope):
        '''
        Get channel from scope string.

        Args:
            scope:     string, ['5V', '2mA', '100uA'], measure range string.

        Examples:
            string, ['VOLT', 'CURR', wolverine measure channel.

        '''
        if scope.lower() == WolverineDef.VOLT_5V.lower():
            return WolverineDef.VOLTAGE_CHANNEL
        elif scope.lower() in [WolverineDef.CURR_2MA.lower(), WolverineDef.CURR_100UA.lower()]:
            return WolverineDef.CURRENT_CHANNEL
        else:
            raise WolverineException("scope {} is invalid.".format(scope))

    def set_measure_path(self, scope):
        '''
        Wolverine set measure path.

        Args:
            scope:       string, ['100uA', '2mA', '5V''], set range for different channel

        Returns:
            string, "done", api execution successful.

        Examples:
            wolverine.setmeasure_path('5V')

        '''
        channel = self._get_channel_from_scope(scope)
        scope = self._check_scope(channel, scope)

        path_bits = WolverineDef.CHANNEL_CONFIG[channel]['range'][scope]['path']

        if self.measure_path["channel"] != channel or \
                self.measure_path["range"] != scope:
            for bits in path_bits:
                self.channel_path[bits[0]].set_level(bits[1])

        self.measure_path["channel"] = channel
        self.measure_path["range"] = scope

    def get_measure_path(self):
        '''
        Wolverine get measure path.

        Returns:
            dict, current channel and range.

        Examples:
            path = wolverine.get_measure_path()
            printf(path)

        '''
        return self.measure_path

    def voltage_measure(self, sampling_rate=WolverineDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverine measure voltage once

        Args:
            sampling_rate:  float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.

        Returns:
            list, [value, 'mV'], voltage value and unit.

        '''

        # Slect range: VOLT_5V = '5V'
        self.set_measure_path(WolverineDef.VOLT_5V)

        # Set sampling_rate
        self.set_sampling_rate(WolverineDef.VOLTAGE_CHANNEL, sampling_rate)

        voltage = self.ad7175.read_volt(WolverineDef.CHANNEL_CONFIG[self.measure_path['channel']]['adc_channel'])
        gain = WolverineDef.VOLTAGE_5V_GAIN
        voltage /= gain
        cal_item = self.measure_path["channel"] + "_" + self.measure_path["range"]
        voltage = self.calibrate(cal_item, voltage)

        return [voltage, 'mV']

    def multi_points_voltage_measure(self, count, sampling_rate=WolverineDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverine measure voltage in continuous mode.

        Notice that before call this function,
        continuous voltage measure has been started.

        Args:
            count:          int, [1~512], Get count voltage in continuous mode.
            sampling_rate:  float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.

        Returns:
            dict, {"rms":[value, 'mVrms'], "average":[value, 'mV'], "max":[value, 'mV'], "min":[value, 'mV']},
                  rms, average, max and min voltage with unit.

        '''

        adc_channel = WolverineDef.CHANNEL_CONFIG[self.measure_path['channel']]['adc_channel']

        # Slect range: VOLT_5V = '5V'
        self.set_measure_path(WolverineDef.VOLT_5V)

        self.ad7175.disable_continuous_sampling(adc_channel)
        time.sleep(WolverineDef.SWITCH_DELAY)
        self.ad7175.enable_continuous_sampling(adc_channel,
                                               sampling_rate)
        adc_volt = self.ad7175.get_continuous_sampling_voltage(adc_channel, count)
        self.ad7175.disable_continuous_sampling(adc_channel)

        min_data = min(adc_volt)
        max_data = max(adc_volt)
        sum_Data = sum(adc_volt)
        avg_data = sum_Data / len(adc_volt)
        suqare_sum_data = sum([x**2 for x in adc_volt])
        rms_data = math.sqrt(suqare_sum_data / len(adc_volt))

        gain = WolverineDef.VOLTAGE_5V_GAIN

        rms = rms_data / gain
        voltage = avg_data / gain
        max_voltage = max_data / gain
        min_voltage = min_data / gain

        cal_item = self.measure_path["channel"] + "_" + self.measure_path["range"]
        voltage = self.calibrate(cal_item, voltage)

        result = dict()
        result['rms'] = (rms, 'mVrms')
        result['average'] = (voltage, 'mV')
        result['max'] = (max_voltage, 'mV')
        result['min'] = (min_voltage, 'mV')

        return result

    def current_measure(self, curr_range=WolverineDef.CURR_2MA,
                        sampling_rate=WolverineDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverine measure current once

        Args:
            curr_range:     string, ['2mA', '100uA'], default '2mA', measure range string.
            sampling_rate:  float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.

        Returns:
            list, [value, 'mA'], current value and unit.

        '''
        assert curr_range in [WolverineDef.CURR_100UA, WolverineDef.CURR_2MA]

        # Slect range: CURR_100UA = '100uA', CURR_2MA = '2mA'
        self.set_measure_path(curr_range)

        # Set sampling_rate
        self.set_sampling_rate(WolverineDef.CURRENT_CHANNEL, sampling_rate)

        volt = self.ad7175.read_volt(WolverineDef.CHANNEL_CONFIG[self.measure_path['channel']]['adc_channel'])

        sample_res = WolverineDef.CURRENT_100UA_SAMPLE_RES if \
            self.measure_path["range"] == WolverineDef.CURR_100UA else \
            WolverineDef.CURRENT_2MA_SAMPLE_RES
        gain = WolverineDef.CURRENT_100UA_GAIN if \
            self.measure_path["range"] == WolverineDef.CURR_100UA else \
            WolverineDef.CURRENT_2MA_GAIN
        current = (volt / gain) / sample_res
        cal_item = self.measure_path["channel"] + "_" + self.measure_path["range"]
        current = self.calibrate(cal_item, current)

        return [current, 'mA']

    def multi_points_current_measure(self, count,
                                     curr_range=WolverineDef.CURR_2MA,
                                     sampling_rate=WolverineDef.DEFAULT_SAMPLE_RATE):
        '''
        Wolverine measure current in continuous mode.

        Note that before call this function,
        continuous current measure must be started first

        Args:
            count:           int, [1~512], number current value to be get
            curr_range:      string, ['2mA', '100uA'], default '2mA', measure range string.
            sampling_rate:   float, [5~250000], default 5, not continuous, please refer to ad7175 datasheet.

        Returns:
            dict, {"rms":[value, 'mVrms'], "average":[value, 'mA'], "max":[value, 'mA'], "min":[value, 'mA']},
                  rms, average, max and min current with unit.

        '''
        assert curr_range in [WolverineDef.CURR_100UA, WolverineDef.CURR_2MA]

        adc_channel = WolverineDef.CHANNEL_CONFIG[self.measure_path['channel']]['adc_channel']

        # Slect range: CURR_100UA = '100uA', CURR_2MA = '2mA'
        self.set_measure_path(curr_range)

        self.ad7175.disable_continuous_sampling(adc_channel)
        time.sleep(WolverineDef.SWITCH_DELAY)

        self.ad7175.enable_continuous_sampling(adc_channel,
                                               sampling_rate)

        adc_volt = self.ad7175.get_continuous_sampling_voltage(adc_channel, count)
        self.ad7175.disable_continuous_sampling(adc_channel)

        min_data = min(adc_volt)
        max_data = max(adc_volt)
        sum_Data = sum(adc_volt)
        avg_data = sum_Data / len(adc_volt)
        suqare_sum_data = sum([x**2 for x in adc_volt])
        rms_data = math.sqrt(suqare_sum_data / len(adc_volt))

        sample_res = WolverineDef.CURRENT_100UA_SAMPLE_RES if \
            self.measure_path["range"] == WolverineDef.CURR_100UA else \
            WolverineDef.CURRENT_2MA_SAMPLE_RES
        gain = WolverineDef.CURRENT_100UA_GAIN if \
            self.measure_path["range"] == WolverineDef.CURR_100UA else \
            WolverineDef.CURRENT_2MA_GAIN

        rms = (rms_data / gain) / sample_res
        current = (avg_data / gain) / sample_res
        max_current = (max_data / gain) / sample_res
        min_current = (min_data / gain) / sample_res

        cal_item = self.measure_path["channel"] + "_" + self.measure_path["range"]
        current = self.calibrate(cal_item, current)

        result = dict()
        result['rms'] = (rms, 'mArms')
        result['average'] = (current, 'mA')
        result['max'] = (max_current, 'mA')
        result['min'] = (min_current, 'mA')

        return result

    def legacy_write_calibration_cell(self, unit_index, gain, offset, threshold):
        '''
        MIXBoard calibration data write

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
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        use_flag = self.calibration_info["use_flag"]
        data = (gain, offset, use_flag)
        s = struct.Struct(WolverineDef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(WolverineDef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = self.calibration_info["unit_start_addr"] + WolverineDef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)
        return "done"

    def legacy_read_calibration_cell(self, unit_index):
        '''
        MIXBoard read calibration data

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
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        address = self.calibration_info["unit_start_addr"] + WolverineDef.CAL_DATA_LEN * unit_index
        data = self.read_eeprom(address, WolverineDef.READ_CAL_BYTE)

        s = struct.Struct(WolverineDef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(WolverineDef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        threshold = 0.0
        for cal_item in wolverine_calibration_info:
            for level in wolverine_calibration_info[cal_item]:
                if unit_index == wolverine_calibration_info[cal_item][level]["unit_index"]:
                    threshold = wolverine_calibration_info[cal_item][level]["limit"][0]

        if self.calibration_info["use_flag"] != result[2]:
            return {"gain": 1.0, "offset": 0.0, "threshold": 0, "is_use": True}
        else:
            return {"gain": result[0], "offset": result[1], "threshold": threshold, "is_use": True}
