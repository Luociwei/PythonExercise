# -*- coding: utf-8 -*-
import struct
import copy
from datetime import datetime
from mix.driver.core.module.mixmodulehelper import BytesHelper
from mix.driver.core.module.mixmoduledriver import MIXModuleDriver
from mix.driver.core.module.mixmodulenvmem import NVMemFieldNames
from mix.driver.smartgiant.common.module.mixmoduleerror import (InvalidCalibrationIndex, InvalidCalibrationCell)

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


class CalibrationDef:
    CAL_COUNT_LEN = 1
    CAL_VERSION_SIZE = 1
    CAL_RANGE_LEN = 2
    CAL_CELL_LEN = 16
    CAL_SAVE_FLAG = 0x5A
    MAJOR_VERSION = 0x01
    NUM_CALS_ADDR = 0x18
    RO_Checksum_ADDR = 0x2C
    LATEST_CAL = -1

Cal_DateTime_ADDR = lambda index: 0x40 + index * 0x25
Cal_StartAddr_ADDR = lambda index: 0x49 + index * 0x25
Cal_DataSize_ADDR = lambda index: 0x4D + index * 0x25
Cal_CheckSum_ADDR = lambda index: 0x51 + index * 0x25


class BoardOperationError(Exception):
    '''When the board have the hardware operation error, use this raise
    '''

    def __init__(self, err):
        Exception.__init__(
            self, "[SGModuleDriver operation exception] %s" % (err))


class BoardArgCheckError(Exception):
    '''Check parameter results do not conform to the function afferent specification, use this raise
    '''

    def __init__(self, err):
        Exception.__init__(
            self, "[SGModuleDriver arg check exception] %s" % (err))


class ICIException(Exception):
    pass


def leastsq(x, y):
    meanx = sum(x) / (len(x) * 1.0)
    meany = sum(y) / (len(y) * 1.0)

    xsum = 0.0
    ysum = 0.0

    for i in range(len(x)):
        xsum += (x[i] - meanx) * (y[i] - meany)
        ysum += (x[i] - meanx) ** 2

    k = xsum * 1.0 / ysum
    b = meany - k * meanx

    return k, b


