# -*- coding: UTF-8 -*-
import time
import struct
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.core.ic.tca9538 import TCA9538
from mix.driver.core.ic.tca9538_emulator import TCA9538Emulator
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667R
from mix.driver.smartgiant.common.ic.ad56x7_emulator import AD56X7REmulator


__author__ = 'zhiwei.deng@SmartGiant'
__version__ = '0.5'


sg2251_calibration_info = {
    "power_output": {
        'level1': {'unit_index': 0, 'limit': (1000, 'mV')},
        'level2': {'unit_index': 1, 'limit': (5000, 'mV')},
        'level3': {'unit_index': 2, 'limit': (10000, 'mV')},
        'level4': {'unit_index': 3, 'limit': (20000, 'mV')}
    },
    "curr_limit": {
        'level1': {'unit_index': 4, 'limit': (1000, 'mA')},
        'level2': {'unit_index': 5, 'limit': (2000, 'mA')},
        'level3': {'unit_index': 6, 'limit': (3000, 'mA')},
        'level4': {'unit_index': 7, 'limit': (5500, 'mA')}
    },
    "volt_measure": {
        'level1': {'unit_index': 8, 'limit': (1000, 'mV')},
        'level2': {'unit_index': 9, 'limit': (5000, 'mV')},
        'level3': {'unit_index': 10, 'limit': (10000, 'mV')},
        'level4': {'unit_index': 11, 'limit': (20000, 'mV')}
    },
    "curr_measure": {
        'level1': {'unit_index': 12, 'limit': (1000, 'mA')},
        'level2': {'unit_index': 13, 'limit': (2000, 'mA')},
        'level3': {'unit_index': 14, 'limit': (3000, 'mA')},
        'level4': {'unit_index': 15, 'limit': (5500, 'mA')}
    }
}

sg2251_range_table = {
    'power_output': 0,
    'curr_limit': 1,
    'volt_measure': 2,
    'curr_measure': 3
}


formula = {
    # the formula Provided by hardware engineer
    "power_output": lambda volt: ((volt + 0.044) / 4.444),
    "curr_limit": lambda curr: ((curr + 0.011) / 1.155),
    "volt_measure": lambda volt: (volt / 0.2273),
    "curr_measure": lambda volt: (volt / 0.8942),
}


class SG2251PW01PCADef:
    DAC_CLR_PIN = 0
    PWR_CONTROL_PIN = 1
    PWR_STATE = {
        'on': 0,
        'off': 1
    }
    RANGE = {
        'volt': {"min": 0, 'max': 20000},
        'curr_limit': {"min": 0, 'max': 5500}
    }
    DAC_CHANNEL = {
        'volt': 0,
        'curr_limit': 1
    }
    DAC_ADDR = 0x0F
    DAC_REF_VOLT = 5000
    EEPROM_DEV_ADDR = 0x53
    NCT75_DEV_ADDR = 0x4a
    IO_EXP_ADDR = 0x73
    CAL_DATA_LEN = 12
    WRITE_CAL_DATA_PACK_FORMAT = "2f4B"
    WRITE_CAL_DATA_UNPACK_FORMAT = "12B"

    READ_CAL_BYTE = 12
    READ_CAL_DATA_PACK_FORMAT = "12B"
    READ_CAL_DATA_UNPACK_FORMAT = "2f4B"


class SG2251PW01PCAException(Exception):
    def __init__(self, err_str):
        self.reason = '%s' % (err_str)

    def __str__(self):
        return self.reason


