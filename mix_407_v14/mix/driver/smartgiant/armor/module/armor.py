# -*- coding: utf-8 -*-
import struct
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.smartgiant.common.module.mix_board import BoardArgCheckError
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667R
from mix.driver.smartgiant.common.ic.mcp4725 import MCP4725
from mix.driver.smartgiant.common.ic.pca9536 import PCA9536
from mix.driver.smartgiant.common.ic.ad527x import AD5272
from mix.driver.smartgiant.common.ic.ad56x7_emulator import AD5667REmulator
from mix.driver.smartgiant.common.ic.mcp4725_emulator import MCP4725Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.ic.pca9536_emulator import PCA9536 as PCA9536Emulator
from mix.driver.smartgiant.common.ic.ad5272_emulator import AD5272Emulator


__author__ = 'zicheng.huang@SmartGiant'
__version__ = '0.2'


class ArmorCoeffDef:
    # These coefficient obtained from Armor Driver ERS

    CAL_DATA_LEN = 13
    WRITE_CAL_DATA_PACK_FORMAT = '2f5B'
    WRITE_CAL_DATA_UNPACK_FORMAT = '13B'

    READ_CAL_BYTE = 13
    READ_CAL_DATA_PACK_FORMAT = '13B'
    READ_CAL_DATA_UNPACK_FORMAT = '2f5B'


armor_calibration_info = {
    'batt': {
        'level1': {'unit_index': 0, 'limit': (10, 'mV')},
        'level2': {'unit_index': 1, 'limit': (50, 'mV')},
        'level3': {'unit_index': 2, 'limit': (100, 'mV')},
        'level4': {'unit_index': 3, 'limit': (500, 'mV')},
        'level5': {'unit_index': 4, 'limit': (1000, 'mV')},
        'level6': {'unit_index': 5, 'limit': (3000, 'mV')},
        'level7': {'unit_index': 6, 'limit': (5000, 'mV')}
    },
    'ppvrect': {
        'level1': {'unit_index': 7, 'limit': (10, 'mV')},
        'level2': {'unit_index': 8, 'limit': (50, 'mV')},
        'level3': {'unit_index': 9, 'limit': (100, 'mV')},
        'level4': {'unit_index': 10, 'limit': (500, 'mV')},
        'level5': {'unit_index': 11, 'limit': (1000, 'mV')},
        'level6': {'unit_index': 12, 'limit': (3000, 'mV')},
        'level7': {'unit_index': 13, 'limit': (5000, 'mV')},
        'level8': {'unit_index': 14, 'limit': (8000, 'mV')}
    },
    'vddmain': {
        'level1': {'unit_index': 15, 'limit': (10, 'mV')},
        'level2': {'unit_index': 16, 'limit': (50, 'mV')},
        'level3': {'unit_index': 17, 'limit': (100, 'mV')},
        'level4': {'unit_index': 18, 'limit': (500, 'mV')},
        'level5': {'unit_index': 19, 'limit': (1000, 'mV')},
        'level6': {'unit_index': 20, 'limit': (3000, 'mV')},
        'level7': {'unit_index': 21, 'limit': (5000, 'mV')}
    },
    'eload': {
        'level1': {'unit_index': 22, 'limit': (10, 'mA')},
        'level2': {'unit_index': 23, 'limit': (30, 'mA')},
        'level3': {'unit_index': 24, 'limit': (50, 'mA')},
        'level4': {'unit_index': 25, 'limit': (100, 'mA')},
        'level5': {'unit_index': 26, 'limit': (200, 'mA')},
        'level6': {'unit_index': 27, 'limit': (500, 'mA')}
    },
    'batt_limit': {
        'level1': {'unit_index': 28, 'limit': (10, 'mA')},
        'level2': {'unit_index': 29, 'limit': (50, 'mA')},
        'level3': {'unit_index': 30, 'limit': (100, 'mA')},
        'level4': {'unit_index': 31, 'limit': (500, 'mA')},
        'level5': {'unit_index': 32, 'limit': (1000, 'mA')},
        'level6': {'unit_index': 33, 'limit': (1200, 'mA')}
    },
    'ppvrect_limit': {
        'level1': {'unit_index': 34, 'limit': (10, 'mA')},
        'level2': {'unit_index': 35, 'limit': (50, 'mA')},
        'level3': {'unit_index': 36, 'limit': (100, 'mA')},
        'level4': {'unit_index': 37, 'limit': (500, 'mA')}
    },
    'vddmain_limit': {
        'level1': {'unit_index': 38, 'limit': (10, 'mA')},
        'level2': {'unit_index': 39, 'limit': (50, 'mA')},
        'level3': {'unit_index': 40, 'limit': (100, 'mA')},
        'level4': {'unit_index': 41, 'limit': (500, 'mA')}
    },
    "batt_readback": {
        'level1': {'unit_index': 42, 'limit': (10, 'mA')},
        'level2': {'unit_index': 43, 'limit': (50, 'mA')},
        'level3': {'unit_index': 44, 'limit': (100, 'mA')},
        'level4': {'unit_index': 45, 'limit': (500, 'mA')},
        'level5': {'unit_index': 46, 'limit': (1000, 'mA')},
        'level6': {'unit_index': 47, 'limit': (1200, 'mA')}
    },
    "ppvrect_readback": {
        'level1': {'unit_index': 48, 'limit': (10, 'mA')},
        'level2': {'unit_index': 49, 'limit': (50, 'mA')},
        'level3': {'unit_index': 50, 'limit': (100, 'mA')},
        'level4': {'unit_index': 51, 'limit': (500, 'mA')}
    },
    "vddmain_readback": {
        'level1': {'unit_index': 52, 'limit': (10, 'mA')},
        'level2': {'unit_index': 53, 'limit': (50, 'mA')},
        'level3': {'unit_index': 54, 'limit': (100, 'mA')},
        'level4': {'unit_index': 55, 'limit': (500, 'mA')}
    },
    "eload_readback": {
        'level1': {'unit_index': 56, 'limit': (10, 'mA')},
        'level2': {'unit_index': 57, 'limit': (50, 'mA')},
        'level3': {'unit_index': 58, 'limit': (100, 'mA')},
        'level4': {'unit_index': 59, 'limit': (500, 'mA')}
    }
}

