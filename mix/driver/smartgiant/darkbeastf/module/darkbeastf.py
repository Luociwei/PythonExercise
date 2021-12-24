# -*- coding: utf-8 -*-
import re
import os
import time
import struct
from subprocess import PIPE, STDOUT, Popen

from mix.driver.core.ic.cat24cxx import CAT24C08
from mix.driver.smartgiant.common.bus.gpio_emulator import GPIOEmulator
from mix.driver.smartgiant.common.ic.ad5592r_emulator import AD5592REmulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard, BoardArgCheckError

__author__ = 'dongdong.zhang@SmartGiant'
__version__ = '0.2'


darkbeastf_calibration_base_addr = {
    'set_eload_current': 0x101,
    'set_orion_voltage': 0x162,
    'read_eload_current': 0x1C3,
    'read_orion_current': 0x224,
    'read_orion_voltage': 0x285
}


darkbeastf_calibration_info = {
    'set_eload_current': {
        'level1': {'unit_index': 0, 'limit': (1000, 'mA')},
        'level2': {'unit_index': 1, 'limit': (3000, 'mA')},
        'level3': {'unit_index': 2, 'limit': (5500, 'mA')},
        'level4': {'unit_index': 3, 'limit': (5500, 'mA')},
        'level5': {'unit_index': 4, 'limit': (5500, 'mA')}
    },
    'set_orion_voltage': {
        'level1': {'unit_index': 0, 'limit': (1000, 'mV')},
        'level2': {'unit_index': 1, 'limit': (3000, 'mV')},
        'level3': {'unit_index': 2, 'limit': (5500, 'mV')},
        'level4': {'unit_index': 3, 'limit': (5500, 'mV')},
        'level5': {'unit_index': 4, 'limit': (5500, 'mV')}
    },
    'read_eload_current': {
        'level1': {'unit_index': 0, 'limit': (1000, 'mA')},
        'level2': {'unit_index': 1, 'limit': (3000, 'mA')},
        'level3': {'unit_index': 2, 'limit': (5500, 'mA')},
        'level4': {'unit_index': 3, 'limit': (5500, 'mA')},
        'level5': {'unit_index': 4, 'limit': (5500, 'mA')}
    },
    'read_orion_current': {
        'level1': {'unit_index': 0, 'limit': (1000, 'mA')},
        'level2': {'unit_index': 1, 'limit': (3000, 'mA')},
        'level3': {'unit_index': 2, 'limit': (5500, 'mA')},
        'level4': {'unit_index': 3, 'limit': (5500, 'mA')},
        'level5': {'unit_index': 4, 'limit': (5500, 'mA')}
    },
    'read_orion_voltage': {
        'level1': {'unit_index': 0, 'limit': (1000, 'mV')},
        'level2': {'unit_index': 1, 'limit': (3000, 'mV')},
        'level3': {'unit_index': 2, 'limit': (5500, 'mV')},
        'level4': {'unit_index': 3, 'limit': (5500, 'mV')},
        'level5': {'unit_index': 4, 'limit': (5500, 'mV')}
    }
}

darkbeastf_range_table = {
    'set_eload_current': 0,
    'set_orion_voltage': 1,
    'read_eload_current': 2,
    'read_orion_current': 3,
    'read_orion_voltage': 4
}


class DarkBeastFDef:
    EXIT_STRING = 'Exit'
    RESULT_END_FLAG = '^_^)'
    RESULT_CHECK_FLAG = ')'

    DEFAULT_TIMEOUT = 5
    # delay time, when switch select.
    DELAY_TIME = 0.5
    CAT24C08_ADDR = 0x50

    MIN_ORION_VOLT = 0
    MAX_ORION_VOLT = 10305
    MIN_ELOAD_CURRENT = 0
    MAX_ELOAD_CURRENT = 5000

    CAL_DATA_LEN = 16
    WRITE_CAL_DATA_PACK_FORMAT = '3f4B'
    WRITE_CAL_DATA_UNPACK_FORMAT = '16B'

    READ_CAL_BYTE = 16
    READ_CAL_DATA_PACK_FORMAT = '16B'
    READ_CAL_DATA_UNPACK_FORMAT = '3f4B'


