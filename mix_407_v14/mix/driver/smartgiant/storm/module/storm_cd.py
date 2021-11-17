# -*- coding: utf-8 -*-
import os
import struct
import time
from mix.driver.core.ic.cat24cxx import CAT24C64
from mix.driver.smartgiant.storm.module.storm import StormBase
from mix.driver.smartgiant.storm.module.spill import SPILL


__author__ = 'yuanle@SmartGiant'
__version__ = '0.3'


class StormDef:
    ADC_CURR_SRC_RATIO_C = 4.0 * 440 / 240
    ADC_CURR_SRC_RATIO_D = 4.0 * 474 / 274
    ADC_CURR_SRC_CHANNEL = 1  # AIN2-AIN3
    EEPROM_DEV_ADDR = 0x52
    SPILL_EEPROM_DEV_ADDR = 0x53
    DAC_DEV_ADDR = 0x0D

    ADC_VOLT_RATIO = 7.8
    ADS1119_VOLT_RATIO = 4.0
    ADC_CURR_SINK_RATIO = 4.0
    MAX_BUCK_OUT = 12800  # mV
    MIN_BUCK_OUT = 7200  # mV
    MAX_OC_CURR = 24300  # mA
    MIN_OC_CURR = 2050  # mA
    MAX_VGAP = 500  # mV
    MIN_VGAP = 5  # mV
    MAX_RINT = 1  # ohm
    MIN_RINT = 0.01  # ohm
    DAC_VOLT_CHANNEL = 0  # 'DAC_A'

    ADS1119_DEV_ADDR = 0x40
    ADS1119_VOLT_CHANNEL = 3  # AIN0-AGND
    ADS1119_CURR_SINK_CHANNEL = 4  # AIN1-AGND
    ADS1119_CURR_SRC_CHANNEL = 5  # AIN2-AGND
    ADS1119_CURR_REM_CHANNEL = 6  # AIN3-AGND
    ADC_VOLT_CHANNEL = 2  # AIN0-AIN3
    ADC_CURR_SINK_CHANNEL = 3  # AIN1-AIN3
    AD7606_RANGE = 5  # V
    CONVST_DELAY = 0.0001  # 100uS
    DEFAULT_TIMEOUT = 100
    # MCP23008 Pins
    PIN_ADC_CONVST = 2  # AD7606
    PIN_ADC_BUSY = 3  # AD7606 input

    CALIBRATION_COE_MAP_1 = {
        'a_volt': [0x0500, 0x0503],
        'b_volt': [0x0508, 0x050B],
        'a_sink_curr': [0x0510, 0x0513],
        'b_sink_curr': [0x0518, 0x051B],
        'a_src_curr': [0x0520, 0x0523],
        'b_src_curr': [0x0528, 0x052B],
    }

    CALIBRATION_COE_MAP_2 = {
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
    CONFIG_LIST = ["740", "030", "040"]
    TIMEOUT = 1  # s
    IO_INIT_DIR = [0x08]
    IO_INIT_STATE = [0x82]
    LOCAL_OT = 90  # Celsius
    SN_ADDR = 0x03
    SN_LEN = 17


class StormException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class StormCD(StormBase):
    '''
    Storm (Battery Emulator) is a bi-directional DC power supply.

    It can simulate the charging and discharging functions of battery
    with the maximum output power of 120W and the maximum sink current of 6A.

    Note:
    1. The I2C Bus Speed is 100KHz.
    2. FT4222 firmwave: FT4222-arm.tar.gz
        install driver: bash /path/install4222.sh
        gpiow: /path/dist/gpiow 0 2 1
        spimr: /path/spimr 0 1 64 1 1 1 8

    Args:
        i2c:                 instance(I2C)/None, Class instance of PLI2CBus, which is used to access
                                                 CAT24C64,MCP23008, ADS1112, AD5696, CAT9555, MAX6642.
        ft4222_gpiow_file:   string,             FT4222 gpiow firmware file absolute path.
        ft4222_spimr_file:   string,             FT4222 spimr firmware file absolute path.
        eeprom_devaddr:      int,                Eeprom device address.
        spill:              instance/None, Class instance of SPILL board.

    Examples:
        # Create Instance: i2c speed 100KHz
        axi4_bus = AXI4LiteBus('/dev/MIX_I2C_0', 256)
        i2c_bus = PLI2CBus(axi4_bus)
        i2c_bus.set_speed(100000)
        ft4222_gpiow_file = '/root/FT4222-arm/dist/gpiow'
        ft4222_spimr_file = '/root/FT4222-arm/dist/spimr'
        storm = Storm(i2c_bus, ft4222_gpiow_file, ft4222_spimr_file)

        # enable calibration mode 'raw' or 'cal'
        storm.set_calibration_mode('raw')

        # measure the output voltage, Terminal will show "[xxx.xxx, 'mV']"
        result = storm.read_output_voltage()
        print(result)

        # measure the source current, Terminal will show "[xxx.xxx, 'mA']"
        result = storm.read_source_current()
        print(result)

        # measure the sink current, Terminal will show "[xxx.xxx, 'mA']"
        result = storm.read_sink_current()
        print(result)

        # get the local temperature, Terminal will show "[xx.xx, 'Celsius']"
        result = storm.get_local_temperature()
        print(result)

        # get the remote temperature, Terminal will show "[xx.xx, 'Celsius']"
        result = storm.get_remote_temperature()
        print(result)

        # set the output voltage
        storm.set_output_voltage(7201)

        # FT4222
        # Enable MCP23008 and active AD7606
        storm.ft4222_enable_measure()

        # Measure output voltage and output current via AD7606
        # Terminal will show "{'source_current': (xx.xx, 'mA'), 'voltage': (xx.xx, 'mV'),
                'sink_current': (xx.xx, 'mA')}"
        result = storm.ft4222_measure()
        print(result)

    '''
    rpc_public_api = ['module_init', 'set_oc', 'set_vgap', 'set_rint', 'read_rem_volt', 'tmp_read_src',
                      'tmp_read_sink_int', 'tmp_read_sink_ext', 'temp_write_limit_src',
                      'temp_read_limit_src', 'temp_write_limit_sink_int', 'temp_read_limit_sink_int',
                      'temp_write_limit_sink_ext', 'temp_read_limit_sink_ext', 'buck_off', 'src_off',
                      'sink_off', 'all_on'] + StormBase.rpc_public_api

    # launcher will use this to match driver compatible string and load driver if matched.

    compatible = ["GQQ-MJ28-02C", "GQQ-MJ28-73C", "GQQ-MJ28-02D", "GQQ-MJ28-73D", "GQQ-MJ28-740",
                  "GQQ-MJ28-030", "GQQ-MJ28-040"]

    def __init__(self, i2c=None, ft4222_gpiow_file='', ft4222_spimr_file='', spill=None):
        super(StormCD, self).__init__(i2c, ft4222_gpiow_file, ft4222_spimr_file,
                                      StormDef.EEPROM_DEV_ADDR, spill)
        self._record_common_error = None
        self._record_mismatch_error = None
        self.i2c = i2c

    def module_init(self):
        '''
        Storm module initialization

        User need to call this function once before using the module.

        Returns:
            string, "done", api execution successful.

        Examples:
            storm.module_init()

        '''
        self._record_common_error = None
        self._record_mismatch_error = None

        try:
            self.load_calibration()
            self.ad5696.output_volt(StormDef.DAC_VOLT_CHANNEL, 0)
            if self._hardware_version in StormDef.CONFIG_LIST:
                # PCA9554 config
                self.pca9554.set_pins_dir(StormDef.IO_INIT_DIR)
                self.pca9554.set_ports(StormDef.IO_INIT_STATE)
                self.backpack_max6642.write_high_limit("local", StormDef.LOCAL_OT)
                self.i2c.write(StormDef.DAC_DEV_ADDR, [0x38, 0x7F, 0xFF])
                self.i2c.write(StormDef.DAC_DEV_ADDR, [0x34, 0xDE, 0x27])
                self.ads1119.init()

                self._backpack_hw_sn = self.read_serial_number()
                self.spill_eeprom = CAT24C64(StormDef.SPILL_EEPROM_DEV_ADDR, self.i2c)
                self._spill_hw_sn = self._read_spill_serial_number()
                if self._spill_hw_sn != self._backpack_hw_sn:
                    self._record_mismatch_error = StormException(
                        "The serial number of the spill board does not match the backpack board")
                    return
                if self.spill is None:
                    self.spill = SPILL(self.i2c)
                self.spill.reset()
            return
        except Exception as e:
            self._record_common_error = StormException(
                "The spill may not be connected or the initialization failed: " + str(e))
            return

    def _read_spill_serial_number(self):
        '''
        returns a string that represents the serial number string of spill board.
        '''
        sn_str = bytearray(self.spill_eeprom.read(StormDef.SN_ADDR, StormDef.SN_LEN))
        return "".join([chr(c) for c in sn_str])

    def set_output_voltage(self, volt):
        '''
        Storm set the output voltage via The AD5696 DAC with I2C interface.

        Args:
            volt:   float, [7200.1~12800], unit mV, output voltage.

        Returns:
            string, "done", api execution successful.

        Examples:
            storm.set_output_voltage(12800)

        '''
        assert isinstance(volt, (int, float))
        assert StormDef.MIN_BUCK_OUT < volt <= StormDef.MAX_BUCK_OUT

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            if self.is_use_cal_data():
                vmax = self.legacy_read_calibration_cell('max_set_volt')
                vmin = self.legacy_read_calibration_cell('min_set_volt')
            else:
                vmax = 12.8
                vmin = 7.2
            volt = volt / 1000.0  # mV convert to V
            cdw_v = (1 - (volt - vmin) / (vmax - vmin)) * 65535
            cdw_v = int(cdw_v)
            byte1 = (cdw_v >> 8) & 255
            byte2 = cdw_v & 255
            self.i2c.write(StormDef.DAC_DEV_ADDR, [49, byte1, byte2])
        else:
            volt_val = self._volt_to_dac(volt)
            self.ad5696.output_volt(StormDef.DAC_VOLT_CHANNEL, volt_val)

        return "done"

    def set_oc(self, threshold):
        '''
        Storm set source current OC threshold.

        Args:
            threshold:   float, [2050~24300], unit mA, threshold current to set value.

        Returns:
            string, "done", api execution successful.

        Examples:
            storm.set_oc(10000)

        '''
        assert isinstance(threshold, (int, float))
        assert StormDef.MIN_OC_CURR <= threshold <= StormDef.MAX_OC_CURR

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            threshold = threshold / 1000.0  # mA convert to A
            cdw_v = 2933.1265 * threshold - 6000
            cdw_v = int(cdw_v)
            byte1 = (cdw_v >> 8) & 255
            byte2 = cdw_v & 255
            self.i2c.write(StormDef.DAC_DEV_ADDR, [50, byte1, byte2])
        else:
            raise StormException("No concerte implmenetation for setting OC in this driver")

        return "done"

    def set_vgap(self, gap_volt):
        '''
        Storm set the gap voltage between battery mulator sourced output voltage, and
        external voltage, sinking the current will start at gap_volt is the gap voltage to set value.

        Args:
            gap_volt:   float, [5~500], unit mV,  gap voltage to set value.

        Returns:
            string, "done", api execution successful.

        Examples:
            storm.set_vgap(500)

        '''
        assert isinstance(gap_volt, (int, float))
        assert StormDef.MIN_VGAP <= gap_volt <= StormDef.MAX_VGAP

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            if self.is_use_cal_data():
                vmax = self.legacy_read_calibration_cell('max_set_vgap')
                vmin = self.legacy_read_calibration_cell('min_set_vgap')
            else:
                vmax = 0.0925
                vmin = -0.6066
            gap_volt = gap_volt / 1000.0  # mV convert to V
            cdw_v = ((-gap_volt - vmin) / (vmax - vmin)) * 65535
            cdw_v = int(cdw_v)
            byte1 = (cdw_v >> 8) & 255
            byte2 = cdw_v & 255
            self.i2c.write(StormDef.DAC_DEV_ADDR, [52, byte1, byte2])
        else:
            raise StormException("No concerte implmenetation for setting Vgap in this driver")

        return "done"

    def set_rint(self, resistance):
        '''
        Set the emulated battery internal resistance for sinking the current.

        Args:
            resistance:    float/int, [0.01~1], unit ohm, battery internal resistance to set value in ohm.

        Returns:
            string, "done", api execution successful.

        Examples:
            storm.set_rint(1)

        '''
        assert isinstance(resistance, (int, float))
        assert StormDef.MIN_RINT <= resistance <= StormDef.MAX_RINT

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            if self._record_common_error is not None:
                raise self._record_common_error
            if self.is_use_cal_data():
                a_res = self.legacy_read_calibration_cell('a_set_rint')
                b_res = self.legacy_read_calibration_cell('b_set_rint')
                res = self.cal_pipe(a_res, b_res, resistance)
            self.spill.set_rint(res)
        else:
            raise StormException("No concerte implmenetation for setting rint in this driver")

        return "done"

    def read_output_voltage(self):
        '''
        Storm measure the output voltage via the ADS1112 ADC with I2C interface.

        Returns:
            list,   [value, 'mV'].

        Examples:
            storm.read_output_voltage()

        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            volt_val = self.ads1119.read_volt(StormDef.ADS1119_VOLT_CHANNEL)
            volt_val *= StormDef.ADS1119_VOLT_RATIO
        else:
            volt_val = self.ads1112.read_volt(StormDef.ADC_VOLT_CHANNEL)
            volt_val *= StormDef.ADC_VOLT_RATIO

        if self.is_use_cal_data():
            volt_val = volt_val / 1000.0  # mV convert to V
            a_volt = self.legacy_read_calibration_cell('a_volt')
            b_volt = self.legacy_read_calibration_cell('b_volt')
            volt_val = self.cal_pipe(a_volt, b_volt, volt_val)
            volt_val = volt_val * 1000.0  # V convert to mV

        return [volt_val, 'mV']

    def read_rem_volt(self):
        '''
        Storm read the remote measurement of the battery emulator output voltage value.

        Returns:
            list,   [value, 'mV'].

        Examples:
            storm.read_rem_volt()

        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            volt_val = self.ads1119.read_volt(StormDef.ADS1119_CURR_REM_CHANNEL)
            volt_val *= StormDef.ADS1119_VOLT_RATIO
        else:
            raise StormException("No concerte implmenetation for reding remote voltage in this driver")

        if self.is_use_cal_data():
            volt_val = volt_val / 1000.0  # mV convert to V
            a_volt = self.legacy_read_calibration_cell('a_rem_volt')
            b_volt = self.legacy_read_calibration_cell('b_rem_volt')
            volt_val = self.cal_pipe(a_volt, b_volt, volt_val)
            volt_val = volt_val * 1000.0  # V convert to mV

        return [volt_val, 'mV']

    def read_source_current(self):
        '''
        Storm measure the source current.

        Returns:
            list,   [value, 'mA'].

        Examples:
            storm.read_source_current()

        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            volt_val = self.ads1119.read_volt(StormDef.ADS1119_CURR_SRC_CHANNEL)
            current = volt_val * 6.0 / 1000.0
            if current < 6.144:  # 8192 * 4096.0 / 32768 * 6.0 / 1000.0 = 6.144A
                level = 0
                self.ads1119.set_gain(4)
                current = self.ads1119.read_volt(StormDef.ADS1119_CURR_SRC_CHANNEL)
            else:
                level = 1
                current = self.ads1119.read_volt(StormDef.ADS1119_CURR_SRC_CHANNEL)
            self.ads1119.set_gain(1)
            curr_val = 6.0 * current

            if self.is_use_cal_data():
                curr_val = curr_val / 1000.0  # mA convert to A
                a_src_curr = self.legacy_read_calibration_cell('a_src_curr', level)
                b_src_curr = self.legacy_read_calibration_cell('b_src_curr', level)
                curr_val = self.cal_pipe(a_src_curr, b_src_curr, curr_val)
                curr_val = curr_val * 1000.0  # A convert to mA
                if curr_val < 0:
                    curr_val = 0
        else:
            curr_val = self.ads1112.read_volt(StormDef.ADC_CURR_SRC_CHANNEL)

            if self._hardware_version in ['02D', '73D']:
                curr_val *= StormDef.ADC_CURR_SRC_RATIO_D
            else:
                curr_val *= StormDef.ADC_CURR_SRC_RATIO_C

            if self.is_use_cal_data():
                curr_val = curr_val / 1000.0  # mA convert to A
                a_src_curr = self.legacy_read_calibration_cell('a_src_curr')
                b_src_curr = self.legacy_read_calibration_cell('b_src_curr')
                curr_val = self.cal_pipe(a_src_curr, b_src_curr, curr_val)
                curr_val = curr_val * 1000.0  # A convert to mA

        return [curr_val, 'mA']

    def read_sink_current(self):
        '''
        Storm measure the sink current.

        Returns:
            list,   [value, 'mA'].

        Examples:
            storm.read_sink_current()

        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            volt_val = self.ads1119.read_volt(StormDef.ADS1119_CURR_SINK_CHANNEL)
            current = volt_val * 3.0 / 1000.0
            if current < 3.072:  # 8192 * 4096.0 / 32768 * 3.0 / 1000.0 = 3.072A
                level = 0
                self.ads1119.set_gain(4)
                current = self.ads1119.read_volt(StormDef.ADS1119_CURR_SINK_CHANNEL)
            else:
                level = 1
                current = self.ads1119.read_volt(StormDef.ADS1119_CURR_SINK_CHANNEL)
            self.ads1119.set_gain(1)
            curr_val = 3.0 * current

            if self.is_use_cal_data():
                curr_val = curr_val / 1000.0  # mA convert to A
                a_sink_curr = self.legacy_read_calibration_cell('a_sink_curr', level)
                b_sink_curr = self.legacy_read_calibration_cell('b_sink_curr', level)
                curr_val = self.cal_pipe(a_sink_curr, b_sink_curr, curr_val)
                curr_val = curr_val * 1000.0  # A convert to mA
                if curr_val < 0:
                    curr_val = 0
        else:
            curr_val = self.ads1112.read_volt(StormDef.ADC_CURR_SINK_CHANNEL)
            curr_val *= StormDef.ADC_CURR_SINK_RATIO

            if self.is_use_cal_data():
                curr_val = curr_val / 1000.0  # mA convert to A
                a_sink_curr = self.legacy_read_calibration_cell('a_sink_curr')
                b_sink_curr = self.legacy_read_calibration_cell('b_sink_curr')
                curr_val = self.cal_pipe(a_sink_curr, b_sink_curr, curr_val)
                curr_val = curr_val * 1000.0  # A convert to mA

        return [curr_val, 'mA']

    def tmp_read_src(self):
        '''
        read the backpack temperature sensor, returns temperature in degC.

        Returns:
            list,   [value, 'Celsius'].

        Examples:
            storm.tmp_read_src()

        '''

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            val = self.backpack_max6642.get_temperature("local", extended=True)
        else:
            raise StormException("No concerte implmenetation for reading source temperature in this driver")

        return [val, 'Celsius']

    def tmp_read_sink_int(self):
        '''
        read the spill internal temperature sensor, returns temperature in degC.

        Returns:
            list,   [value, 'Celsius'].

        Examples:
            storm.tmp_read_sink_int()

        '''

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            if self._record_common_error is not None:
                raise self._record_common_error
            val = self.spill.get_temperature("local")
        else:
            raise StormException("No concerte implmenetation for reading sink internal temperature in this driver")

        return [val, 'Celsius']

    def tmp_read_sink_ext(self):
        '''
        read the spill external temperature sensor, returns temperature in degC.

        Returns:
            list,   [value, 'Celsius'].

        Examples:
            storm.tmp_read_sink_ext()

        '''

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            if self._record_common_error is not None:
                raise self._record_common_error
            val = self.spill.get_temperature("remote")
        else:
            raise StormException("No concerte implmenetation for reading sink external temperature in this driver")

        return [val, 'Celsius']

    def temp_write_limit_src(self, limit):
        '''
        Write the backpack local high limit.

        Args:
            limit:      int, [0~255], temperature limit.

        Returns:
            string, "done", "done" for success

        Examples:
            storm.temp_write_limit_src(90)

        '''

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            self.backpack_max6642.write_high_limit("local", limit)
        else:
            raise StormException("No concerte implmenetation for writing source limit temperature in this driver")

        return "done"

    def temp_read_limit_src(self):
        '''
        read the backpack local limit temperature, returns limit temperature in degC.

        Returns:
            list,   [value, 'Celsius'].

        Examples:
            storm.temp_read_limit_src()

        '''

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            val = self.backpack_max6642.read_high_limit("local")
        else:
            raise StormException("No concerte implmenetation for reading source limit temperature in this driver")

        return [val, 'Celsius']

    def temp_write_limit_sink_int(self, limit):
        '''
        Write the spill local high limit.

        Args:
            limit:      int, [0~255], temperature limit.

        Returns:
            string, "done", "done" for success

        Examples:
            storm.temp_write_limit_sink_int(90)

        '''

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            if self._record_common_error is not None:
                raise self._record_common_error
            self.spill.write_high_limit("local", limit)
        else:
            raise StormException("No concerte implmenetation for writing sink limit temperature in this driver")

        return "done"

    def temp_read_limit_sink_int(self):
        '''
        read the spill local temperature sensor, returns limit temperature in degC.

        Returns:
            list,   [value, 'Celsius'].

        Examples:
            storm.temp_read_limit_sink_int()

        '''

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            if self._record_common_error is not None:
                raise self._record_common_error
            val = self.spill.read_high_limit("local")
        else:
            raise StormException("No concerte implmenetation for reading sink limit temperature in this driver")

        return [val, 'Celsius']

    def temp_write_limit_sink_ext(self, limit):
        '''
        Write the spill remote high limit.

        Args:
            limit:      int, [0~255], temperature limit.

        Returns:
            string, "done", "done" for success

        Examples:
            storm.temp_write_limit_sink_ext(90)

        '''

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            if self._record_common_error is not None:
                raise self._record_common_error
            self.spill.write_high_limit("remote", limit)
        else:
            raise StormException("No concerte implmenetation for writing sink limit temperature in this driver")

        return "done"

    def temp_read_limit_sink_ext(self):
        '''
        read the spill remote temperature sensor, returns limit temperature in degC.

        Returns:
            list,   [value, 'Celsius'].

        Examples:
            storm.temp_read_limit_sink_ext()

        '''

        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            if self._record_common_error is not None:
                raise self._record_common_error
            val = self.spill.read_high_limit("remote")
        else:
            raise StormException("No concerte implmenetation for reading sink limit temperature in this driver")

        return [val, 'Celsius']

    def buck_off(self):
        '''
         Turn off the main buck converter of the battery emulator.

         Returns:
            string, "done", "done" for success

        Examples:
            storm.buck_off()
        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            self.pca9554.set_ports([0x83])
        else:
            raise StormException("No concerte implmenetation for turning off the main buck converter in this driver")

        return "done"

    def src_off(self):
        '''
         Turn off source voltage output.

         Returns:
            string, "done", "done" for success

        Examples:
            storm.src_off()
        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            self.pca9554.set_ports([0xA2])
        else:
            raise StormException("No concerte implmenetation for disable source voltage in this driver")

        return "done"

    def sink_off(self):
        '''
         Turn off sink voltage output.

         Returns:
            string, "done", "done" for success

        Examples:
            storm.sink_off()
        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            self.pca9554.set_ports([0x92])
        else:
            raise StormException("No concerte implmenetation for disable sink voltage in this driver")

        return "done"

    def all_on(self):
        '''
         Turn on the battery emulator voltage output.

         Returns:
            string, "done", "done" for success

        Examples:
            storm.all_on()
        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            self.pca9554.set_ports([0x82])
        else:
            raise StormException("No concerte implmenetation for battery emulator voltage output in this driver")

        return "done"

    def ft4222_measure(self):
        '''
        Storm Measure output voltage and output current through USB interface to SPI bridge.

        Command: spimr device ioLine clockDiv clockPolarity clockPhase ssoMap number-of-bytes-to-read
                 spimr 0 1 64 1 1 1 8
                 Terminal shows: ['locID = xxxx\n', '2a63001d00273086\n']

        Returns:
            dict, {"voltage":[value, 'mV'], "sink_current":[value, 'mA'], "source_current":[value, 'mA']}.

        Raise:
            StormException('AD7606 Check busy state timeout!')
            StormException('FT4222H is not connected, please check it!')

        '''
        assert os.access(self.ft4222_spimr_file, os.F_OK | os.X_OK), 'path <{}> not exist or execute'.format(
            self.ft4222_spimr_file)

        # Maximum 0.5ms delay between CONVST A,CONVST B rising edges
        if self._hardware_version in StormDef.CONFIG_LIST:
            if self._record_mismatch_error is not None:
                raise self._record_mismatch_error
            self.pca9554.set_pin(StormDef.PIN_ADC_CONVST, 0)
            time.sleep(StormDef.CONVST_DELAY)
            self.pca9554.set_pin(StormDef.PIN_ADC_CONVST, 1)
        else:
            self.mcp23008.set_pin(StormDef.PIN_ADC_CONVST, 0)
            time.sleep(StormDef.CONVST_DELAY)
            self.mcp23008.set_pin(StormDef.PIN_ADC_CONVST, 1)

        # Check AD7606 BUSY_PIN state, The BUSY output remains high
        # until the conversion process for all channels is complete.
        last_time = time.time()
        while(time.time() - last_time < StormDef.DEFAULT_TIMEOUT):
            time.sleep(StormDef.CONVST_DELAY)
            if self._hardware_version in StormDef.CONFIG_LIST:
                if self.pca9554.get_pin(StormDef.PIN_ADC_BUSY) == 0:
                    break
            else:
                if self.mcp23008.get_pin(StormDef.PIN_ADC_BUSY) == 0:
                    break
        if time.time() - last_time >= StormDef.DEFAULT_TIMEOUT:
            raise StormException('AD7606 Check busy state timeout!')

        # Run `spimr 0 1 64 1 1 1 8` and get the stdout
        cmd = self.ft4222_spimr_file + ' 0 1 64 1 1 1 8'
        output = os.popen(cmd).readlines()

        if len(output) == 2 and 'locID' in output[0]:
            data = output[1].strip("\n")
            if len(data) != 16:
                raise StormException('FT4222H spimr return error data (16 bytes is correct)')

            # 8 bytes, bytes 7&8 reserve
            # bytes 1&2 are voltage
            cdw = int(data[0:2], 16) * 256 + int(data[2:4], 16)
            volt = StormDef.ADC_VOLT_RATIO * StormDef.AD7606_RANGE * cdw / 32768
            volt *= 1000
            # bytes 3&4 are sinking current
            cdw = int(data[4:6], 16) * 256 + int(data[6:8], 16)
            sink_curr = StormDef.ADC_CURR_SINK_RATIO * StormDef.AD7606_RANGE * cdw / 32768
            sink_curr *= 1000
            # bytes 5&6 are sourcing current
            cdw = int(data[8:10], 16) * 256 + int(data[10:12], 16)
            if self._hardware_version in ['02D', '73D', '740', '030', '040']:
                source_curr = StormDef.ADC_CURR_SRC_RATIO_D * StormDef.AD7606_RANGE * cdw / 32768
            else:
                source_curr = StormDef.ADC_CURR_SRC_RATIO_C * StormDef.AD7606_RANGE * cdw / 32768
            source_curr *= 1000

            result = {}
            result['voltage'] = (volt, 'mV')
            result['sink_current'] = (sink_curr, 'mA')
            result['source_current'] = (source_curr, 'mA')
            return result
        else:
            raise StormException('FT4222H is not connected, please check it!')

    def legacy_write_calibration_cell(self, cal_item, cal_value, cal_index=0):
        '''
        MIXBoard calibration data write.

        Args:
            cal_item:   string, ['a_volt', 'b_volt', 'a_sink_curr', 'b_sink_curr',
                                 'a_src_curr', 'b_src_curr', 'a_rem_volt', 'b_rem_volt',
                                 'max_set_volt', 'min_set_volt', 'max_set_vgap', 'min_set_vgap',
                                 'a_set_rint', 'b_set_rint'], calibration item.
            cal_value:  int/float, calibration value.
            cal_index:  int, (>=0), default 0, the index in the cal_item to write data.

        Returns:
            string, "done", api execution successful.

        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            CALIBRATION_COE_MAP = StormDef.CALIBRATION_COE_MAP_2
        else:
            CALIBRATION_COE_MAP = StormDef.CALIBRATION_COE_MAP_1

        assert cal_item in CALIBRATION_COE_MAP
        assert isinstance(cal_value, (int, float))

        s = struct.Struct("f")
        pack_data = s.pack(float(cal_value))
        s = struct.Struct("4B")
        data = s.unpack(pack_data)
        address = CALIBRATION_COE_MAP[cal_item][cal_index]
        self.write_eeprom(address, data)
        return "done"

    def legacy_read_calibration_cell(self, cal_item, cal_index=0):
        '''
        MIXBoard calibration data read.

        Args:
            cal_item:   string, ['a_volt', 'b_volt', 'a_sink_curr', 'b_sink_curr',
                                 'a_src_curr', 'b_src_curr', 'a_rem_volt', 'b_rem_volt',
                                 'max_set_volt', 'min_set_volt', 'max_set_vgap', 'min_set_vgap',
                                 'a_set_rint', 'b_set_rint'], calibration item.
            cal_index:  int, (>=0), default 0, the index in the cal_item to write data.

        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            CALIBRATION_COE_MAP = StormDef.CALIBRATION_COE_MAP_2
        else:
            CALIBRATION_COE_MAP = StormDef.CALIBRATION_COE_MAP_1

        assert cal_item in CALIBRATION_COE_MAP

        address = CALIBRATION_COE_MAP[cal_item][cal_index]
        data = self.read_eeprom(address, StormDef.CAL_CELL_LEN)

        s = struct.Struct("4B")
        pack_data = s.pack(*data)

        s = struct.Struct("f")
        result = s.unpack(pack_data)[0]

        return result

    def legacy_erase_calibration_cell(self, cal_item, cal_index=0):
        '''
        MIXBoard calibration data erase.

        Args:
            cal_item:   string, ['a_volt', 'b_volt', 'a_sink_curr', 'b_sink_curr',
                                 'a_src_curr', 'b_src_curr', 'a_rem_volt', 'b_rem_volt',
                                 'max_set_volt', 'min_set_volt', 'max_set_vgap', 'min_set_vgap',
                                 'a_set_rint', 'b_set_rint'], calibration item.
            cal_index:  int, (>=0), default 0, the index in the cal_item to write data.

        Returns:
            string, "done", api execution successful.

        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            CALIBRATION_COE_MAP = StormDef.CALIBRATION_COE_MAP_2
        else:
            CALIBRATION_COE_MAP = StormDef.CALIBRATION_COE_MAP_1

        assert cal_item in CALIBRATION_COE_MAP

        data = [0xff for i in range(StormDef.CAL_CELL_LEN)]
        address = CALIBRATION_COE_MAP[cal_item][cal_index]
        self.write_eeprom(address, data)
        return "done"