armor_range_table = {
    "batt": 0,
    "ppvrect": 1,
    "vddmain": 2,
    "eload": 3,
    "batt_limit": 4,
    "ppvrect_limit": 5,
    "vddmain_limit": 6,
    "batt_readback": 7,
    "ppvrect_readback": 8,
    "vddmain_readback": 9,
    "eload_readback": 10
}


class ArmorDef:

    IO_SET = 0x00

    DAC_VOLTAGE_REF = 2500  # mV
    DAC3_VOLTAGE_REF = 3300  # mV
    DAC1_DEV_ADDR = 0x0C
    DAC2_DEV_ADDR = 0x0F
    DAC3_DEV_ADDR = 0x60
    RES_1_ADDR = 0x2C
    RES_2_ADDR = 0x2F
    DAC_CHANNEL = {'A': 0, 'B': 1, 'ALL': 2}
    ENABLE_LEVEL = 1
    DISABLE_LEVEL = 0
    BATT_PIN = 0
    RECT_PIN = 1
    MAIN_PIN = 2
    RES_CMD_ADDR = 0x07
    RES_CMD_DATA = 0x02
    RES_WORK_MODE = 'normal'
    SLEEP_TIME = 0.005

    MAX_VOLTAGE = 2500.0
    MIN_VOLTAGE = 0.0

    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    IO_EXP_DEV_ADDR = 0x41

    UNIT_CONVERSION = 1000.0

    DAC_CHANNEL_LIST = ('batt', 'vddmain', 'ppvrect', 'eload')
    DAC_RANGE_DICT = {"batt": {"min": -30.6, "max": 5495},
                      "vddmain": {"min": -30.6, "max": 5495},
                      "ppvrect": {"min": -30.6, "max": 8000},
                      "eload": {"min": -30.6, "max": 5495}}
    ADC_CHANNEL_LIST = ('vddmain', 'ppvrect', 'batt', 'eload')
    # Hardware engineer defineed Vback range value for different channel.
    ADC_RANGE_DICT = {"batt": {"min": -6500, "max": 6500},
                      "vddmain": {"min": 0, "max": 6500},
                      "ppvrect": {"min": 0, "max": 6500},
                      "eload": {"min": 0, "max": 6500}}

