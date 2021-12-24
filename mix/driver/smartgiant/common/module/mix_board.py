# -*- coding: utf-8 -*-
import struct
import collections
from datetime import datetime
from mix.driver.smartgiant.common.module.mixmoduledriver import MIXModuleDriver
from mix.driver.core.ic.nct75_emulator import NCT75Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator

__author__ = 'yuanle@SmartGiant'
__version__ = '0.2'


# ICI Spec2.7
class ICIDef:
    FID_ADDR = 0x00
    FID_LEN = 54
    ROMVer_ADDR = 0x36
    ROMVer_LEN = 1
    CAPACITY_ADDR = 0x37
    CAPACITY_LEN = 2
    VID_ADDR = 0x39
    VID_LEN = 3
    DID_ADDR = 0x3C
    DID_LEN = 3
    HW_ADDR = 0x3F
    HW_LEN = 9
    SN_ADDR = 0x48
    SN_LEN = 17
    DATE_TIME_CELL_ADDR = 0x59
    DATE_TIME_CELL_LEN = 5
    DATE_TIME_CELL_NUM = 16
    CAL_DESC_ADDR = 0xA9
    CAL_START_ADDR = 0xA9
    CAL_START_ADDR_LEN = 2

    CAL_NUM_CALS_ADDR = 0x18
    CAL_NUM_CALS_ADDR_LEN = 1
    CAL_MAX_NUM = 3

    CAL_CELLEN_ADDR = 0xAB
    CAL_CELL_LEN = 16
    CAL_RANGE_LEN = 2
    SYS_CAL_START_ADDR = 0xAC
    SYS_CAL_START_ADDR_LEN = 2
    SYS_CAL_CELLLEN_ADDR = 0xAE
    CONFIG_ADDR = 0xAF
    CONFIG_LEN = 3
    CAL_AREA_ADDR = 0xE0
    CAL_AREA_SIZE = (240 * 16)
    CHECKSUM_SIZE = 16

    CAL_SAVE_FLAG = 0x5A

    USE_CAL = 1
    USE_NONE_CAL = 0

    CAL_VERSION_SIZE = 1
    CAL_COUNT_LEN = 1

    SG_VID = 'GQQ'


class MIXBoardDef:
    ICI_VERSION_NONE = "none"
    ICI_VERSION_2_7 = "v2.7"
    ICI_VERSION_2_8_4 = "v2.8.4"

    # ICI Spec Version >= 2.8.4
    SG_VID = 'GQQ'

    SN_ADDR = 0x48
    EEEE_CODE_ADDR = 0x48 + 11
    EEEE_CODE_LEN = 4

    # some module sn address is 0x3f or 0x50 or 0x51
    XAVIER5_0_SN_ADDR_0X3F = 0x3F
    XAVIER5_0_SN_ADDR_0X50 = 0x50
    XAVIER5_0_SN_ADDR_0X51 = 0x51
    XAVIER5_0_SN_LEN = 16
    SN_MONTHS = [chr(ord('A') + i) for i in range(12)]
    SN_YEARS = ['A', 'B', 'C', 'D']


class BoardOperationError(Exception):
    '''When the board have the hardware operation error, use this raise
    '''

    def __init__(self, err):
        Exception.__init__(
            self, "[MixBoard operation exception] %s" % (err))


class BoardArgCheckError(Exception):
    '''Check parameter results do not conform to the function afferent specification, use this raise
    '''

    def __init__(self, err):
        Exception.__init__(
            self, "[MixBoard arg check exception] %s" % (err))


class ICIException(Exception):
    pass


def capacity_to_bytes(kbits):
    '''
    Convert capacity to bytes

    Args:
        kbits:      int, (>=0), kbit(s), capacity in kbits

    Returns:
        int:        (>0), bytes, capacity in bytes
    '''
    return kbits * 1024 / 8


