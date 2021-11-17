# -*- coding: utf-8 -*-
import time
import math
import struct
from mix.driver.core.ic.cat24cxx import CAT24C64
from mix.driver.smartgiant.common.ic.max6642 import MAX6642
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver


__author__ = 'tufeng.mao@SmartGiant'
__version__ = 'V0.0.1'


class SPILLException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


spill_range_table = {
    'a_volt': 0,
    'b_volt': 1,
    'a_sink_curr': 2,
    'b_sink_curr': 3,
    'a_src_curr': 4,
    'b_src_curr': 5,
    'a_rem_volt': 6,
    'b_rem_volt': 7,
    'max_set_volt': 8,
    'min_set_volt': 9,
    'max_set_vgap': 10,
    'min_set_vgap': 11,
    'a_set_rint': 12,
    'b_set_rint': 13
}


class SPILLDef:
    TIMEOUT = 1  # s
    LOCAL_OT = 90  # Celsius
    REMOTE_OT = 90  # Celsius
    EEPROM_DEV_ADDR = 0x53
    SENSOR_DEV_ADDR = 0x48
    LTC2606_DEV_ADDR = 0x30

    # Calibration Coefficients Map
    CALIBRATION_COE_MAP = {
        'a_volt': [0x0500, 0x0503],
        'b_volt': [0x0508, 0x050B],
        'a_sink_curr': [0x0530, 0x0540],
        'b_sink_curr': [0x0538, 0x0548],
        'a_src_curr': [0x0510, 0x0520],
        'b_src_curr': [0x0518, 0x0528],
        'a_rem_volt': [0x0550, 0x0553],
        'b_rem_volt': [0x0558, 0x055B],
        'max_set_volt': [0x0560, 0x0563],
        'min_set_volt': [0x0568, 0x056B],
        'max_set_vgap': [0x0570, 0x0573],
        'min_set_vgap': [0x0578, 0x057B],
        'a_set_rint': [0x0580, 0x0583],
        'b_set_rint': [0x0588, 0x058B]
    }
    CAL_CELL_LEN = 4
    LATEST_CAL = -1