formula = {
    # VOUT = 2.24 * DAC - 30.6
    "batt": lambda vout: (((vout) + 30.6) / 2.24),
    # VOUT = 1.62 * (2.24 * DAC) - 30.6
    "vddmain": lambda vout: (((vout) + 30.6) / 2.24),
    # VOUT = 2.24 * DAC - 30.6
    "ppvrect": lambda vout: (((vout / 1.62) + 30.6) / 2.24),
    # CURR = (2.24*DAC-30.6) / 3.1
    "eload": lambda curr: (((curr) * 3.1 + 30.6) / 2.24),
    # limit = (9800 * 1.18 / resistor)
    "vddmain_limit": lambda res: (((1.18 / res) * 9800)),
    # limit = (4.75 - 2 * Vout) / 13750 * 15000
    "ppvrect_limit": lambda res: (((13750.0 / 15000.0 * res - 4.75) / (-2.0))),
    # limit = (9800 * 1.18 / resistor)
    "batt_limit": lambda res: (((1.18 / res) * 9800)),
    # Vback = I * 0.1 * 100
    "vddmain_readback": lambda vback: (vback / (0.1 * 100)),
    # Vback = I * 0.1 * 100
    "ppvrect_readback": lambda vback: (vback / (0.1 * 100)),
    # Vback = I * 0.1 * 40.83
    "batt_readback": lambda vback: (vback / (0.1 * 40.83)),
    # Vback = I * 0.1 * 100
    "eload_readback": lambda vback: (vback / (0.1 * 100)),
}