class DarkBeastFCMDDef:
    EXIT = 'EXIT'
    CMD_READ_ELOAD_CURRENT = 'CMD_READ_ELOAD_CURRENT'
    CMD_READ_ORION_VOLTAGE = 'CMD_READ_ORION_VOLTAGE'
    CMD_READ_ORION_CURRENT = 'CMD_READ_ORION_CURRENT'
    CMD_SET_PWR_ORION_INIT = 'CMD_SET_PWR_ORION-0'
    CMD_PWR_ORION_EN_INIT = 'CMD_PWR_ORION_EN-0'
    CMD_PWR_ORION_SW_EN_INIT = 'CMD_PWR_ORION_SW_EN-0'
    CMD_ELOAD_EN_INIT = 'CMD_ELOAD_EN-0'
    CMD_SET_ELOAD_INIT = 'CMD_SET_ELOAD-0'
    CMD_IDBUS_POWER_MODE_PULL_UP = 'CMD_IDBUS_POWER_MODE-0'
    CMD_WAITFORID = 'WAITFORID'
    CMD_IDBUS_POWER_MODE_PULL_DOWN = 'CMD_IDBUS_POWER_MODE-1'


class DarkBeastFAD5592RDef:
    # (Sampling resistance 0.1) * (amplification factor 4.98387) * (partial voltage resistance 2/(2+1))
    ELOAD_READ_GAIN = 0.1 * 4.98387 * 2.0 / (2.0 + 1.0)
    # (Sampling resistance 0.1) * (amplification factor 10) * (partial voltage resistance 2/(8.2+2))
    ORION_CURRENT_READ_GAIN = 0.1 * 10 * 2. / (8.2 + 2.0)
    # (partial voltage resistance 1/(10+1))
    ORION_VOLT_READ_GAIN = 1.0 / (10.0 + 1.0)


class DarkBeastFException(Exception):

    '''
    DarkBeastF exception class.
    '''

    def __init__(self, err_str):
        self.reason = "DarkBeastFException {}".format(err_str)

    def __str__(self):
        return self.reason