class SG2251PW01PCA(MIXBoard):
    '''
    SG2251PW01PCA is a PSU, output volt range is 0~20V, current range is 0-5.5A.

    compatible = ["GQQ-SG2251PW01PCA-000"]

    Args:
        i2c:             instance(I2C)/None, which is used to control nct75/cat24c32/DAC. If not given,
                                             emulator will be created.

    Examples:
        Example for init class:
            i2c = I2C('/dev/i2c-1')
            psu = SG2251PW01PCA(i2c)

        Example for output 5v volt:
            psu.power_output('volt', 5000)
            psu.power_control('on')

    '''
    compatible = ["GQQ-PW01-000"]

    rpc_public_api = ['module_init', 'power_output', 'set_current_limit',
                      'power_readback_voltage_calc', 'power_readback_current_calc',
                      'power_control', 'power_step_output'] + MIXBoard.rpc_public_api

    def __init__(self, i2c):

        if i2c:
            self.eeprom = CAT24C32(SG2251PW01PCADef.EEPROM_DEV_ADDR, i2c)
            self.sensor = NCT75(SG2251PW01PCADef.NCT75_DEV_ADDR, i2c)
            self.dac = AD5667R(SG2251PW01PCADef.DAC_ADDR, i2c, "EXTERN", SG2251PW01PCADef.DAC_REF_VOLT)
            self.io_expand = TCA9538(SG2251PW01PCADef.IO_EXP_ADDR, i2c)
        else:
            self.eeprom = EepromEmulator("cat24cxx_emulator")
            self.sensor = NCT75Emulator("nct75_emulator")
            self.dac = AD56X7REmulator(SG2251PW01PCADef.DAC_ADDR)
            self.io_expand = TCA9538Emulator(SG2251PW01PCADef.IO_EXP_ADDR)

        super(SG2251PW01PCA, self).__init__(self.eeprom, self.sensor,
                                            cal_table=sg2251_calibration_info,
                                            range_table=sg2251_range_table)

    def module_init(self):
        '''
        SG2251PW01PCA module init.

        Returns:
            string, "done", api execution successful.

        Raise:
            SG2251PW01PCAException:  If volt is invalid, exception will be raised.

        Examples:
            sg2251pw01pca.module_init()
        '''
        self.load_calibration()
        self.io_expand.set_pin_dir(SG2251PW01PCADef.DAC_CLR_PIN, "output")
        self.io_expand.set_pin_dir(SG2251PW01PCADef.PWR_CONTROL_PIN, "output")
        self.io_expand.set_pin(SG2251PW01PCADef.DAC_CLR_PIN, 0)
        time.sleep(0.1)
        self.io_expand.set_pin(SG2251PW01PCADef.DAC_CLR_PIN, 1)
        self.io_expand.set_pin(SG2251PW01PCADef.PWR_CONTROL_PIN, SG2251PW01PCADef.PWR_STATE['off'])
        self.dac.reset()
        self.power_dac_volt = 0
        return 'done'

    def power_output(self, volt):
        '''
        SG2251PW01PCA set volt

        Args:
            volt: float, [0-20000] Set specific volt value.

        Returns:
            string, "done", api execution successful.

        Raise:
            SG2251PW01PCAException:  If volt is invalid, exception will be raised.

        Examples:
            sg2251pw01pca.power_output(10000)
        '''

        assert SG2251PW01PCADef.RANGE["volt"]['min'] <= volt <= SG2251PW01PCADef.RANGE["volt"]['max']

        volt = self.calibrate('power_output', volt)
        volt = formula["power_output"](volt)
        self.dac.output_volt_dc(SG2251PW01PCADef.DAC_CHANNEL["volt"], volt)

        # readback voltage and save
        self.power_dac_volt = self.dac.read_volt(SG2251PW01PCADef.DAC_CHANNEL["volt"])

        return 'done'

    def set_current_limit(self, curr):
        '''
        SG2251PW01PCA set current limit value

        Args:
            curr: float, [0-5500] Set specific current limit value.

        Returns:
            string, "done", api execution successful.

        Raise:
            SG2251PW01PCAException:  If curr is invalid, exception will be raised.

        Examples:
            sg2251pw01pca.set_current_limit(4000)
        '''

        assert SG2251PW01PCADef.RANGE["curr_limit"]['min'] <= curr <= SG2251PW01PCADef.RANGE["curr_limit"]['max']

        curr = self.calibrate('curr_limit', curr)
        curr = formula["curr_limit"](curr)
        self.dac.output_volt_dc(SG2251PW01PCADef.DAC_CHANNEL["curr_limit"], curr)

        return 'done'

    def power_readback_voltage_calc(self, volt):
        '''
        Calculate and calibrate readback power voltage.

        Args:
            volt:    float, ADC read back voltage, unit mV.

        Returns:
            float, unit mV, voltage value.

        Examples:
            volt = sg2251pw01pca.power_readback_voltage(1000)

        '''
        assert isinstance(volt, (int, float))
        voltage = formula["volt_measure"](volt)
        return self.calibrate("volt_measure", voltage)

    def power_readback_current_calc(self, volt):
        '''
        Calculate and calibrate readback power current.

        Args:
            volt:    float, ADC read back current, unit mA.

        Returns:
            float, unit mA, current volt.

        Examples:
            volt = sg2251pw01pca.power_readback_current(1000)

        '''
        assert isinstance(volt, (int, float))
        current = formula["curr_measure"](volt)
        return self.calibrate("curr_measure", current)

    def power_control(self, state):
        '''
        SG2251PW01PCA on/off power board output

        Args:
            channel: string, ['on','off'], Select specific state.

        Returns:
            string, "done", api execution successful.

        Raise:
            SG2251PW01PCAException:  If state is invalid, exception will be raised.

        Examples:
            sg2251pw01pca.power_control('on')
        '''
        assert state in SG2251PW01PCADef.PWR_STATE

        self.io_expand.set_pin(SG2251PW01PCADef.PWR_CONTROL_PIN, SG2251PW01PCADef.PWR_STATE[state])

        return "done"

    def power_step_output(self, volt, step_volt, step_delay=0):
        '''
        SG2251PW01PCA set volt step by step

        Args:
            volt:       float, [0-20000]    End voltage, unit is mV.
            step_volt:  float, [0-20000]    Step voltage, unit is mV.
            step_delay: float, [0-1.0]      Step delay between step, unit is second, default=0.

        Returns:
            string, "done", api execution successful.

        Raise:
            SG2251PW01PCAException:  If volt is invalid, exception will be raised.

        Examples:
            sg2251pw01pca.power_step_output(12000, 1000, 0.001)

        '''
        assert isinstance(volt, (int, float))
        assert SG2251PW01PCADef.RANGE["volt"]['min'] <= volt <= SG2251PW01PCADef.RANGE["volt"]['max']
        assert isinstance(step_volt, (int, float))
        assert SG2251PW01PCADef.RANGE["volt"]['min'] <= step_volt <= SG2251PW01PCADef.RANGE["volt"]['max']
        assert isinstance(step_delay, (int, float))
        assert 0 <= step_delay <= 1.0

        volt = self.calibrate('power_output', volt)
        end_volt = formula["power_output"](volt)
        step_volt = formula["power_output"](step_volt)
        start_volt = self.power_dac_volt

        sign = 1 if end_volt > start_volt else -1  # flag, voltage increase by step if sign=1, or decrease
        volt_list = [start_volt + i * sign * step_volt for i in range(0, int(abs(end_volt - start_volt) / step_volt))]
        volt_list.append(end_volt)

        # output
        for volt in volt_list:
            self.dac.output_volt_dc(SG2251PW01PCADef.DAC_CHANNEL["volt"], volt)
            step_delay and time.sleep(step_delay)

        self.power_dac_volt = self.dac.read_volt(SG2251PW01PCADef.DAC_CHANNEL["volt"])

        return 'done'

    def legacy_write_calibration_cell(self, unit_index, gain, offset):
        '''
        MIXBoard calibration data write

        Args:
            unit_index:   int,    calibration unit index.
            gain:         float,  calibration gain.
            offset:       float,  calibration offset.

        Examples:
             board.write_calibration_cel(0, 1.1, 0.1, 100)

        Raise:
            BoardArgCheckError:  unit_index data type is not int type or unit_index < 0.
            calibration unit format:
                Meaning:    Gain,     Offset,   threshold value, Use flag
                Mem size:   4Bytes,   4Bytes,   4Bytes,            Byte
                Data type:  float,    float,    float,            uint8_t
                Formula:    Y = Gain * X  + Offset
        '''

        if not isinstance(unit_index, int) or unit_index < 0:
            raise SG2251PW01PCAException(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        use_flag = self.calibration_info["use_flag"]
        data = (gain, offset, use_flag, 0xff, 0xff, 0xff)
        s = struct.Struct(SG2251PW01PCADef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(SG2251PW01PCADef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = self.calibration_info["unit_start_addr"] + \
            SG2251PW01PCADef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)

        return "done"

    def legacy_read_calibration_cell(self, unit_index):
        '''
        MIXBoard read calibration data

        Args:
            unit_index: int, calibration unit index.

        Examples:
            data = board.read_calibration_cel(0)
            print(data)

        Raise:
            BoardArgCheckError:  unit_index data type is not int type or unit_index < 0.
            calibration unit format:
                Meaning:    Gain,     Offset,   threshold value, Use flag
                Mem size:   4Bytes,   4Bytes,   4Bytes,            Byte
                Data type:  float,    float,    float,            uint8_t
                Formula:    Y = Gain * X  + Offset

        Returns:
            dict:           {"gain": value, "offset": value, "threshold": value, "is_use": value}
        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise SG2251PW01PCAException(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        address = self.calibration_info["unit_start_addr"] + \
            SG2251PW01PCADef.CAL_DATA_LEN * unit_index
        data = self.read_eeprom(address, SG2251PW01PCADef.READ_CAL_BYTE)

        s = struct.Struct(SG2251PW01PCADef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(SG2251PW01PCADef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        threshold = 0.0
        for cal_item in sg2251_calibration_info:
            for level in sg2251_calibration_info[cal_item]:
                if unit_index == sg2251_calibration_info[cal_item][level]["unit_index"]:
                    threshold = sg2251_calibration_info[cal_item][level]["limit"][0]
                    break

        if self.calibration_info["use_flag"] != result[2]:
            return {"gain": 1.0, "offset": 0.0, "threshold": threshold, "is_use": True}
        else:
            return {"gain": result[0], "offset": result[1], "threshold": threshold, "is_use": True}

    def legacy_erase_calibration_cell(self, unit_index):
        '''
        MIXBoard erase calibration unit

        Args:
            unit_index: int, calibration unit index.

        Examples:
            board.erase_calibration_cell(0)

        '''

        if not isinstance(unit_index, int) or unit_index < 0:
            raise SG2251PW01PCAException(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        data = [0xff for i in range(SG2251PW01PCADef.CAL_DATA_LEN)]
        address = self.calibration_info["unit_start_addr"] + SG2251PW01PCADef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)

        return "done"