class SPILL(SGModuleDriver):
    '''
    Spill is part of Storm (Battery Emulator), and Storm is a bi-directional DC power supply.

    compatible = ["GQQ-MJ28-5-030"]

    Args:
        i2c:                 instance(I2C), Class instance of I2C, which is used to access
                                                 CAT24C64, LTC2606, MAX6642.

    '''

    rpc_public_api = ['get_temperature', 'read_high_limit',
                      'write_high_limit', 'set_rint'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c):
        self.max6642 = MAX6642(SPILLDef.SENSOR_DEV_ADDR, i2c)
        self.eeprom = CAT24C64(SPILLDef.EEPROM_DEV_ADDR, i2c)
        self.i2c = i2c
        super(SPILL, self).__init__(self.eeprom, None, range_table=spill_range_table)

    def post_power_on_init(self, timeout=SPILLDef.TIMEOUT):
        '''
        Init module to a know harware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''

        self.reset(timeout)

    def reset(self, timeout=SPILLDef.TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                self.load_calibration()
                self.write_high_limit("local", SPILLDef.LOCAL_OT)
                self.write_high_limit("remote", SPILLDef.REMOTE_OT)
                # write default battery Rint = 125mΩ
                self.i2c.write(SPILLDef.LTC2606_DEV_ADDR, [SPILLDef.LTC2606_DEV_ADDR, 0x20, 0x00])
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise SPILLException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def get_temperature(self, channel, extended=True):
        '''
        MAX6642 read local or remote temperature, chose to read extended resolution.

        Args:
            channel:    string, ['local', 'remote'], temperature sensor channel.
            extended:   boolean, [True, False], default True, enable or disable extended resolution.

        Returns:
            int/float, value, unit °C.

        '''
        assert channel in ['local', 'remote']
        assert isinstance(extended, bool)

        val = self.max6642.get_temperature(channel, extended)
        return [val, 'Celsius']

    def read_high_limit(self, channel):
        '''
        MAX6642 read local or remote high limit.

        Args:
            channel:    string, ['local', 'remote'], temperature sensor channel.

        Returns:
            list,   [value, 'Celsius'].
        '''
        assert channel in ['local', 'remote']

        val = self.max6642.read_high_limit(channel)
        return [val, 'Celsius']

    def write_high_limit(self, channel, limit):
        '''
        MAX6642 write local or remote high limit.
        The intended measuring range for the MAX6642 is 0 to +150 (Celsius).
        However, the limit is an 8 bit unsigned number and can be set between 0 and +255.

        Args:
            channel:    string, ['local', 'remote'], temperature sensor channel.
            limit:      int, [0~255], temperature limit.

        Returns:
            string, "done", "done" for success
        '''
        assert channel in ['local', 'remote']
        assert isinstance(limit, int) and 0 <= limit <= 0xff

        self.max6642.write_high_limit(channel, limit)
        return "done"

    def set_rint(self, resistance):
        '''
        Set the emulated battery internal resistance for sinking the current.

        Args:
            resistance:    float/int, [0.01~1], unit ohm, battery internal resistance to set value in ohm.

        Returns:
            string, "done", "done" for success
        '''
        assert 0.01 <= resistance <= 1
        assert isinstance(resistance, (int, float))

        cdw_v = 65535 * resistance / 1.2
        cdw_v = int(cdw_v)
        byte1 = (cdw_v >> 8) & 255
        byte2 = cdw_v & 255
        self.i2c.write(SPILLDef.LTC2606_DEV_ADDR, [SPILLDef.LTC2606_DEV_ADDR, byte1, byte2])

        return "done"

    def write_calibration_item(self, cal_index, range_name, index, gain, offset):
        '''
        Write calibration data defined in ICI spec 2.8.4. This is private function.

        The formula is below result = gain * raw_data + offset

        Args:
            cal_index:      int, (>=0), the index in the range to calibration item
            range_name:     string, which range to write
            index:          int, (>=0), the index in the range to write data
            gain:           float, gain value
            offset:         float, offset value

        Returns:
            string, "done", "done" for success
        '''
        assert cal_index >= 0
        assert range_name in self._range_table
        assert index >= 0

        gain = float(gain) - 1
        if range_name in ["a_volt", "a_sink_curr", "a_src_curr", "a_rem_volt", "a_set_rint"]:
            w_data = gain
        elif range_name in ["max_set_volt", "max_set_vgap", "b_volt", "b_sink_curr",
                            "b_src_curr", "min_set_volt", "b_rem_volt", "min_set_vgap", "b_set_rint"]:
            w_data = offset
        else:
            raise SPILLException("Range {} is invalid".format(range_name))

        addr = SPILLDef.CALIBRATION_COE_MAP[range_name][index]
        s = struct.Struct("f")
        pack_data = s.pack(w_data)
        s = struct.Struct("4B")
        data = s.unpack(pack_data)
        self.write_nvmem(addr, data)
        return "done"

    def read_calibration_item(self, cal_index, range_name, index):
        '''
        Read calibration data defined by ICI spec 2.8.4. This is private function.

        Args:
            cal_index:      int, (>=0), the index in the range to calibration item
            range_name:     string, range name which range to read
            index:          int, (>=0), the calibration data index to read in current range

        Returns:
            dict:           {"gain": value, "offset": value}
        '''
        assert cal_index >= 0
        assert range_name in self._range_table
        assert index >= 0

        addr = SPILLDef.CALIBRATION_COE_MAP[range_name][index]
        data = self.read_nvmem(addr, SPILLDef.CAL_CELL_LEN)

        s = struct.Struct("4B")
        pack_data = s.pack(*data)

        s = struct.Struct("f")
        result = s.unpack(pack_data)

        if range_name in ["a_volt", "a_sink_curr", "a_src_curr", "a_rem_volt", "a_set_rint"]:
            gain = result[0]
            offset = 0.0
        elif range_name in ["max_set_volt", "max_set_vgap", "b_volt", "b_sink_curr",
                            "b_src_curr", "min_set_volt", "b_rem_volt", "min_set_vgap", "b_set_rint"]:
            gain = 0.0
            offset = result[0]

        if math.isnan(gain):
            gain = 1.0
        else:
            gain += 1.0
        if math.isnan(offset):
            offset = 0.0
        else:
            offset = offset

        return {"gain": gain, "offset": offset}

    def calibrate(self, range_name, data, level):
        '''
        This function is used to calibrate data. This is private function.

        Args:
            range_name:     string, which range used to do calibration
            data:           float, raw data which need to be calibrated.
            level:          int, calibration level index.

        Returns:
            float:          calibrated data
        '''
        if not self.is_use_cal_data():
            return data

        if self._cal_common_error is not None:
            raise self._cal_common_error

        if range_name in self._range_err_table:
            raise self._range_err_table[range_name]

        assert range_name in self._calibration_table
        items = self._calibration_table[range_name]
        if len(items) == 0:
            return data

        return items[level]['gain'] * data + items[level]['offset']

    def load_calibration(self, calibration_cell_index=SPILLDef.LATEST_CAL):
        '''
        Load ICI calibration data. This is private function.

        This function is used to load calibration data defined by ICI Spec 2.8.4

        Args:
            calibration_cell_index: int, default -1, the desired index from module NVMEM to use for calibration.
            Valid values are -1, and 0 through the number of supported calibrations for that module. See
            MIXModuleDriver.read_number_supported_calibrations() for information on querying the supported number of
            calibrations. A value of -1 should use the newest calibration cell.

        Returns:
            string, "done", "done" for success
        '''
        self._calibration_table = {}
        self._cal_common_error = None
        self._range_err_table = {}

        if calibration_cell_index == SPILLDef.LATEST_CAL:
            try:
                cal_index = self.read_latest_calibration_index()
            except Exception as e:
                self._cal_common_error = SPILLException(str(e))
                return "done"
        else:
            cal_index = calibration_cell_index

        try:
            read_data = self.read_calibration_cell(cal_index)
        except Exception as e:
            self._cal_common_error = SPILLException("Read calibration cell error: " + str(e))
            return "done"

        self.cal_index = cal_index

        data_size = self._get_cal_size(cal_index)
        start_address = self._get_cal_address(cal_index)

        for range_name, index in self._range_table.items():
            self._calibration_table[range_name] = []
            cal_item_addr = SPILLDef.CALIBRATION_COE_MAP[range_name][0]
            cal_pos = cal_item_addr - start_address
            # check cal_pos range
            if cal_pos < 0 or cal_pos >= data_size:
                err_info = SPILLException("Range {} count pos 0x{:x} is invalid".format(range_name, cal_pos))
                self._range_err_table[range_name] = err_info
                continue
            count = len(SPILLDef.CALIBRATION_COE_MAP[range_name])
            cal_len = count * SPILLDef.CAL_CELL_LEN
            cal_data = read_data[cal_pos:(cal_pos + cal_len)]

            for i in range(count):
                if range_name in ["a_src_curr", "b_src_curr", "a_sink_curr", "b_sink_curr"]:
                    item_pos = SPILLDef.CALIBRATION_COE_MAP[range_name][i] - start_address
                    data = read_data[item_pos:(item_pos + SPILLDef.CAL_CELL_LEN)]
                else:
                    item_pos = i * SPILLDef.CAL_CELL_LEN
                    data = cal_data[item_pos:(item_pos + SPILLDef.CAL_CELL_LEN)]

                s = struct.Struct("4B")
                pack_data = s.pack(*data)

                s = struct.Struct("f")
                result = s.unpack(pack_data)

                if range_name in ["a_volt", "a_sink_curr", "a_src_curr", "a_rem_volt", "a_set_rint"]:
                    gain = result[0]
                    offset = 0.0
                elif range_name in ["max_set_volt", "max_set_vgap", "b_volt", "b_sink_curr",
                                    "b_src_curr", "min_set_volt", "b_rem_volt", "min_set_vgap", "b_set_rint"]:
                    gain = 0.0
                    offset = result[0]

                if math.isnan(gain):
                    gain = 1.0
                else:
                    gain += 1.0
                if math.isnan(offset):
                    offset = 0.0
                else:
                    offset = offset

                self._calibration_table[range_name].append({"gain": gain, "offset": offset})
        return "done"