class ArmorException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class ArmorBase(MIXBoard):
    '''
    Base class of Armor and ArmorCompatible.

    Providing common Armor methods.

    Args:
        dac_i2c:                 instance(I2C),  which is used to control ad5667, ad5272 and mcp4725. If not given,
                                                 emulator will be created.
        eeprom_i2c:              instance(I2C),  which is used to control nct75, cat24c32 and pca9536. If not given,
                                                 emulator will be created.

    '''

    rpc_public_api = ['module_init', 'power_output', 'power_enable',
                      'power_disable', 'power_curr_readback', 'resistor_set'] + MIXBoard.rpc_public_api

    def __init__(self, dac_i2c=None, eeprom_i2c=None):

        if dac_i2c:
            self.dac1 = AD5667R(ArmorDef.DAC1_DEV_ADDR, dac_i2c, ArmorDef.DAC_VOLTAGE_REF)
            self.dac2 = AD5667R(ArmorDef.DAC2_DEV_ADDR, dac_i2c, ArmorDef.DAC_VOLTAGE_REF)
            self.dac3 = MCP4725(ArmorDef.DAC3_DEV_ADDR, dac_i2c, ArmorDef.DAC3_VOLTAGE_REF)
            self.res1 = AD5272(ArmorDef.RES_1_ADDR, dac_i2c)
            self.res2 = AD5272(ArmorDef.RES_2_ADDR, dac_i2c)
        else:
            self.dac1 = AD5667REmulator("ad5667r_emulator_1")
            self.dac2 = AD5667REmulator("ad5667r_emulator_2")
            self.dac3 = MCP4725Emulator('mcp4725_emulator')
            self.res1 = AD5272Emulator("ad5272_emulator_1")
            self.res2 = AD5272Emulator("ad5272_emulator_2")

        if eeprom_i2c:
            self.eeprom = CAT24C32(ArmorDef.EEPROM_DEV_ADDR, eeprom_i2c)
            self.sensor = NCT75(ArmorDef.SENSOR_DEV_ADDR, eeprom_i2c)
            MIXBoard.__init__(self, self.eeprom, self.sensor,
                              cal_table=armor_calibration_info, range_table=armor_range_table)
            self.pca9536 = PCA9536(ArmorDef.IO_EXP_DEV_ADDR, eeprom_i2c)
        else:
            self.eeprom = EepromEmulator('eeprom_emulator')
            self.sensor = NCT75Emulator('nct75_emulator')
            MIXBoard.__init__(self, None, None, cal_table=armor_calibration_info, range_table=armor_range_table)
            self.pca9536 = PCA9536Emulator('pca9536_emulator')

    def module_init(self):
        '''
        Init Armor module.

        This function will set pca9536 io direction to output and
        set the AD5667, MCP4725 and AD5272.

        Returns:
            string, "done", api execution successful.

        Examples:
            # GPIO expander directly connected to xavier, not behind i2c-mux:
            power = Armor(...)
            power.board_init()

            # GPIO expander is connected to downstream port of i2c-mux:
            power = Armor(...)
            # some i2c_mux action
            ...
            power.board_init()

        '''

        self.pca9536.set_pins_dir([ArmorDef.IO_SET])
        self.pca9536.set_ports([ArmorDef.IO_SET])
        self.dac1.select_work_mode(ArmorDef.DAC_CHANNEL['ALL'])
        self.dac1.set_reference("EXTERN")
        self.dac2.select_work_mode(ArmorDef.DAC_CHANNEL['ALL'])
        self.dac2.set_reference("EXTERN")
        self.res1.write_command(ArmorDef.RES_CMD_ADDR, ArmorDef.RES_CMD_DATA)
        self.res2.write_command(ArmorDef.RES_CMD_ADDR, ArmorDef.RES_CMD_DATA)
        self.res1.set_work_mode(ArmorDef.RES_WORK_MODE)
        self.res2.set_work_mode(ArmorDef.RES_WORK_MODE)
        self.load_calibration()

        return 'done'

    def power_output(self, channel, output):
        '''
        power board output enable, set the ad5667 output the voltage.

        Args:
            channel:        string,     ['vddmain', 'ppvrect', 'batt', 'eload'], select output source.
            output:         int/float,  [0~8000], Range value, vddmain output range is (0-5000mV),
                                        ppvrect output range is (0-8000mV),
                                        batt    output range is (0-5000mV),
                                        eload   output range is (0-500mA).

        Returns:
            string, "done", api execution successful.

        Examples:
            power.power_output('eload', 300)

        '''
        assert channel in ArmorDef.DAC_CHANNEL_LIST
        assert isinstance(output, (int, float))
        assert output >= ArmorDef.DAC_RANGE_DICT[channel]["min"] and output <= ArmorDef.DAC_RANGE_DICT[channel]["max"]

        if "batt" == channel:
            dac = self.dac1
            dac_channel = ArmorDef.DAC_CHANNEL['B']
        elif "vddmain" == channel:
            dac = self.dac2
            dac_channel = ArmorDef.DAC_CHANNEL['A']
        elif "ppvrect" == channel:
            dac = self.dac2
            dac_channel = ArmorDef.DAC_CHANNEL['B']
        elif "eload" == channel:
            dac = self.dac1
            dac_channel = ArmorDef.DAC_CHANNEL['A']
        else:
            raise ArmorException("channel is error.")

        cal_item = channel
        output = self.calibrate(cal_item, output)
        dac_output = round(formula[channel](output), 3)

        if ArmorDef.MAX_VOLTAGE < dac_output:
            dac_output = ArmorDef.MAX_VOLTAGE
        if ArmorDef.MIN_VOLTAGE > dac_output:
            dac_output = 0

        dac.output_volt_dc(dac_channel, dac_output)

        return "done"

    def power_enable(self, channel):
        '''
        power board output enable, open the ad5667 output the voltage.

        Args:
            channel:    string,     ['vddmain', 'ppvrect', 'batt', 'eload'], select output source.

        Returns:
            string, "done", api execution successful.

        Examples:
            power.power_enable('eload')

        '''

        assert channel in ArmorDef.DAC_CHANNEL_LIST

        if 'batt' == channel:
            pin = ArmorDef.BATT_PIN
        elif "vddmain" == channel:
            pin = ArmorDef.MAIN_PIN
        elif "ppvrect" == channel:
            pin = ArmorDef.RECT_PIN
        elif "eload" == channel:
            pin = None
        else:
            raise ArmorException("channel is error.")

        if pin is not None:
            self.pca9536.set_pin(pin, ArmorDef.ENABLE_LEVEL)

        return "done"

    def power_disable(self, channel):
        '''
        power board output disable, close the ad5667 output the voltage.

        Args:
            channel:    string, ['vddmain', 'ppvrect', 'batt', 'eload'], select output source.

        Returns:
            string, "done", api execution successful.

        Examples:
            power.power_disable('eload')

        '''

        assert channel in ArmorDef.DAC_CHANNEL_LIST

        if 'batt' == channel:
            pin = ArmorDef.BATT_PIN
        elif "vddmain" == channel:
            pin = ArmorDef.MAIN_PIN
        elif "ppvrect" == channel:
            pin = ArmorDef.RECT_PIN
        elif "eload" == channel:
            pin = None
        else:
            raise ArmorException("channel is error.")

        if pin is not None:
            self.pca9536.set_pin(pin, ArmorDef.DISABLE_LEVEL)

        return "done"

    def power_curr_readback(self, channel, voltage):
        '''
        power board readback current

        Args:
            channel:    string,     ['vddmain', 'ppvrect', 'batt', 'eload'],
                                    select channel source.
            voltage:    float/int,  [-6500~6500], Range value, vddmain voltage range is (0-6500mV),
                                        ppvrect voltage range is (0-6500mV),
                                        batt    voltage range is ((-6500)-6500mV),
                                        eload   voltage range is (0-6500mV).

        Returns:
            float, value, back current value, unit mA.

        Examples:
            power.power_curr_readback("vddmain", 1000)
        '''
        assert channel in ArmorDef.ADC_CHANNEL_LIST
        assert isinstance(voltage, (int, float))
        assert voltage >= ArmorDef.ADC_RANGE_DICT[channel]["min"] and voltage <= ArmorDef.ADC_RANGE_DICT[channel]["max"]

        channel = channel + "_readback"
        current = round(formula[channel](voltage), 3)
        return self.calibrate(channel, current)

    def resistor_set(self, channel, limit):
        '''
        power board set the current limit. When calling the interface to set the current limit in the source output,
        the vddmain and batt sources will pull down the current, and the ppvrect source will pull down the voltage.
        These phenomena are determined by the adc chip.

        Args:
            channel:        string,     ['batt', 'vddmain', 'ppvrect'], select the armor board current limit source.
            limit:          float/int,  [300~1200], set the source limit current,unit is mA, batt limit current range is
                                        300-1200mA,vddmain limit current range is 300-500mA, ppvrect limit current range
                                        is 300-500mA.

        Returns:
            string, "done", api execution successful.

        Examples:
            power.resistor_set('batt', 1000)

        '''

        assert channel in ArmorDef.DAC_CHANNEL_LIST
        assert isinstance(limit, (int, float))

        cal_item = channel + '_limit'
        dac_output = self.calibrate(cal_item, limit) / ArmorDef.UNIT_CONVERSION
        output = round(formula[cal_item](dac_output), 4)

        if cal_item == 'batt_limit':
            self.res1.set_resistor(output)
        elif cal_item == 'ppvrect_limit':
            output *= ArmorDef.UNIT_CONVERSION
            self.dac3.output_volt_dc(output)
        else:
            self.res2.set_resistor(output)

        return "done"

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
                'calibration unit memory unit_index data type is not int type or unit_index < 0')

        use_flag = self.calibration_info['use_flag']
        data = (gain, offset, use_flag, 0xff, 0xff, 0xff, 0xff)
        s = struct.Struct(ArmorCoeffDef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(ArmorCoeffDef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = self.calibration_info['unit_start_addr'] + \
            ArmorCoeffDef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)
        return 'done'

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
                'calibration unit memory unit_index data type is not int type or unit_index < 0')

        address = self.calibration_info['unit_start_addr'] + \
            ArmorCoeffDef.CAL_DATA_LEN * unit_index
        data = self.read_eeprom(address, ArmorCoeffDef.READ_CAL_BYTE)

        s = struct.Struct(ArmorCoeffDef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(ArmorCoeffDef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        threshold = 0.0
        for cal_type in armor_calibration_info.keys():
            for level in armor_calibration_info[cal_type].keys():
                if unit_index == armor_calibration_info[cal_type][level]['unit_index']:
                    threshold = armor_calibration_info[cal_type][level]['limit'][0]
                    break

        if self.calibration_info['use_flag'] != result[2]:
            return {'gain': 1.0, 'offset': 0.0, 'threshold': 0, 'is_use': False}
        else:
            return {'gain': result[0], 'offset': result[1], 'threshold': threshold, 'is_use': True}

    def legacy_erase_calibration_cell(self, unit_index):
        '''
        MIXBoard erase calibration unit

        Args:
            unit_index:  int, calibration unit index.

        Returns:
            string, "done", api execution successful.

        Examples:
            board.erase_calibration_cell(0)

        '''

        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                'calibration unit memory unit_index data type is not int type or unit_index < 0')

        data = [0xff for i in range(ArmorCoeffDef.CAL_DATA_LEN)]
        address = self.calibration_info['unit_start_addr'] + \
            ArmorCoeffDef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)
        return 'done'