class SGModuleDriver(MIXModuleDriver):
    '''
    SGModuleDriver function class, this is all board parent

    Args:
        eeprom:             instance(EEPROM)/None, Eeprom class instance, if None, will create emulator.
        temperature_device: instance(SENSOR)/None, Temperature class instance, if None will create emulator.
        range_table:        dict, which is ICI calibration range table.

    Examples:
        class SCOPE002004(SGModuleDriver):
            def __init__(self, ad7177=None, eeprom=None, nct75=None):
                SGModuleDriver.__init__(self, eeprom, nct75)
    '''

    rpc_public_api = ['eeprom_read_string', 'get_calibration_mode',
                      'set_calibration_mode', 'load_calibration', 'calibrate',
                      # ici spec 2.8.4
                      'reset', 'read_nvmem', 'get_driver_version', 'read_vendor',
                      'read_EEEE_code', 'read_hardware_version', 'read_number_supported_calibrations',
                      'read_ers_version', 'read_hardware_config', 'read_serial_number',
                      'read_nvmem_size', 'read_production_date', 'read_production_count',
                      'read_latest_calibration_index', 'write_calibration_cell', 'read_calibration_cell',
                      'read_calibration_date', 'read_user_area', 'write_user_area',
                      'write_module_calibration',
                      # function defined by SG
                      'read_calibration_item', 'get_ranges_name', 'read_temperature',
                      'enable_calibration', 'disable_calibration', 'get_active_calibration_index'
                      ] + MIXModuleDriver.rpc_public_api

    def __init__(self, eeprom=None, temperature_device=None, range_table={}):
        self._calibration_table = {}
        self._eeprom_device = eeprom
        self._temperature_device = temperature_device
        self._cal_mode_flag = 'cal'

        self._range_err_table = {}
        self._cal_common_error = None
        super(SGModuleDriver, self).__init__()
        self._range_table = self._get_range_table(range_table)
        self.load_calibration()

    def _get_range_table(self, range_table):
        if isinstance(range_table, dict):
            return range_table
        elif isinstance(range_table, list):
            cal_start_addr = self._get_cal_address()
            version = self.read_nvmem(cal_start_addr, 1)[0]
            major_version = (version >> 4) & 0xF
            minor_version = (version & 0xF)
            if major_version != CalibrationDef.MAJOR_VERSION:
                raise ICIException("Calibration major version 0x{:x}"
                                   " does not match 0x{:}".format(CalibrationDef.MAJOR_VERSION))
            for table in range_table:
                version = table.pop('version')
                if version == minor_version:
                    return table
            raise ICIException("No minor version 0x{:x} is matched in range table".format(minor_version))
        else:
            raise ICIException("Range table type invalid")

    def read_nvmem(self, address, count):
        '''
        this should return a bytearray object representing the data

        Args:
            address:        int, (>=0), the start address to read data
            count:          int, (>0), number bytes to read of data

        Returns:
            bytearray, data has been read
        '''
        return bytearray(self._eeprom_device.read(address, count))

    def write_nvmem(self, address, data):
        '''
        data should be a byte array object

        Args:
            address:        int, (>=0), the start address to write data
            data:           bytearray, the data to be write
        '''
        return self._eeprom_device.write(address, list(data))

    def read_temperature(self):
        '''
        Read module temperature.

        Returns:
            float, temperature value
        '''
        if not self._temperature_device:
            raise BoardOperationError('The module does not support read temperature')
        return self._temperature_device.get_temperature()

    def get_calibration_mode(self):
        '''
        SGModuleDriver get calibration mode

        Examples:
            mode = board.mode
            print(mode)

        '''
        return self._cal_mode_flag

    def set_calibration_mode(self, mode):
        '''
        SGModuleDriver set calibration mode

        Args:
            mode:   string, ['cal', 'raw'], 'cal' enable calibration, 'raw': disable calibration.

        Examples:
            board.mode = 'cal'

        '''
        assert mode in ['cal', 'raw']
        self._cal_mode_flag = mode

    def is_use_cal_data(self):
        '''
        SGModuleDriver check whether the current mode is a calibration mode

        Examples:
            if board.is_use_cal_data:
                print('Use calibration data')
            else:
                print('Not use calibration data')

        '''

        if self._cal_mode_flag != 'raw':
            return True
        else:
            return False

    def _get_cal_address(self, cal_index):
        return self.nvmem[NVMemFieldNames.CAL_DATA_START_ADDR][cal_index]

    def _get_cal_size(self, cal_index):
        return self.nvmem[NVMemFieldNames.CAL_DATA_SIZE][cal_index]

    def load_calibration(self, calibration_cell_index=CalibrationDef.LATEST_CAL):
        '''
        Load ICI calibration data.

        This function is used to load calibration data defined by ICI Spec 2.8.4

        Args:
            calibration_cell_index: int, the desired index from module NVMEM to use for calibration. Valid values
            are -1, and 0 through the number of supported calibrations for that module. See
            MIXModuleDriver.read_number_supported_calibrations() for information on querying the supported number of
            calibrations. A value of -1 should use the newest calibration cell.

        Returns:
            string, "done", "done" for success
        '''
        self._calibration_table = {}
        self._cal_common_error = None
        self._range_err_table = {}

        if calibration_cell_index == CalibrationDef.LATEST_CAL:
            try:
                cal_index = self.read_latest_calibration_index()
            except Exception as e:
                self._cal_common_error = ICIException(str(e))
                return "done"
        else:
            cal_index = calibration_cell_index

        try:
            read_data = self.read_calibration_cell(cal_index)
        except Exception as e:
            self._cal_common_error = ICIException("Read calibration cell error: " + str(e))
            return "done"

        self.cal_index = cal_index

        data_size = self._get_cal_size(cal_index)
        start_address = self._get_cal_address(cal_index)

        for range_name, index in self._range_table.items():
            self._calibration_table[range_name] = []
            range_pos = CalibrationDef.CAL_VERSION_SIZE + index * CalibrationDef.CAL_RANGE_LEN
            # check range_pos range
            if range_pos >= data_size:
                err_info = ICIException("Range {} range pos 0x{:x} is invalid".format(range_name, range_pos))
                self._range_err_table[range_name] = err_info
                continue

            range_pos_high = read_data[range_pos]
            range_pos_low = read_data[range_pos + 1]
            range_addr = (range_pos_high << 8) | range_pos_low
            count_pos = range_addr - start_address
            # check count_pos range
            min_size = (len(self._range_table) * CalibrationDef.CAL_RANGE_LEN + CalibrationDef.CAL_VERSION_SIZE)
            if count_pos < min_size or count_pos >= data_size:
                err_info = ICIException("Range {} count pos 0x{:x} is invalid".format(range_name, count_pos))
                self._range_err_table[range_name] = err_info
                continue
            count = read_data[count_pos]
            cal_pos = count_pos + CalibrationDef.CAL_COUNT_LEN
            cal_len = count * CalibrationDef.CAL_CELL_LEN
            cal_data = read_data[cal_pos:(cal_pos + cal_len)]

            for i in range(count):
                item_pos = i * CalibrationDef.CAL_CELL_LEN
                data = cal_data[item_pos:(item_pos + CalibrationDef.CAL_CELL_LEN)]

                s = struct.Struct('16B')
                pack_data = s.pack(*data)

                s = struct.Struct('3f4B')
                result = s.unpack(pack_data)
                if result[3] != CalibrationDef.CAL_SAVE_FLAG:
                    self._calibration_table[range_name].append({'gain': 1.0, "offset": 0.0,
                                                                "threshold": 0.0, "is_use": False})
                else:
                    self._calibration_table[range_name].append({"gain": result[0], "offset": result[1],
                                                                "threshold": result[2], "is_use": True})
        return "done"

    def calibrate(self, range_name, data):
        '''
        This function is used to calibrate data.

        Args:
            range_name:     string, which range used to do calibration
            data:           float, raw data which need to be calibrated.

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

        level = 0
        for i in range(len(items)):
            if data < items[i]['threshold']:
                level = i
                break
            if not items[i]['is_use']:
                break
            level = i

        return items[level]['gain'] * data + items[level]['offset']

    def eeprom_read_string(self, addr, rd_len):
        '''
        Read string from eeprom specific address.

        Args:
            addr:   hex, (>0), the address to read data.
            rd_len: int, (>0), length of data to be read.

        Returns:
            string: string data.
        '''
        rd_data = self.read_nvmem(addr, rd_len)
        result = ""
        for data in rd_data:
            if data == 0x00:
                break
            # Ascii print char is between ' ' and '~'
            if data < ord(' ') or data > ord('~'):
                result += '?'
            else:
                result += chr(data)
        return result

    def eeprom_write_string(self, addr, data):
        '''
        Write string to eeprom.

        Args:
            addr:   hex, (>0), the address to write string.
            data:   string, the string data to be write.

        Returns:
            string, "done", "done" for success
        '''
        assert isinstance(data, basestring)
        data = [ord(ch) for ch in data]
        for ch in data:
            if ch < ord(' ') or ch > ord('~'):
                raise BoardArgCheckError("Data 0x{:x} is not printable".format(ch))
        self.write_nvmem(addr, data)
        return "done"

    def _get_cal_item_addr(self, cal_index, range_name, index):
        '''
        Get calibration cell address defined by ICI spec 2.7

        Args:
            cal_index:      int, (>=0), the index in the range to calibration item
            range_name:     string, range name, which is defined in module driver
            index:          int, (>=0), the index in the table of current range.

        Returns:
            int:            (>=0), calibration cell address.
        '''
        # get calibration base address
        cal_size = self.nvmem[NVMemFieldNames.CAL_DATA_SIZE][cal_index]
        base_addr = self.nvmem[NVMemFieldNames.CAL_DATA_START_ADDR][cal_index] + CalibrationDef.CAL_VERSION_SIZE

        # get range address
        addr = base_addr + self._range_table[range_name] * CalibrationDef.CAL_RANGE_LEN
        data = self.read_nvmem(addr, 2)
        # get item count address
        addr = (data[0] << 8) | data[1]
        count_pos = addr - base_addr + CalibrationDef.CAL_VERSION_SIZE
        # check count_pos range
        min_size = (len(self._range_table) * CalibrationDef.CAL_RANGE_LEN + CalibrationDef.CAL_VERSION_SIZE)
        if count_pos < min_size or count_pos >= cal_size:
            raise ICIException("Range {} count pos 0x{:x} is invalid".format(range_name, count_pos))
        count = self.read_nvmem(addr, 1)[0]
        if count < 0 or count >= cal_size:
            raise ICIException("Range {} cell count {} is invalid".format(range_name, count))
        if index >= count:
            raise ICIException("index {} beyond to max count{}".format(index, count))
        # get cal cell address
        addr += CalibrationDef.CAL_COUNT_LEN
        return addr + index * CalibrationDef.CAL_CELL_LEN

    def read_calibration_item(self, cal_index, range_name, index):
        '''
        Read calibration data defined by ICI spec 2.8.4

        Args:
            cal_index:      int, (>=0), the index in the range to calibration item
            range_name:     string, range name which range to read
            index:          int, (>=0), the calibration data index to read in current range

        Returns:
            dict:           {"gain": value, "offset": value, "threshold": value, "is_use": value}
        '''
        assert cal_index >= 0
        assert range_name in self._range_table
        assert index >= 0

        addr = self._get_cal_item_addr(cal_index, range_name, index)
        data = self.read_nvmem(addr, CalibrationDef.CAL_CELL_LEN)

        s = struct.Struct('16B')
        pack_data = s.pack(*data)

        s = struct.Struct('3f4B')
        result = s.unpack(pack_data)
        if result[3] != CalibrationDef.CAL_SAVE_FLAG:
            return {"gain": 1.0, "offset": 0.0, "threshold": 0.0, "is_use": False}
        else:
            return {"gain": result[0], "offset": result[1], "threshold": result[2], "is_use": True}

    def _read_new_cal_start_address(self, date_list):
        max_start_address = self.nvmem[NVMemFieldNames.CAL_DATA_START_ADDR][0]
        max_data_size = self.nvmem[NVMemFieldNames.CAL_DATA_SIZE][0]
        for i in range(len(date_list)):
            address = self.nvmem[NVMemFieldNames.CAL_DATA_START_ADDR][i]
            if date_list[i] is None:
                continue
            if address > max_start_address:
                max_start_address = address
                max_data_size = self.nvmem[NVMemFieldNames.CAL_DATA_SIZE][i]
        return max_start_address + max_data_size

    def _read_date_list(self, num_cals):
        date_list = []
        for i in range(num_cals):
            try:
                date = self.read_calibration_date(i)
            except (ValueError, TypeError):
                date = None
            date_list.append(date)
        return date_list

    def _read_new_cal_index(self, latest_index, latest_date, num_cals, date_list, date_now):
        latest_date = latest_date
        if latest_date > date_now:
            raise ICIException("Current date '{}' is before latest calibration date '{}'"
                               "Please sync time with Firmware first.".format(date_now, latest_date))

        if latest_date == date_now:
            return latest_index

        for i in range(num_cals):
            if date_list[i] is None:
                return i

        if num_cals < 3:
            return num_cals

        oldest_date = min(date_list)
        return date_list.index(oldest_date)

    def _write_calibration_data(self, new_index, start_address, data_size, version, cal_table):
        new_cal_data = bytearray([0xFF for i in range(data_size)])
        new_cal_data[0] = version
        range_count = len(self._range_table)
        range_header = [[] for i in range(range_count)]
        for range_name in cal_table:
            range_index = self._range_table[range_name]
            range_header[range_index] = cal_table[range_name]

        range_data_offset = CalibrationDef.CAL_VERSION_SIZE + range_count * CalibrationDef.CAL_RANGE_LEN
        for range_index in range(range_count):
            cal_data = range_header[range_index]
            count = len(cal_data)
            range_addr = start_address + range_data_offset

            new_cal_data[CalibrationDef.CAL_VERSION_SIZE + range_index * 2] = (range_addr >> 8) & 0xFF
            new_cal_data[CalibrationDef.CAL_VERSION_SIZE + range_index * 2 + 1] = range_addr & 0xFF
            new_cal_data[range_data_offset] = count

            for i in range(count):
                item_offset = range_data_offset + CalibrationDef.CAL_VERSION_SIZE + i * CalibrationDef.CAL_CELL_LEN
                if cal_data[i]['is_use'] is True:
                    gain = cal_data[i]['gain']
                    offset = cal_data[i]['offset']
                    threshold = cal_data[i]['threshold']
                    s = struct.Struct('3f4B')
                    pack_data = s.pack(gain, offset, threshold, CalibrationDef.CAL_SAVE_FLAG, 0xFF, 0xFF, 0xFF)
                    s = struct.Struct('16B')
                    data = s.unpack(pack_data)
                else:
                    data = bytearray([0xFF for i in range(CalibrationDef.CAL_CELL_LEN)])
                new_cal_data[item_offset: item_offset + CalibrationDef.CAL_CELL_LEN] = data
            range_data_offset = range_data_offset + count * CalibrationDef.CAL_CELL_LEN + 1
        self.write_calibration_cell(new_index, new_cal_data)

    def write_module_calibration(self, channel, calibration_vectors):
        '''
        Calculate module calibration and write to eeprom.

        This function should be reimplemented in module driver.

        Args:
            channel:    string, module range. It is different for different module.
            calibration_vectors:    list, it contains value pairs of module raw reading
                                        and benchmark value got from external equipments.
                                        [[module_raw1, benchmark1], [module_raw2, benchmark2],
                                         ...,[module_rawN, benchmarkN]]
        Returns:
            string, 'done', execute successfully.
        '''
        date_now = datetime.now()
        new_date = date_now.strftime('%Y%U%w')
        num_cals = self.read_number_supported_calibrations()
        latest_index = self.read_latest_calibration_index()
        latest_date = self.read_calibration_date(latest_index).strftime("%Y%U%w")
        latest_size = self.nvmem[NVMemFieldNames.CAL_DATA_SIZE][latest_index]
        date_list = self._read_date_list(num_cals)
        new_index = self._read_new_cal_index(latest_index, latest_date, num_cals, date_list, new_date)
        cal_table = copy.deepcopy(self._calibration_table)

        version = self.read_nvmem(self.nvmem[NVMemFieldNames.CAL_DATA_START_ADDR][latest_index], 1)[0]

        if new_index >= num_cals or date_list[new_index] is None:
            new_start_address = self._read_new_cal_start_address(date_list)
            self.write_nvmem(CalibrationDef.NUM_CALS_ADDR, bytearray([new_index + 1]))
            ro_data = self.read_nvmem(0, CalibrationDef.RO_Checksum_ADDR)
            self.write_nvmem(CalibrationDef.RO_Checksum_ADDR, BytesHelper.sha1_hash(ro_data))
            temp = bytearray([new_start_address & 0xFF, (new_start_address >> 8) & 0xFF,
                              (new_start_address >> 16) & 0xFF, (new_start_address >> 24) & 0xFF])
            self.write_nvmem(Cal_StartAddr_ADDR(new_index), temp)
            temp = bytearray([latest_size & 0xFF, (latest_size >> 8) & 0xFF,
                              (latest_size >> 16) & 0xFF, (latest_size >> 24) & 0xFF])
            self.write_nvmem(Cal_DataSize_ADDR(new_index), temp)
            self.nvmem.refresh_cal_header_info()
        else:
            new_start_address = self.nvmem[NVMemFieldNames.CAL_DATA_START_ADDR][new_index]
        if new_date != latest_date:
            # clear calibration data
            for range_name, range_cal_table in cal_table.items():
                for item in range_cal_table:
                    item['gain'] = 1.0
                    item['offset'] = 0.0

        range_cal_table = cal_table[channel]
        range_cal_table_len = len(range_cal_table)
        for i in range(range_cal_table_len):
            range_cal_table[i]['X'] = []
            range_cal_table[i]['Y'] = []

        for raw_data in calibration_vectors:
            level = 0
            for i in range(range_cal_table_len):
                if raw_data[0] < range_cal_table[i]['threshold']:
                    level = i
                    break
                    level = i
            if range_cal_table[level]['is_use'] is False:
                continue
            range_cal_table[level]['X'].append(raw_data[0])
            range_cal_table[level]['Y'].append(raw_data[1])

        for i in range(range_cal_table_len):
            if range_cal_table[i]['is_use'] is False:
                continue
            k, b = leastsq(range_cal_table[i]['X'], range_cal_table[i]['Y'])
            range_cal_table[i]['gain'] = k
            range_cal_table[i]['offset'] = b
            range_cal_table[i]['is_use'] = True

        self._write_calibration_data(new_index, new_start_address, latest_size, version, cal_table)
        self.load_calibration()

    def get_ranges_name(self):
        '''
        Get board range name.

        Returns:
            list.
        '''
        return self._range_table.keys()

    def enable_calibration(self, calibration_cell_index):
        '''
        Enables the module calibration using the index specified. -1 for index will use the latest calibration.

        Args:
            calibration_cell_index: int, the desired index from module NVMEM to use for calibration.

        Returns:
            string, "done", "done" for success

        Exception:
            InvalidCalibrationIndex() if index is <-1 or greater than the number of supported calibrations

            InvalidCalibrationCell() if the specified index does not contain calibration data with a valid checksum
        '''
        number = self.read_number_supported_calibrations()
        if calibration_cell_index < CalibrationDef.LATEST_CAL or calibration_cell_index > number:
            raise InvalidCalibrationIndex("index is <-1 or greater than the number of supported calibrations")

        self.set_calibration_mode('cal')

        self.load_calibration(calibration_cell_index)

        if self._cal_common_error is not None:
            raise InvalidCalibrationCell("the specified index does not contain calibration data with a valid checksum")
        return "done"

    def disable_calibration(self):
        '''
        Disables the module calibration.

        Returns:
            string, "done", "done" for success
        '''
        self.set_calibration_mode('raw')
        return "done"

    def get_active_calibration_index(self):
        '''
        Returns the index of the active calibration cell.

        Returns:
            The index of the active calibration cell
        '''
        return self.cal_index