class DarkBeastFBase(MIXBoard):

    '''
    Base class of DarkBeastF and DarkBeastFCompatible.

    Providing common DarkBeastF methods.

    Args:
        firmware_path:       string,               DarkBeastF firmware absolute path.
        aid_connect:         instance(GPIO)/None,  Class instance of GPIO, UART RX connect AID to enable or disable,
                                                   if None creating emulator.
        ad5592r:             instance(ADC)/None,   Class instance of AD5592R, if None creating emulator,
        adc_channel:         int,                  Channel id for adc AD5592R.
        i2c:                 instance(I2C)/None,   Class instance of PLI2CBus, which is used to control cat9555,
                                                   eeprom and AD5667 sensor.
        pl_uart_drv_ko_file: string,               DarkBeastF pl uart drive file absolute path.
        ad5667r_drv_ko_file: string,               DarkBeastF ad5667r drive file absolute path.
        eeprom_dev_addr:     int,                  Eeprom device address.

    '''

    rpc_public_api = ['module_init', 'close', 'open', 'communicate',
                      'aid_connect_set', 'set_orion_volt', 'set_eload_current', 'read_eload_current',
                      'read_orion_volt', 'read_orion_current'] + MIXBoard.rpc_public_api

    def __init__(self, firmware_path='', aid_connect=None, ad5592r=None, adc_channel=7, i2c=None,
                 pl_uart_drv_ko_file='', ad5667r_drv_ko_file='', eeprom_dev_addr=DarkBeastFDef.CAT24C08_ADDR):
        self.path = firmware_path
        self.process = None
        self.adc_channel = adc_channel
        self.pl_uart_drv_ko_file = pl_uart_drv_ko_file
        self.ad5667r_drv_ko_file = ad5667r_drv_ko_file
        self.vid = None
        if(firmware_path == '' and aid_connect is None and ad5592r is None and
           i2c is None and pl_uart_drv_ko_file == '' and ad5667r_drv_ko_file == ''):
            self.aid_connect = GPIOEmulator('aid_connect')
            self.ad5592r = AD5592REmulator('ad5592r')
            self.eeprom = EepromEmulator('eeprom_emulator')
            super(DarkBeastFBase, self).__init__(None, None, cal_table=darkbeastf_calibration_info,
                                                 range_table=darkbeastf_range_table)

        elif(firmware_path != '' and aid_connect is not None and ad5592r is not None and
             i2c is not None and pl_uart_drv_ko_file != '' and ad5667r_drv_ko_file != ''):
            self.aid_connect = aid_connect
            self.ad5592r = ad5592r
            self.eeprom = CAT24C08(eeprom_dev_addr, i2c)
            super(DarkBeastFBase, self).__init__(self.eeprom, None,
                                                 cal_table=darkbeastf_calibration_info,
                                                 range_table=darkbeastf_range_table)
        else:
            raise DarkBeastFException('__init__ error! Please check the parameters!')

    def __del__(self):
        self.close()

    def _capture_by_flag(self):
        '''
        capture end flag of result.
        '''
        last_time = time.time()
        data_str = ""
        while(time.time() - last_time < DarkBeastFDef.DEFAULT_TIMEOUT):
            read_str = self.process.stdout.read(1)
            data_str = data_str + read_str
            if read_str == DarkBeastFDef.RESULT_CHECK_FLAG:
                if data_str.endswith(DarkBeastFDef.RESULT_END_FLAG):
                    break
        if time.time() - last_time >= DarkBeastFDef.DEFAULT_TIMEOUT:
            raise DarkBeastFException('process read wait timeout!')

        return data_str.strip(DarkBeastFDef.RESULT_END_FLAG)

    def _update_linux_driver(self):
        ''' update pl_uart_drv.ko if exist '''
        if os.path.isfile(self.pl_uart_drv_ko_file):
            os.system('rmmod ' + self.pl_uart_drv_ko_file)
            os.system('insmod ' + self.pl_uart_drv_ko_file)

        ''' update ad5667r.ko if exist '''
        if os.path.isfile(self.ad5667r_drv_ko_file):
            os.system('rmmod ' + self.ad5667r_drv_ko_file)
            os.system('insmod ' + self.ad5667r_drv_ko_file)

    def module_init(self):
        '''
        DarkBeastF module init：initialize ad5592r channel mode and open darkbeastf process.

        Returns:
            string, return open information.

        Examples:
            DarkBeastf.module_init()

        '''
        self.load_calibration()
        self._update_linux_driver()
        ret_str = 'done'
        if os.path.isfile(self.path):
            ret_str = self.open()
        # config ad5592r channel to ADC mode
        self.ad5592r.channel_config(self.adc_channel, 'ADC')
        # set gpio init
        self.communicate(DarkBeastFCMDDef.CMD_SET_PWR_ORION_INIT)
        self.communicate(DarkBeastFCMDDef.CMD_PWR_ORION_EN_INIT)
        self.communicate(DarkBeastFCMDDef.CMD_PWR_ORION_SW_EN_INIT)
        self.communicate(DarkBeastFCMDDef.CMD_ELOAD_EN_INIT)
        self.communicate(DarkBeastFCMDDef.CMD_SET_ELOAD_INIT)
        self.communicate(DarkBeastFCMDDef.CMD_IDBUS_POWER_MODE_PULL_UP)
        self.communicate(DarkBeastFCMDDef.CMD_WAITFORID)
        self.communicate(DarkBeastFCMDDef.CMD_IDBUS_POWER_MODE_PULL_DOWN)
        self.vid = self.read_vid()
        return ret_str

    def close(self):
        '''
        close the DarkBeastF process.

        Returns:
            string, "done", api execution successful.

        '''
        if self.process is not None:
            string_list = []
            pid_list = []
            pgid = os.getpgid(self.process.pid)

            command = 'ps -C {}'.format(os.path.basename(self.path))
            progress = Popen(command, shell=True, stdin=PIPE, stdout=PIPE)
            string = progress.communicate()[0]
            string_list = string.split("\n")
            for line in string_list:
                pid = re.findall("\d+", line)
                if len(pid) != 0:
                    pid_list.append(pid[0])

            for pid in pid_list:
                if os.getpgid(int(pid)) == pgid:
                    command = "kill " + pid
                    os.system(command)
            self.process = None

        return 'done'

    def open(self):
        '''
        open darkbeastf process by Popen, and return open information or faild raising Exception

        Returns:
            string, return open information.

        '''
        assert os.access(self.path, os.F_OK | os.X_OK), 'path <{}> not exist or execute'.format(self.path)
        if self.process is not None:
            return 'done'

        command = 'cd {};./{}'.format(os.path.dirname(self.path), os.path.basename(self.path))

        # stderr is standard error output, can be file descriptors and STDOUT. None means no output
        self.process = Popen([command, ""], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)

        return self._capture_by_flag()

    def communicate(self, command):
        '''
        communicate with darkbeastf process. if process not open, raise DarkBeastFException

        Args:
            command:  string, command string.

        Returns:
            string, return information.

        Examples:
            cmd_string = "CMD_READ_ELOAD_CURRENT"
            print darkbeastf.communicate(cmd_string)

        Raises:
            DarkBeastFException:  process not open, communicate error!

        '''
        if self.process is not None:
            self.process.stdin.write(command + "\n")
            if DarkBeastFCMDDef.EXIT == command:
                self.process = None
                return DarkBeastFDef.EXIT_STRING
            else:
                return self._capture_by_flag()

        raise DarkBeastFException('process not open, communicate error!')

    def aid_connect_set(self, status):
        '''
        AID connect to dut enable or disable

        Args:
            status:  string, ['enable', 'disable'].

        Returns:
            string, "done", api execution successful.

        Examples:
            darkbeastf.aid_connect_set(1)

        '''
        assert status in ('enable', 'disable')
        if status == 'enable':
            level = 1
        else:
            level = 0
        self.aid_connect.set_level(level)

        return 'done'

    def set_orion_volt(self, volt):
        '''
        Orion Power voltage setting

        Args:
            volt:    float, [0~10305], unit mv, output voltage value.

        Returns:
            string, string, return information.

        Examples:
            darkbeastf.set_orion_volt(3000)

        '''
        assert isinstance(volt, (int, float))
        assert volt >= DarkBeastFDef.MIN_ORION_VOLT
        assert volt <= DarkBeastFDef.MAX_ORION_VOLT

        volt = self.calibrate('set_orion_voltage', volt)

        return self.communicate('CMD_SET_PWR_ORION-{}'.format(volt))

    def set_eload_current(self, current):
        '''
        CC_Eload(Constant Current Eload) current setting

        Args:
            current:     float, [0~5000], unit mv, output voltage value.

        Returns:
            string, return information.

        Examples:
            darkbeastf.set_eload_current(1000)

        '''
        assert isinstance(current, (int, float))
        assert current >= DarkBeastFDef.MIN_ELOAD_CURRENT
        assert current <= DarkBeastFDef.MAX_ELOAD_CURRENT

        current = self.calibrate('set_eload_current', current)

        return self.communicate('CMD_SET_ELOAD-{}'.format(current))

    def read_eload_current(self):
        '''
        CC_Eload(Constant Current Eload) current read back

        Returns:
            float, value, unit mA, reback current value.

        Examples:
            result = darkbeastf.read_eload_current()
            print(result)

        '''
        self.communicate(DarkBeastFCMDDef.CMD_READ_ELOAD_CURRENT)  # just for select switch

        # delay 0.5s, when switch select. If less than 0.5s, volt inaccuracy.
        time.sleep(DarkBeastFDef.DELAY_TIME)

        current = self.ad5592r.read_volt(self.adc_channel)
        current /= DarkBeastFAD5592RDef.ELOAD_READ_GAIN

        current = self.calibrate('read_eload_current', current)

        return current

    def read_orion_volt(self):
        '''
        Orion Power voltage reading

        Returns:
            float, value, unit mV, reback voltage value.

        Examples:
            result = darkbeastf.read_orion_volt()
            print(result)

        '''
        self.communicate(DarkBeastFCMDDef.CMD_READ_ORION_VOLTAGE)  # just for select switch

        # delay 0.5s, when switch select. If less than 0.5s, volt inaccuracy.
        time.sleep(DarkBeastFDef.DELAY_TIME)

        volt = self.ad5592r.read_volt(self.adc_channel)
        volt /= DarkBeastFAD5592RDef.ORION_VOLT_READ_GAIN

        volt = self.calibrate('read_orion_voltage', volt)

        return volt

    def read_orion_current(self):
        '''
        Orion Power current reading.

        Returns:
            float, value, unit mA, reback current value.

        Examples:
            result = darkbeastf.read_orion_current()
            print(result)

        '''
        self.communicate(DarkBeastFCMDDef.CMD_READ_ORION_CURRENT)  # just for select switch

        # delay 0.5s, when switch select. If less than 0.5s, volt inaccuracy.
        time.sleep(DarkBeastFDef.DELAY_TIME)

        current = self.ad5592r.read_volt(self.adc_channel)
        current /= DarkBeastFAD5592RDef.ORION_CURRENT_READ_GAIN

        current = self.calibrate('read_orion_current', current)

        return current

    def load_legacy_calibration(self):
        '''
        Load legacy calibration data.

        This function is used to load legacy calibration data which is compatible with xavier5.0.

        '''
        self._calibration_table = {}
        for range_name in self._legacy_cal_table:
            self._calibration_table[range_name] = []
            for level in self._legacy_cal_table[range_name]:
                result = self.legacy_read_calibration_cell(
                    range_name, self._legacy_cal_table[range_name][level]['unit_index'])
                self._calibration_table[range_name].append(result)
        return "done"

    def legacy_write_calibration_cell(self, cal_name, unit_index, gain, offset, threshold):
        '''
        DarkBeastF calibration data write

        Args:
            cal_name:     string, ['set_eload_current', 'set_orion_voltage',
                                   'read_eload_current', 'read_orion_current',
                                   'read_orion_voltage'], calibration name.
            unit_index:   int,    calibration unit index.
            gain:         float,  calibration gain.
            offset:       float,  calibration offset.
            threshold:    float,  if value < threshold, use this calibration unit data.

        Returns:
            string, "done", api execution successful.

        Examples:
            board.write_calibration_cell(0, 1.1, 0.1, 1000, 'set_eload_current')

        Raises:
            BoardArgCheckError: unit_index < 0 or type is not int.
            calibration unit format:
                Meaning:    Gain,     Offset,   threshold value, Use flag
                Mem size:   4Bytes,   4Bytes,   4Bytes,            Byte
                Data type:  float,    float,    float,            uint8_t
                Formula:    Y = Gain * X  + Offset

        '''
        assert cal_name in ["set_eload_current", "set_orion_voltage", "read_eload_current",
                            "read_orion_current", "read_orion_voltage"]
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        use_flag = self.calibration_info["use_flag"]
        data = (gain, offset, threshold, use_flag, 0xff, 0xff, 0xff)
        s = struct.Struct(DarkBeastFDef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(DarkBeastFDef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = darkbeastf_calibration_base_addr[cal_name] + DarkBeastFDef.CAL_DATA_LEN * unit_index
        self.write_eeprom(address, data)

    def legacy_read_calibration_cell(self, cal_name, unit_index):
        '''
        DarkBeastF read calibration data

        Args:
            cal_name:     string, ['set_eload_current', 'set_orion_voltage',
                                   'read_eload_current', 'read_orion_current',
                                   'read_orion_voltage'], calibration name.
            unit_index:   int, calibration unit index.

        Returns:
            dict, {"gain": value, "offset": value, "threshold": value, "is_use": value}.

        Examples:
            data = board.read_calibration_cell('set_eload_current', 0)
            print(data)

        Raises:
            BoardArgCheckError: unit_index < 0 or type is not int.
            calibration unit format:
                Meaning:    Gain,     Offset,   threshold value, Use flag
                Mem size:   4Bytes,   4Bytes,   4Bytes,            Byte
                Data type:  float,    float,    float,            uint8_t
                Formula:    Y = Gain * X  + Offset

        '''
        assert cal_name in ["set_eload_current", "set_orion_voltage", "read_eload_current",
                            "read_orion_current", "read_orion_voltage"]
        if not isinstance(unit_index, int) or unit_index < 0:
            raise BoardArgCheckError(
                "calibration unit memory unit_index data type is not int type or unit_index < 0")

        address = darkbeastf_calibration_base_addr[cal_name] + DarkBeastFDef.CAL_DATA_LEN * unit_index
        data = self.read_eeprom(address, DarkBeastFDef.READ_CAL_BYTE)

        s = struct.Struct(DarkBeastFDef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(DarkBeastFDef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        use_flag = result[3]
        if self.calibration_info["use_flag"] != use_flag:
            return {"gain": 1.0, "offset": 0.0, "threshold": 0.0, "is_use": False}
        else:
            return {"gain": result[0], "offset": result[1], "threshold": result[2], "is_use": True}


class DarkBeastF(DarkBeastFBase):

    '''
    Dark Beast-F is a keyboard peripheral simulation module.

    compatible = ["GQQ-OAF001004-000"]

    OAB is the abbreviation of Orion accessory board,
    and F stands for FATP station. The interface between the module and DUT has three connection points.
    DATA_ORION is the communication interface to carry out AID (slave) communication and UART communication
    with DUT, with the highest UART communication rate of 1Mbps. PWR_ORIN is the power interface. The first is
    the power supply capacity of DUT tested as CC ELOAD, and the second is to charge DUT as the power supply
    interface. A mock switch is also included for contamination testing at the DUT ORION interface point.
    This class is legacy driver for normal boot.

    Args:
        firmware_path:       string,               DarkBeastF firmware absolute path.
        aid_connect:         instance(GPIO)/None,  Class instance of GPIO, UART RX connect AID to enable or disable,
                                                   if None creating emulator.
        ad5592r:             instance(ADC)/None,   Class instance of AD5592R, if None creating emulator,
        adc_channel:         int,                  Channel id for adc AD5592R.
        i2c:                 instance(I2C)/None,   Class instance of PLI2CBus, which is used to control cat9555,
                                                   eeprom and AD5667 sensor.
        pl_uart_drv_ko_file: string,               DarkBeastF pl uart drive file absolute path.
        ad5667r_drv_ko_file: string,               DarkBeastF ad5667r drive file absolute path.

    Examples:
        axi4_bus = AXI4LiteBus('/dev/MIX_SPI_0', 256)
        spi_bus = PLSPIBus(axi4_bus)

        firmware_path = '/root/AID_OAB3_FATP_v1_0_12_DOE8.elf'
        aid_connect = GPIO(59)
        ad5592r = AD5592R(spi_bus, 2500, 'internal', 1, 2)
        adc_channel = 7
        i2c = I2C('/dev/i2c-0')
        pl_uart_drv_ko_file = '/mix/driver/module/pl_uart_drv.ko'
        # driver for ad5667r
        ad5667r_drv_ko_file = '/mix/driver/module/ad5064.ko'
        darkbeastf = DarkBeastF(firmware_path, aid_connect, ad5592r, adc_channel, i2c)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-OAF001004-000"]

    def __init__(self, firmware_path='', aid_connect=None, ad5592r=None, adc_channel=7, i2c=None,
                 pl_uart_drv_ko_file='', ad5667r_drv_ko_file=''):
        super(DarkBeastF, self).__init__(firmware_path, aid_connect, ad5592r, adc_channel, i2c,
                                         pl_uart_drv_ko_file, ad5667r_drv_ko_file, DarkBeastFDef.CAT24C08_ADDR)