class Armor(ArmorBase):
    '''
    Power009002 Module is used for output the voltage and set the current limit.

    compatible = ["GQQ-PWR009002-000"]

    Armor(PWR-009) is a high performance digital power module.DAC has a 16-bit resolution, and it has four
    channels: channel 1 is the primary power supply, channel 2 is the standby power supply, channel
    3 is the battery simulation, and channel 4 is e-load, which supports CC mode.In addition, it also has
    over current protection, and the output current over current protection current size can be set.

    Args:
        dac_i2c:        instance(I2C),  which is used to control ad5667, ad5272 and mcp4725. If not given,
                                        emulator will be created.
        eeprom_i2c:     instance(I2C),  which is used to control nct75, cat24c32 and pca9536. If not given,
                                        emulator will be created.


    Examples:

    .. code-block:: python

        dac_i2c = I2C('/dev/i2c-3')
        eeprom_i2c = I2C('/dev/i2c-7')
        armor = ARMOR(dac_i2c, eeprom_i2c)

        # power board output the voltage
        result = armor.module_init()
        result = armor.power_output('batt', 1000)
        armor.power_enable('batt')
        set the source batt (A02) output 1000mV
        return 'done'

        # power board disable output the voltage
        result = armor.module_init()
        result = armor.power_disable('batt')
        disable the source batt (A02) output
        return 'done'

        # power board set the over current protect
        result = armor.module_init()
        result = resistor_set('batt', 5000)
        set the resistor to protect over current
        return 'done'
    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-PWR009002-000"]

    def __init__(self, dac_i2c=None, eeprom_i2c=None):

        super(Armor, self).__init__(dac_i2c, eeprom_i2c)