class MIXBoard(MIXModuleDriver):
    '''
    MIXBoard function class, this is all board parent

    Args:
        eeprom:             instance(EEPROM)/None, Eeprom class instance, if None, will create emulator.
        temperature_devcie: instance(SENSOR)/None, Temperature class instance, if None will create emulator.
        cal_table:          dict, which is legacy calibration table
        range_table:        dict, which is ICI calibration range table.

    Examples:
        class SCOPE002004(MIXBoard):
            def __init__(self, ad7177=None, eeprom=None, nct75=None):
                MIXBoard.__init__(self, eeprom, nct75)
    '''

    rpc_public_api = ['get_temperature', 'read_eeprom', 'write_eeprom', 'eeprom_read_string', 'eeprom_write_string',
                      'get_calibration_mode', 'set_calibration_mode', 'load_calibration', 'calibrate',
                      # ici spec 2.8.4
                      'pre_power_on_init', 'post_power_on_init', 'reset', 'pre_power_down',
                      'get_driver_version', 'read_hardware_config',
                      'read_hardware_version',
                      'read_serial_number', 'read_temperature',
                      'read_calibration_cell', 'write_calibration_cell',
                      'read_EEEE_code', 'read_nvram', 'write_nvram', 'read_vendor',
                      'config_calibration_checksum',
                      'config_calibration_range',
                      'read_calibration_item', 'write_calibration_item', 'get_ranges_name',
                      'set_production_mode'
                      ] + MIXModuleDriver.rpc_public_api

    calibration_info = {
        "mode": {"raw": 0, "cal": 1},
        "default": "cal",
        "unit_start_addr": 0x80,
        "use_flag": 0x5a,
        'date_addr': 0x70,
        'date_mem_length': 16
    }

    serialnumber_info = {
        "start_addr": 0x50,
        "length": 32
    }

    hardware_info = {
        "version_addr": 0x40,
        "version_mem_length": 16
    }

    _module = 'MIX'

    def __init__(self, eeprom=None, temperature_device=None, cal_table={}, range_table={}):
        self._legacy_cal_table = cal_table
        self._range_table = range_table
        self._calibration_table = {}
        if eeprom is None:
            self._eeprom_device = EepromEmulator("eeprom_emulator")
        else:
            self._eeprom_device = eeprom
        if temperature_device is None:
            self._temperature_device = NCT75Emulator("nct75_emulatur")
        else:
            self._temperature_device = temperature_device
        self._cal_mode_flag = self.calibration_info['mode']['cal']

        self._range_err_table = {}
        self._cal_common_error = None
        self._product_cal_flag = False

    def version(self):
        '''
        MIXBoard get board driver version

        Examples:
            version = board.version()
            print(version)

        '''
        return __version__

    def get_temperature(self):
        '''
        MIXBoard read board temperature, and return celsius degree,float type

        Examples:
            temp = board.get_temperature()
            print(temp)

        '''

        temp = self._temperature_device.get_temperature()

        return temp

    def read_nvram(self, address, count):
        '''
        this should return a bytearray object representing the data.

        Args:
            address:        int, (>=0), the start address to read data
            count:          int, (>0), number bytes to read of data

        Returns:
            bytearray, data has been read
        '''
        return bytearray(self._eeprom_device.read(address, count))

    def write_nvram(self, address, data):
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
        return self._temperature_device.get_temperature()

    def read_vendor(self):
        '''
        Read vendor ID

        Returns:
            string, vendor id
        '''
        vendor = super(MIXBoard, self).read_vendor()
        if vendor == MIXBoardDef.SG_VID:
            return vendor
        vendor = self.read_nvram(ICIDef.VID_ADDR, ICIDef.VID_LEN)
        return str(vendor)

    def _read_ici_version(self):
        '''
        Read ICI spec version.

        Returns:
            string, ['v2.7', 'v2.8.4', 'none'], ICI version.
        '''
        vendor = super(MIXBoard, self).read_vendor()
        if vendor == MIXBoardDef.SG_VID:
            return MIXBoardDef.ICI_VERSION_2_8_4
        vendor = self.read_nvram(ICIDef.VID_ADDR, ICIDef.VID_LEN)
        if str(vendor) == MIXBoardDef.SG_VID:
            return MIXBoardDef.ICI_VERSION_2_7
        return MIXBoardDef.ICI_VERSION_NONE

    def read_EEEE_code(self):
        '''
        returns the EEEE code.

        This is an Apple assigned number that uniquely identifies
        this type of modules

        Returns:
            string, EEEE code.
        '''
        version = self._read_ici_version()
        if version == MIXBoardDef.ICI_VERSION_2_8_4:
            return super(MIXBoard, self).read_EEEE_code()
        elif version == MIXBoardDef.ICI_VERSION_2_7:
            return str(self.read_nvram(MIXBoardDef.EEEE_CODE_ADDR, MIXBoardDef.EEEE_CODE_LEN))
        return ""

    def read_hardware_config(self):
        '''
        Read hardware config.

        returns a string that represents the config

        Returns:
            string, hardware config.
        '''
        version = self._read_ici_version()
        if version == MIXBoardDef.ICI_VERSION_2_8_4:
            return super(MIXBoard, self).read_hardware_config()
        elif version == MIXBoardDef.ICI_VERSION_2_7:
            return str(self.read_nvram(ICIDef.CONFIG_ADDR, ICIDef.CONFIG_LEN))
        return ""

    def read_serial_number(self):
        '''
        Read serial number.

        Returns a string that represents the serial number

        Returns:
            string, serial number string.
        '''
        version = self._read_ici_version()
        if version == MIXBoardDef.ICI_VERSION_2_8_4:
            return super(MIXBoard, self).read_serial_number()
        elif version == MIXBoardDef.ICI_VERSION_2_7:
            return str(self.read_nvram(ICIDef.SN_ADDR, ICIDef.SN_LEN))
        else:
            try:
                sn = self.read_serialnumber()
            except Exception as ex:
                sn = ['?'] * MIXBoardDef.XAVIER5_0_SN_LEN
            # pos 9 is year. A is 2018, B is 2019, ...
            year = sn[9]
            # pos 10 is month. A is January, B is February, ...
            month = sn[10]
            if year in MIXBoardDef.SN_YEARS and month in MIXBoardDef.SN_MONTHS:
                return sn

            # some module sn address is 0x3f or 0x50 or 0x51
            for i in [MIXBoardDef.XAVIER5_0_SN_ADDR_0X3F, MIXBoardDef.XAVIER5_0_SN_ADDR_0X50,
                      MIXBoardDef.XAVIER5_0_SN_ADDR_0X51]:
                sn = self.eeprom_read_string(i, MIXBoardDef.XAVIER5_0_SN_LEN)
                # pos 9 is year. A is 2018, B is 2019, ...
                year = sn[9]
                # pos 10 is month. A is January, B is February, ...
                month = sn[10]
                if year in MIXBoardDef.SN_YEARS and month in MIXBoardDef.SN_MONTHS:
                    break
            return sn

    def read_eeprom(self, address, count=1):
        '''
        MIXBoard read data from board eeprom, and return list,element for byte data

        Args:
            address:      hex, [0~0xFFFF], eeprom memory address.
            count:        int, [0~1024], Count of datas to be read.

        Returns:
            list.

        Examples:
            data = board.read_eeprom(0x00, 3)
            print(data)

        '''
        return self._eeprom_device.read(address, count)

    def write_eeprom(self, address, data_list):
        '''
        MIXBoard write data to board eeprom

        Args:
            address:     hex, [0~0xFFFF], eeprom memeroy address.
            data_list:   list, [hex], element for byte data, which you want to write into eeprom.

        Examples:
            board.write_eeprom(0x00, [0x01, 0x02, 0x03])

        '''
        self._eeprom_device.write(address, data_list)

    def write_hardware_version(self, hardware_version):
        '''
        MIXBoard write hardware version to eeprom

        Args:
            hardware_version: string, Max length is 16 character,'\0' do not contain and not write to eeprom.

        Examples:
            board.write_hardware_version("v0.1")

        '''
        hardware_version = str(hardware_version)
        if len(hardware_version) > self.hardware_info['version_mem_length']:
            raise BoardArgCheckError("the max character length is %s, write data[%s]: \'%s\'" % (
                                     self.hardware_info['version_mem_length'],
                                     len(hardware_version), hardware_version))
        data_list = [ord(x) for x in hardware_version]
        if len(data_list) < self.hardware_info['version_mem_length']:
            data_list += [0x00]

        self.write_eeprom(self.hardware_info['version_addr'], data_list)

    def read_hardware_version(self):
        '''
        MIXBoard read hardware version from eeprom

        Examples:
            version = board.read_hardware_version()
            print(version)

        '''
        version = self._read_ici_version()
        if version == MIXBoardDef.ICI_VERSION_2_8_4:
            return super(MIXBoard, self).read_hardware_version()
        elif version == MIXBoardDef.ICI_VERSION_2_7:
            return str(self.read_nvram(ICIDef.HW_ADDR, ICIDef.HW_LEN))
        else:
            data_list = self.read_eeprom(
                self.hardware_info['version_addr'], self.hardware_info['version_mem_length'])

            hardware_version = ""
            for data in data_list:
                if data == 0x00:
                    break

                # if data > 0x7f, it not a acsii character
                if data & 0x80 != 0x00:
                    hardware_version += '?'
                else:
                    hardware_version += chr(data)

            return hardware_version

    def read_serialnumber(self):
        '''
        MIXBoard read board serial-number: (247,59)

        Examples:
            sn = board.read_serialnumber()
            print(sn)

        '''
        key_n = 247
        key_d = 11

        data_list = self.read_eeprom(
            self.serialnumber_info["start_addr"], self.serialnumber_info["length"])
        serialnumber = ""
        for index in range(0, len(data_list)):
            if data_list[index] == 0x00:
                break
            de_crypt = pow(data_list[index], key_d) % key_n
            if de_crypt & 0x80 != 0x00:
                raise BoardOperationError(
                    "the serialnumber in eeprom is not smartgiant writed: %s" % (str(data_list)))
            serialnumber += chr(de_crypt)

        return serialnumber

    def write_serialnumber(self, key_n, key_e, serialnumber):
        '''
        MIXBoard write serial-number to board, only use for smartgiant

        Args:
            key_n:                int,    private key.
            key_e:                int,    private key.
            serialnumber:         string, max length is 32 character,
                                          '\0' do not contain and not write to eeprom.

        Examples:
            board.write_serialnumber(247, 11, "20180101")

        '''
        serialnumber = str(serialnumber)
        if len(serialnumber) > self.serialnumber_info["length"]:
            msg = "the serialnumber is too long, or the max character length is 32, "
            msg += "the write serialnumber:  \'%s\'" % (serialnumber)
            raise BoardArgCheckError(msg)

        data_list = []
        for index in range(0, len(serialnumber)):
            data_list += [pow(ord(serialnumber[index]), key_e) % key_n]

        if len(data_list) < self.serialnumber_info["length"]:
            data_list += [0x00]

        self.write_eeprom(self.serialnumber_info["start_addr"], data_list)

    def write_legacy_calibration_date(self, date):
        '''
        MIXBoard write calibration data write date time

        Args:
            date:    string, max length is 16 character,'\0' do not contain and not write to eeprom.

        Examples:
            board.write_legacy_calibration_date("2018.01.01")

        '''
        date = str(date)
        if len(date) > self.calibration_info['date_mem_length']:
            msg = "calibration date data type is not str type or char bytes, "
            msg += "or the max character length is "
            msg += "%s, write data: \'%s\'" % (self.calibration_info['date_mem_length'], date)
            raise BoardArgCheckError(msg)

        data_list = [ord(x) for x in date]
        if len(data_list) < self.calibration_info['date_mem_length']:
            data_list += [0x00]

        self.write_eeprom(self.calibration_info['date_addr'], data_list)

    def read_legacy_calibration_date(self):
        '''
        MIXBoard read calibration data write date time

        Examples:
            result = board.read_legacy_calibration_date()
            print(result)

        '''

        data_list = self.read_eeprom(
            self.calibration_info['date_addr'], self.calibration_info['date_mem_length'])

        date_time = ""
        for data in data_list:
            if data == 0x00:
                break

            # if data > 0x7f, it not a acsii character
            if data & 0x80 != 0x00:
                date_time += '?'
            else:
                date_time += chr(data)

        return date_time

    def legacy_write_calibration_cell(self, unit_index, gain, offset, threshold):
        '''
        MIXBoard calibration data write

        Args:
            unit_index:   int,    calibration unit index.
            gain:         float,  calibration gain.
            offset:       float,  calibration offset.
            threshold:    float,  if value < threshold, use this calibration unit data.

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
            raise BoardArgCheckError(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        use_flag = self.calibration_info["use_flag"]
        data = (gain, offset, threshold, use_flag)
        s = struct.Struct("3fB")
        pack_data = s.pack(*data)

        s = struct.Struct("13B")
        data = s.unpack(pack_data)
        address = self.calibration_info["unit_start_addr"] + 13 * unit_index
        self.write_eeprom(address, data)

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
            raise BoardArgCheckError(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        address = self.calibration_info["unit_start_addr"] + 13 * unit_index
        data = self.read_eeprom(address, 13)

        s = struct.Struct("13B")
        pack_data = s.pack(*data)

        s = struct.Struct("3fB")
        result = s.unpack(pack_data)

        use_flag = result[3]
        if self.calibration_info["use_flag"] != use_flag:
            return {"gain": 1.0, "offset": 0.0, "threshold": 0.0, "is_use": False}
        else:
            return {"gain": result[0], "offset": result[1], "threshold": result[2], "is_use": True}

    def legacy_erase_calibration_cell(self, unit_index):
        '''
        MIXBoard erase calibration unit

        Args:
            unit_index: int, calibration unit index.

        Examples:
            board.erase_calibration_cell(0)

        '''
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        data = [0xff for i in range(13)]
        address = self.calibration_info["unit_start_addr"] + 13 * unit_index
        self.write_eeprom(address, data)

    def get_calibration_mode(self):
        '''
        MIXBoard get calibration mode

        Examples:
            mode = board.mode
            print(mode)

        '''
        if self._cal_mode_flag == self.calibration_info["mode"]["cal"]:
            return "cal"
        else:
            return "raw"

    def set_calibration_mode(self, mode):
        '''
        MIXBoard set calibration mode

        Args:
            mode:   string, ['cal', 'raw'], 'cal' enable calibration, 'raw': disable calibration.

        Examples:
            # enable calibration
            board.set_calibration_mode('cal')
            # disable calibration
            board.set_calibration_mode('raw')

        '''
        assert mode in ["cal", "raw"]
        self._cal_mode_flag = self.calibration_info["mode"][mode]

    def is_use_cal_data(self):
        '''
        MIXBoard check whether the current mode is a calibration mode

        Examples:
            if board.is_use_cal_data:
                print('Use calibration data')
            else:
                print('Not use calibration data')

        '''

        if self._cal_mode_flag == self.calibration_info["mode"]["cal"]:
            return True
        else:
            return False

    def cal_pipe(self, fun_cal_info, raw_data):
        '''
        MIXBoard get the calibrated results

        Args:
            fun_cal_info: dict.

            Examples:
                #config limit
                {
                    'level1': {'unit_index':int type,'limit':(value, unit)},
                    'level2': {'unit_index':int type,'limit':(value, unit)},
                    ......
                    'leveln': {'unit_index':int type,'limit':(value, unit)},
                }

                #memory limit
                {
                    "level1":{'unit_index': int},
                    "level2":{'unit_index': int},
                    "level3":{'unit_index': int},
                    ......
                    "leveln":{'unit_index': int},
                }

            raw_data: int or float type.
            Examples:
                cal_info = {
                    'level1': {'unit_index':0,'limit':(100, 'mA')},
                    'level2': {'unit_index':2,'limit':(200, 'mA')},
                    ......
                    'leveln': {'unit_index':n-1,'limit':(1000, 'mA')}

                result = cal_pipe(cal_info, 10)
                print(result)

        '''

        if fun_cal_info == {} or fun_cal_info is None:
            return raw_data

        # select calibration limit data format
        cal_info_mode = None
        for key, value in fun_cal_info.items():
            if 'limit' in value.keys():
                cal_info_mode = 'config'
            else:
                cal_info_mode = 'memory'

            break

        if cal_info_mode == 'memory':
            # read section cal data from eeprom
            cal_info = collections.OrderedDict()
            for i in range(0, len(fun_cal_info)):
                level = "level%d" % (i + 1)
                index = fun_cal_info[level]["unit_index"]
                result = self.legacy_read_calibration_cell(index)
                if not result['is_use']:
                    break
                cal_info[level] = result

            # select cal data
            level = None
            for key, value in cal_info.items():
                if raw_data <= value["threshold"]:
                    level = key
                    break
            if level is None:
                if len(cal_info) > 0:
                    level = "level%d" % (len(cal_info))
                else:
                    return raw_data
            cal_datas = cal_info[level]

        else:
            # select cal data
            level = None
            for i in range(0, len(fun_cal_info)):
                key = "level%d" % (i + 1)
                if raw_data <= fun_cal_info[key]["limit"][0]:
                    level = key
                    break

            if level is None:
                if len(fun_cal_info) > 0:
                    level = "level%d" % (len(fun_cal_info))

            # read cal data from eeprom
            index = fun_cal_info[level]["unit_index"]
            cal_datas = self.legacy_read_calibration_cell(index)

        if cal_datas['is_use']:
            calibrated_result = cal_datas["gain"] * \
                raw_data + cal_datas["offset"]
        else:
            calibrated_result = raw_data

        return calibrated_result

    def set_production_mode(self, state="enable"):
        '''
        MIXBoard set product flag for production calibration

        Args:
            state:    string, ['enable', 'disable'], default 'enable'.

        Returns:
            string, ['done', 'fail'].

        Examples:
            set_production_mode(enable)

        '''
        if state not in ["enable", "disable"]:
            return 'fail'
        else:
            self._product_cal_flag = True if state == "enable" else False
            return 'done'

    def load_legacy_calibration(self):
        '''
        Load legacy calibration data.

        This function is used to load legacy calibration data which is compatible with xavier5.0.

        '''
        self._calibration_table = {}
        for range_name in self._legacy_cal_table:
            self._calibration_table[range_name] = []
            for level in self._legacy_cal_table[range_name]:
                try:
                    result = self.legacy_read_calibration_cell(self._legacy_cal_table[range_name][level]['unit_index'])
                except Exception as e:
                    self._cal_common_error = e
                    continue
                self._calibration_table[range_name].append(result)
        return "done"

    def _date_from_bytes(self, date_array):
        # expecting YYWWDHHMM
        # in compliance with 081-2110-C section 5, Sun-Sat is defined as 1-7 instead of 0-6 for day
        # and week code starts from 1 instead of 0 so we decrement the day and week bytes to be
        # compliant with python datetime prior to conversion
        date_string = str(date_array)
        ww = int(date_string[2:4])
        d = int(date_string[4])
        date_string = '20' + date_string[:2] + '{0:02d}{1}'.format(ww - 1, d - 1) + date_string[5:]
        return datetime.strptime(date_string, '%Y%U%w%H%M')

    def read_latest_calibration_index(self):
        '''
        Returns the index of the "latest" calibration blob written to nvmem. Intended for use in
        class init when loading default calibration values. Multiple calibrations written within
        the same minute will return the cal in the higher index.
        '''
        date_list = []
        num_cals = self.read_eeprom(ICIDef.CAL_NUM_CALS_ADDR, ICIDef.CAL_NUM_CALS_ADDR_LEN)[0]
        unused_date = datetime(1, 1, 1)  # earliest timestamp available
        if num_cals == 0:
            num_cals = 1
        for i in range(num_cals):
            # if date hasn't been written, has been erased, or is invalid, read will return ValueError or TypeError
            try:
                date = self.read_calibration_date(i)
            except (ValueError, TypeError):
                date = unused_date
            date_list.append(date)
        latest_date = max(date_list)
        if latest_date == unused_date:
            raise RuntimeError('cannot read latest cal index as all indices are empty or invalid')
        else:
            date_list.reverse()  # to prioritize timestamps written in same minute in higher indices
            return num_cals - date_list.index(latest_date) - 1

    def load_ici_calibration(self):
        '''
        Load ICI calibration data.

        This function is used to load calibration data defined by ICI Spec 2.8.4
        '''
        self._calibration_table = {}
        try:
            cal_index = self.read_latest_calibration_index()
        except Exception as e:
            self._cal_common_error = ICIException(str(e))
            return "done"

        if not self._product_cal_flag:
            try:
                read_data = super(MIXBoard, self).read_calibration_cell(cal_index)
            except Exception as e:
                self._cal_common_error = e
                return "done"
        else:
            start_address = self._get_cal_address(cal_index)
            data_size = self._get_cal_size(cal_index)
            read_data = self.read_nvram(start_address, data_size)

        base_addr = super(MIXBoard, self)._get_cal_address(cal_index)
        cal_size = super(MIXBoard, self)._get_cal_size(cal_index)

        for range_name, index in self._range_table.items():
            self._calibration_table[range_name] = []
            range_pos = ICIDef.CAL_VERSION_SIZE + index * ICIDef.CAL_RANGE_LEN
            # check range_pos range
            if range_pos >= cal_size:
                err_info = ICIException("Range {} range pos 0x{:x} is invalid".format(range_name, range_pos))
                self._range_err_table[range_name] = err_info
                continue
            range_pos_high = read_data[range_pos]
            range_pos_low = read_data[range_pos + 1]
            range_addr = (range_pos_high << 8) | range_pos_low
            count_pos = range_addr - base_addr
            # check count_pos range
            min_size = (len(self._range_table) * ICIDef.CAL_RANGE_LEN + ICIDef.CAL_VERSION_SIZE)
            if count_pos < min_size or count_pos >= cal_size:
                err_info = ICIException("Range {} count pos 0x{:x} is invalid".format(range_name, count_pos))
                self._range_err_table[range_name] = err_info
                continue
            count = read_data[count_pos]
            cal_pos = count_pos + ICIDef.CAL_COUNT_LEN
            cal_len = count * ICIDef.CAL_CELL_LEN
            cal_data = read_data[cal_pos:(cal_pos + cal_len)]

            for i in range(count):
                item_pos = i * ICIDef.CAL_CELL_LEN
                data = cal_data[item_pos:(item_pos + ICIDef.CAL_CELL_LEN)]

                s = struct.Struct('16B')
                pack_data = s.pack(*data)

                s = struct.Struct('3f4B')
                result = s.unpack(pack_data)
                if result[3] != ICIDef.CAL_SAVE_FLAG:
                    self._calibration_table[range_name].append({'gain': 1.0, "offset": 0.0,
                                                                "threshold": 0.0, "is_use": False})
                else:
                    self._calibration_table[range_name].append({"gain": result[0], "offset": result[1],
                                                                "threshold": result[2], "is_use": True})
        return "done"

    def load_legacy_ici_calibration(self):
        '''
        Load ICI calibration data.

        This function is used to load calibration data defined by ICI Spec 2.7

        '''
        self._calibration_table = {}
        # get calibration base address
        try:
            base_addr = self.read_legacy_ici_cal_start_addr() + ICIDef.CAL_VERSION_SIZE
        except Exception as e:
            self._cal_common_error = e
            return "done"

        for range_name, index in self._range_table.items():
            self._calibration_table[range_name] = []
            # get range address
            addr = base_addr + index * ICIDef.CAL_RANGE_LEN
            if addr < ICIDef.CAL_AREA_ADDR + ICIDef.CAL_VERSION_SIZE or \
               addr >= ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
                continue
            data = self.read_eeprom(addr, ICIDef.CAL_RANGE_LEN)
            # get item count address
            addr = (data[0] << 8) | data[1]
            if addr < ICIDef.CAL_AREA_ADDR + ICIDef.CAL_VERSION_SIZE or \
               addr >= ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
                continue
            count = self.read_eeprom(addr, 1)[0]
            # get cal cell address
            addr += ICIDef.CAL_COUNT_LEN
            if addr < ICIDef.CAL_AREA_ADDR + ICIDef.CAL_VERSION_SIZE or \
               addr >= ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
                self._cal_common_error = ICIException("Range {} cell address 0x{:x} "
                                                      "is invalid".format(range_name, addr))
                continue
            if addr + count > ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
                self._cal_common_error = ICIException("Range {} cell count {} is invalid".format(range_name, count))
                continue

            for i in range(count):
                data = self.read_eeprom(addr, ICIDef.CAL_CELL_LEN)
                addr = addr + ICIDef.CAL_CELL_LEN
                s = struct.Struct('16B')
                pack_data = s.pack(*data)

                s = struct.Struct('3f4B')
                result = s.unpack(pack_data)
                if result[3] != ICIDef.CAL_SAVE_FLAG:
                    self._calibration_table[range_name].append({'gain': 1.0, "offset": 0.0,
                                                                "threshold": 0.0, "is_use": False})
                else:
                    self._calibration_table[range_name].append({"gain": result[0], "offset": result[1],
                                                                "threshold": result[2], "is_use": True})
        return "done"

    def load_calibration(self):
        '''
        Load calibration data. If GQQ is defined in eeprom, this function will load calibration defined

        by ICI Spec 2.7. or 2.8.4
        '''
        self._cal_common_error = None
        self._range_err_table = {}
        version = self._read_ici_version()
        if version == MIXBoardDef.ICI_VERSION_2_8_4:
            self.load_ici_calibration()
        elif version == MIXBoardDef.ICI_VERSION_2_7:
            self.load_legacy_ici_calibration()
        else:
            self.load_legacy_calibration()
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

        assert range_name in self._calibration_table

        items = self._calibration_table[range_name]
        if len(items) == 0:
            return data

        if range_name in self._range_err_table:
            raise self._range_err_table[range_name]

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
        rd_data = self.read_eeprom(addr, rd_len)
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
        '''
        assert isinstance(data, basestring)
        data = [ord(ch) for ch in data]
        for ch in data:
            if ch < ord(' ') or ch > ord('~'):
                raise BoardArgCheckError("Data 0x{:x} is not printable".format(ch))
        self.write_eeprom(addr, data)
        return "done"

    def read_capacity(self):
        '''
        Read Storage size from eeprom

        Returns:
            int:    (>0), Kbit, Storage Size.
        '''
        data = self.read_eeprom(ICIDef.CAPACITY_ADDR, ICIDef.CAPACITY_LEN)
        return (data[0] << 8) | data[1]

    def write_capacity(self, kbits):
        '''
        Wrote storage size to eeprom.

        Args:
            kbits:      (>0), kbits, eeprom storage size.
        '''
        self.write_eeprom(ICIDef.CAPACITY_ADDR, [(kbits >> 8) & 0xFF, kbits & 0xFF])
        return "done"

    def read_legacy_ici_vid(self):
        '''
        Read vendor ID from eeprom.

        Returns:
            string:     Vendor ID.
        '''
        return self.eeprom_read_string(ICIDef.VID_ADDR, ICIDef.VID_LEN)

    def write_vid(self, vid):
        '''
        Write vendor ID to eeprom.

        Args:
            vid:    string, vendor ID.
        '''
        assert len(vid) == ICIDef.VID_LEN
        self.eeprom_write_string(ICIDef.VID_ADDR, vid)
        return "done"

    def read_legacy_ici_cal_start_addr(self):
        '''
        Read calibration area start address.

        Returns:
            int,    [0~65535], calibration start address.

        '''
        data = self.read_eeprom(ICIDef.CAL_START_ADDR, ICIDef.CAL_START_ADDR_LEN)
        addr = (data[0] << 8) | data[1]
        if addr < ICIDef.CAL_AREA_ADDR or addr >= addr + ICIDef.CAL_AREA_SIZE:
            raise ICIException("cal address 0x{:x} is invalid".format(addr))
        return (data[0] << 8) | data[1]

    def write_cal_start_addr(self, addr):
        '''
        Write calibration area start address.

        Args:
            addr:   int, [0~65535], calibration area start address.
        '''
        assert addr >= ICIDef.CAL_START_ADDR and addr < ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE
        self.write_eeprom(ICIDef.CAL_START_ADDR, [(addr >> 8) & 0xFF, addr & 0xFF])
        return "done"

    def read_cal_cell_len(self):
        '''
        Read calibration data cell used length

        Returns:
            int:    [0~255], calibration data cell used length.
        '''
        return self.read_eeprom(ICIDef.CAL_CELLEN_ADDR, 1)[0]

    def write_cal_cell_len(self, length):
        '''
        Write calibration data cell used length

        Args:
            length:   int, (0-255), the calibration cell used length
        '''
        self.write_eeprom(ICIDef.CAL_CELLEN_ADDR, [length])
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
        base_addr = super(MIXBoard, self)._get_cal_address(cal_index) + ICIDef.CAL_VERSION_SIZE
        cal_size = super(MIXBoard, self)._get_cal_size(cal_index)

        # get range address
        addr = base_addr + self._range_table[range_name] * ICIDef.CAL_RANGE_LEN
        data = self.read_eeprom(addr, 2)
        # get item count address
        addr = (data[0] << 8) | data[1]
        count_pos = addr - base_addr + ICIDef.CAL_VERSION_SIZE
        # check count_pos range
        min_size = (len(self._range_table) * ICIDef.CAL_RANGE_LEN + ICIDef.CAL_VERSION_SIZE)
        if count_pos < min_size or count_pos >= cal_size:
            raise ICIException("Range {} count pos 0x{:x} is invalid".format(range_name, count_pos))
        count = self.read_eeprom(addr, 1)[0]
        if count < 0 or count >= cal_size:
            raise ICIException("Range {} cell count {} is invalid".format(range_name, count))
        if index >= count:
            raise ICIException("index {} beyond to max count{}".format(index, count))
        # get cal cell address
        addr += ICIDef.CAL_COUNT_LEN
        return addr + index * ICIDef.CAL_CELL_LEN

    def _get_cal_cell_addr(self, range_name, index):
        '''
        Get calibration cell address defined by ICI spec 2.7

        Args:
            range_name:     string, range name, which is defined in module driver
            index:          int, (>=0), the index in the table of current range.

        Returns:
            int:            (>=0), calibration cell address.
        '''
        # get calibration base address
        base_addr = self.read_legacy_ici_cal_start_addr() + ICIDef.CAL_VERSION_SIZE

        # get range address
        addr = base_addr + self._range_table[range_name] * ICIDef.CAL_RANGE_LEN
        data = self.read_eeprom(addr, 2)
        # get item count address
        addr = (data[0] << 8) | data[1]
        if addr < ICIDef.CAL_AREA_ADDR + ICIDef.CAL_VERSION_SIZE or addr >= ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
            raise ICIException("Range {} address 0x{:x} is invalid".format(range_name, addr))
        count = self.read_eeprom(addr, 1)[0]
        if index >= count:
            raise ICIException("index {} beyond to max count{}".format(index, count))
        # get cal cell address
        addr += ICIDef.CAL_COUNT_LEN
        if addr < ICIDef.CAL_AREA_ADDR + ICIDef.CAL_VERSION_SIZE or addr >= ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
            raise ICIException("Range {} cell address 0x{:x} is invalid".format(range_name, addr))
        if addr + count > ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE:
            raise ICIException("Range {} cell count {} is invalid".format(range_name, count))
        return addr + index * ICIDef.CAL_CELL_LEN

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
        data = self.read_eeprom(addr, ICIDef.CAL_CELL_LEN)

        s = struct.Struct('16B')
        pack_data = s.pack(*data)

        s = struct.Struct('3f4B')
        result = s.unpack(pack_data)
        if result[3] != ICIDef.CAL_SAVE_FLAG:
            return {"gain": 1.0, "offset": 0.0, "threshold": 0.0, "is_use": False}
        else:
            return {"gain": result[0], "offset": result[1], "threshold": result[2], "is_use": True}

    def read_legacy_ici_calibration(self, range_name, index):
        '''
        Read calibration data defined by ICI spec 2.7

        Args:
            range_name:     string, range name which range to read
            index:          int, (>=0), the calibration data index to read in current range

        Returns:
            dict:           {"gain": value, "offset": value, "threshold": value, "is_use": value}
        '''
        assert range_name in self._range_table
        assert index >= 0
        addr = self._get_cal_cell_addr(range_name, index)
        data = self.read_eeprom(addr, ICIDef.CAL_CELL_LEN)
        s = struct.Struct('16B')
        pack_data = s.pack(*data)

        s = struct.Struct('3f4B')
        result = s.unpack(pack_data)
        if result[3] != ICIDef.CAL_SAVE_FLAG:
            return {"gain": 1.0, "offset": 0.0, "threshold": 0.0, "is_use": False}
        else:
            return {"gain": result[0], "offset": result[1], "threshold": result[2], "is_use": True}

    def write_calibration_item(self, cal_index, range_name, index, gain, offset, threshold):
        '''
        Write calibration data defined in ICI spec 2.8.4.

        The formula is below result = gain * raw_data + offset

        Args:
            cal_index:      int, (>=0), the index in the range to calibration item
            range_name:     string, which range to write
            index:          int, (>=0), the index in the range to write data
            gain:           float, gain value
            offset:         float, offset value
            threshold:      float, threshold value, if raw data >= threshold, the cell data
                            will be used to calibrate.

        Returns:
            string, "done", "done" for success
        '''
        assert cal_index >= 0
        assert range_name in self._range_table
        assert index >= 0

        addr = self._get_cal_item_addr(cal_index, range_name, index)
        s = struct.Struct('3f4B')
        pack_data = s.pack(gain, offset, threshold, ICIDef.CAL_SAVE_FLAG, 0xFF, 0xFF, 0xFF)
        s = struct.Struct('16B')
        data = s.unpack(pack_data)
        self.write_eeprom(addr, data)
        return "done"

    def write_legacy_ici_calibration(self, range_name, index, gain, offset, threshold):
        '''
        Write calibration data defined in ICI spec 2.7.

        The formula is below result = gain * raw_data + offset

        Args:
            range_name:     string, which range to write
            index:          int, (>=0), the index in the range to write data
            gain:           float, gain value
            offset:         float, offset value
            threshold:      float, threshold value, if raw data >= threshold, the cell data
                            will be used to calibrate.

        Returns:
            string,     "done", "done" for success
        '''
        assert range_name in self._range_table
        assert index >= 0
        addr = self._get_cal_cell_addr(range_name, index)
        s = struct.Struct('3f4B')
        pack_data = s.pack(gain, offset, threshold, ICIDef.CAL_SAVE_FLAG, 0xFF, 0xFF, 0xFF)
        s = struct.Struct('16B')
        data = s.unpack(pack_data)
        self.write_eeprom(addr, data)
        return "done"

    def erase_calibration_item(self, cal_index, range_name, index):
        '''
        Erase calibration data.

        Args:
            cal_index:      int, (>=0), the index in the range to calibration item.
            range_name:     string, the range to be erased.
            index:          int, (>=0), the index to be erased.

        Returns:
            string,     "done", "done" for success
        '''
        assert cal_index >= 0
        assert range_name in self._range_table
        assert index >= 0
        addr = self._get_cal_item_addr(cal_index, range_name, index)
        self.write_eeprom(addr, [0xFF for i in range(ICIDef.CAL_CELL_LEN)])
        return "done"

    def erase_legacy_ici_calibration(self, range_name, index):
        '''
        Erase calibration data.

        Args:
            range_name:     string, the range to be erased.
            index:          int, (>=0), the index to be erased.

        Returns:
            string,     "done", "done" for success
        '''
        assert range_name in self._range_table
        assert index >= 0
        addr = self._get_cal_cell_addr(range_name, index)
        self.write_eeprom(addr, [0xFF for i in range(ICIDef.CAL_CELL_LEN)])
        return "done"

    def read_legacy_ici_calibration_version(self):
        '''
        Read calibration data version
        '''
        addr = self.read_legacy_ici_cal_start_addr()
        return self.read_eeprom(addr, 1)[0]

    def write_legacy_ici_calibration_version(self, ver):
        '''
        Write calibration data version

        Args:
            ver:    int, (>=0), calibration data version.
        '''
        addr = self.read_legacy_ici_cal_start_addr()
        self.write_eeprom(addr, [ver])
        return "done"

    def config_calibration_checksum(self, cal_index):
        '''
        Config calibration table.

        Args:
            cal_index:      int, (>=0), the index in the range to calibration item.
        '''
        assert cal_index >= 0
        addr = super(MIXBoard, self)._get_cal_address(cal_index)
        size = super(MIXBoard, self)._get_cal_size(cal_index)
        data = self.read_nvram(addr, size)
        sha1_hash = self._cal_hash(self._get_cal_header_bytes(cal_index) + data)
        self.write_nvram(self.FIRST_CAL_CHKSUM_ADDR + cal_index * self.CAL_HEADER_SIZE, sha1_hash)
        return "done"

    def config_calibration_range(self, cal_index, range_name, addr, count):
        '''
        Config calibration table.

        Args:
            cal_index:      int, (>=0), the index in the range to calibration item.
            range_name:     string, the range to be configured.
            addr:           hex, [0xE0~0xFDF], current range calibration address.
            count:          int, (>=0), current range calibration cell count.
        '''
        assert cal_index >= 0
        assert range_name in self._range_table
        assert count > 0 and count <= 0xFF
        base_addr = super(MIXBoard, self)._get_cal_address(cal_index) + ICIDef.CAL_VERSION_SIZE + \
            self._range_table[range_name] * ICIDef.CAL_RANGE_LEN
        self.write_eeprom(base_addr, [(addr >> 8) & 0xFF, addr & 0xFF])
        self.write_eeprom(addr, [count])
        return "done"

    def config_legacy_ici_calibration_range(self, range_name, addr, count):
        '''
        Config calibration table.

        Args:
            range_name:     string, the range to be configured.
            addr:           hex, [0xE0~0xFDF], current range calibration address.
            count:          int, (>=0), current range calibration cell count.
        '''
        assert range_name in self._range_table
        assert count > 0 and count <= 0xFF
        assert addr >= ICIDef.CAL_AREA_ADDR and addr <= ICIDef.CAL_AREA_ADDR + ICIDef.CAL_AREA_SIZE
        base_addr = self.read_legacy_ici_cal_start_addr() + ICIDef.CAL_VERSION_SIZE + \
            self._range_table[range_name] * ICIDef.CAL_RANGE_LEN
        self.write_eeprom(base_addr, [(addr >> 8) & 0xFF, addr & 0xFF])
        self.write_eeprom(addr, [count])
        return "done"

    def get_ranges_name(self):
        '''
        Get board range name.

        '''
        return self._range_table.keys()
