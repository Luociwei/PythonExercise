# -*- coding: utf-8 -*-
from __future__ import division
import math
import time
import struct
from mix.driver.core.ic.cat24cxx import CAT24C64
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.smartgiant.common.ic.max6642 import MAX6642
from mix.driver.smartgiant.common.ic.ads1119 import ADS1119
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver


__author__ = 'xuboyan@SmartGiant, tufengmao@SmartGiant'
__version__ = 'V0.0.1'


luggage_range_table = {
    "read_volt": 0,
    "read_curr": 1,
    "set_CV": 2,
    "set_CC": 3,
    "set_CR": 4,
    "CRoffset": 5
}


class LuggageDef:

    TIMEOUT = 3  # s

    LATEST_CAL = -1
    # Calibration Coefficients Map
    # float-format(16_byte)
    CAL_CELL_LEN = 16
    POS_CAL_DATA_LEN = 12
    WRITE_CAL_DATA_PACK_FORMAT = "f4Bf4B"
    WRITE_CAL_DATA_UNPACK_FORMAT = "16B"

    READ_CAL_BYTE = 16
    READ_CAL_DATA_PACK_FORMAT = "16B"
    READ_CAL_DATA_UNPACK_FORMAT = "f4Bf4B"

    CRoffset_READ_CAL_BYTE = 3

    CRoffset = "CRoffset"
    CALIBRATION_COE_MAP = {
        "read_volt": [0x0500],
        "read_curr": [0x0510, 0x0520],
        "set_CV": [0x0600],
        "set_CC": [0x0610],
        "set_CR": [0x0620, 0x0630, 0x0640, 0x0650],
        "CRoffset": [0x0660]
    }

    # CAT24C64
    EEPROM_DEV_ADDR = 0x52

    # CAT9555
    CAT9555_ADDR = 0x22
    IO_INIT_DIR = [0x06, 0x06]
    IO_INIT_STATE = [0x00, 0x01]

    # MAX6642
    SENSOR_DEV_ADDR = 0x48
    TEMP_LOCAL_HIGH_LIMIT = 110
    TEMP_REMOTE_HIGH_LIMIT = 110

    # ADS1119
    ADS1119_DEV_ADDR = 0x40
    ADS1119_REF_MODE = "EXTERNAL"
    ADS1119_MVREF = 4096.0  # mV
    ADS1119_SAMPLE_RATE = 20  # Hz
    READ_CURR_CHANNEL = 1
    READ_VOLT_CHANNEL = 0
    ADS1119_SUPPLEMENTARY_FORMULA = {
        "restore_raw_data": lambda value: int(value * pow(2, 15) / LuggageDef.ADS1119_MVREF),
        "read_volt": lambda value: 8 * (LuggageDef.ADS1119_MVREF - value)
    }

    # MAX5318
    SPI_CLOCK_SPEED = 100000  # 100KHz
    SPI_BUS_MODE = "MODE1"
    MIX_QSPI_REG_SIZE = 256

    FUNCTION_RANGE = {
        "init_to": ["cc", "cv", "cr", "cr_c"],
        "set_CC": lambda value: 0 <= value <= 4000,
        "set_CV": lambda value: 100 <= value <= 32000,
        "set_CR": lambda value: 0.005 <= value <= 2048
    }


class LuggageException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class Luggage(SGModuleDriver):
    '''
    Luggage module supports three modes: constant current, constant voltage, constant resistance.

    compatible = ["GQQ-MJ2C-5-030", "GQQ-MJ2C-5-03B", "GQQ-MJ2C-5-03C"]

    Luggage is supplied from single external voltage (12Vdc), can be used as stand alone module controlled by
    single USB connection from mac (I2C+SPI over USB), or by direct I2C + SPI interface from Xavier controller.
    Luggage can be ordered in different BOM options, supporting functionality limited to the exact needs for
    cost saving, and for different maximum dissipated power options (this includes different sizes of
    the attached heat sink and cooling fans).

    Args:
        i2c:                instance(I2C),         Which is used to control cat9555, max6642, ads1119, LTC2606
                                                        and cat24c64.
        spi:                instance(MIXQSPISG),   class of MIXQSPISG.
        gpio_switch:        instance(GPIO)/None,   This can be Pin or xilinx gpio, used to switch control mode.

    Examples:
        i2c_bus = I2C('/dev/i2c-1')
        spi_bus = '/dev/MIX_QSPI_0'
        luggage = Luggage(i2c_bus, spi_bus)
        luggage.reset()
        cc mode, 500 mA:
            luggage.init_to("cc")
            luggage.set_CC(500)
        cv mode, 6000 mV:
            luggage.init_to("cv")
            luggage.set_CV(6000)
        cr mode, 500 ohm:
            luggage.init_to("cr")
            luggage.set_CR(500)
        PS:
            Before switching from one channel to another, you need to call the init_to interface again to
            avoid failure of subsequent operations. For example, after outputting 500mA, you need to call
            luggage.init_to("cc") again, and then switch the channel to cv mode.

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-MJ2C-5-030", "GQQ-MJ2C-5-03B", "GQQ-MJ2C-5-03C"]

    rpc_public_api = ['init_to', 'set_CC', 'set_CV', 'set_CR',
                      'read_curr', 'read_volt', 'read_local_temperature', 'read_remote_temperature',
                      'usb_connect_set'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, spi, gpio_switch=None):
        self.i2c = i2c
        if isinstance(spi, basestring):
            axi4_bus = AXI4LiteBus(spi, LuggageDef.MIX_QSPI_REG_SIZE)
            self.spi = MIXQSPISG(axi4_bus)
        else:
            self.spi = spi
        self.gpio_switch = gpio_switch
        self.cat9555 = CAT9555(LuggageDef.CAT9555_ADDR, i2c)
        self.eeprom = CAT24C64(LuggageDef.EEPROM_DEV_ADDR, i2c)
        self.sensor = MAX6642(LuggageDef.SENSOR_DEV_ADDR, i2c)
        self.ads1119 = ADS1119(LuggageDef.ADS1119_DEV_ADDR, self.i2c, LuggageDef.ADS1119_REF_MODE,
                               LuggageDef.ADS1119_MVREF, LuggageDef.ADS1119_SAMPLE_RATE)
        super(Luggage, self).__init__(eeprom=self.eeprom, range_table=luggage_range_table)

    def post_power_on_init(self, timeout=LuggageDef.TIMEOUT):
        '''
        Init module to a know harware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)
        self.load_calibration()

    def reset(self, timeout=LuggageDef.TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        This function will set SPI config and make CAT9555, MAX6642 and ADS1119 chip initial.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                # CAT9555 config
                self.cat9555.set_pins_dir(LuggageDef.IO_INIT_DIR)
                self.cat9555.set_ports(LuggageDef.IO_INIT_STATE)

                # SPI config
                self.spi.open()
                self.spi.set_speed(LuggageDef.SPI_CLOCK_SPEED)
                self.spi.set_mode(LuggageDef.SPI_BUS_MODE)

                # MAX6642 chip initial
                self.sensor.write_high_limit("local", LuggageDef.TEMP_LOCAL_HIGH_LIMIT)
                self.sensor.write_high_limit("remote", LuggageDef.TEMP_REMOTE_HIGH_LIMIT)

                # ADS1119 chip init
                self._adc_init()

                return "done"

            except Exception as e:
                if time.time() - start_time > timeout:
                    raise LuggageException("Timeout: {}".format(e.message))

    def _adc_init(self):
        '''
        ADC initializes to the specified state.
        '''
        self.ads1119.init()
        self.ads1119.enable_continuous_sampling()

    def get_driver_version(self):
        '''
        Get driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def _current_read(self):
        '''
        Do one time sample from adc, return the measurement result.

        Returns:
            dict, {'raw_data': raw_data, 'current': current}, raw data and current value.

        Examples:
            result = luggage._current_read()
            print(result)

        '''
        # ADS1119 chip init
        self._adc_init()

        self.ads1119.set_gain(1)
        result = self.ads1119.read_volt(LuggageDef.READ_CURR_CHANNEL)
        raw_data = LuggageDef.ADS1119_SUPPLEMENTARY_FORMULA["restore_raw_data"](result)

        if raw_data < 0x2000:
            level = 0
            self.ads1119.set_gain(4)
            result = self.ads1119.read_volt(LuggageDef.READ_CURR_CHANNEL)
            raw_data = LuggageDef.ADS1119_SUPPLEMENTARY_FORMULA["restore_raw_data"](result)
        else:
            level = 1

        current = self.calibrate("read_curr", result, level)
        if current < 0:
            current = 0

        return {'raw_data': raw_data, 'current': current}

    def _current_set(self, value):
        '''
        Luggage set the output current.

        Args:
            value:          float, [0~5000], unit mA

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage._current_set(500)

        '''
        assert isinstance(value, (int, float))

        param = float(value)
        self.cat9555.set_ports([0xf1, 0x01])
        param = self.calibrate("set_CC", param, 0)
        amps_to_send = int(1048576 + param * 256)
        byte1 = (amps_to_send >> 16) & 0xFF
        byte2 = (amps_to_send >> 8) & 0xFF
        byte3 = amps_to_send & 0xFF
        self.spi.write([byte1, byte2, byte3])

        return "done"

    def _voltage_read(self):
        '''
        Do one time sample from adc, return the measurement result.

        Returns:
            dict, {'raw_data': raw_data, 'voltage': voltage}, raw data and voltage value.

        Examples:
            result = luggage._voltage_read()
            print(result)

        '''
        # ADS1119 chip init
        self._adc_init()

        self.ads1119.set_gain(1)
        result = self.ads1119.read_volt(LuggageDef.READ_VOLT_CHANNEL)
        raw_data = LuggageDef.ADS1119_SUPPLEMENTARY_FORMULA["restore_raw_data"](result)

        voltage = LuggageDef.ADS1119_SUPPLEMENTARY_FORMULA["read_volt"](result)
        voltage = self.calibrate("read_volt", voltage, 0)

        return {'raw_data': raw_data, 'voltage': voltage}

    def _voltage_set(self, value):
        '''
        Luggage set the output voltage.

        Args:
            value:          float, [100~32000], unit mV

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage._voltage_set(6000)

        '''
        assert isinstance(value, (int, float))

        param = float(value)
        self.cat9555.set_ports([0xf1, 0x81])
        param = self.calibrate("set_CV", param, 0)
        volt_to_send = int(1048576 + 4 * 262144 * (1 - param / 32768))
        byte1 = (volt_to_send >> 16) & 0xFF
        byte2 = (volt_to_send >> 8) & 0xFF
        byte3 = volt_to_send & 0xFF
        self.spi.write([byte1, byte2, byte3])

        return "done"

    def _resistance_set(self, value):
        '''
        Luggage set the output resistance.

        Args:
            value:          float, [0.005~2048], unit ohm

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage._resistance_set(500)

        '''
        assert isinstance(value, (int, float))

        param = float(value)
        self.cat9555.set_ports([0x01, 0x79])

        if param >= 2048:
            raise LuggageException("resistance over the range of 2048ohm max")
        elif param >= 512:
            param = self.calibrate("set_CR", param, 3)
            if param >= 2048:
                raise LuggageException("resistance over the range (2048ohm max after cal correction)")

            cdw_r = int(32 * param)
            byte1 = (cdw_r >> 8) & 0xFF
            byte2 = cdw_r & 0xFF
            self.i2c.write(0x30, [48, byte1, byte2])
            self.cat9555.set_ports([0x01, 0x39])
        elif param >= 128:
            param = self.calibrate("set_CR", param, 2)
            cdw_r = int(128 * param)
            byte1 = (cdw_r >> 8) & 0xFF
            byte2 = cdw_r & 0xFF
            self.i2c.write(0x30, [48, byte1, byte2])
            self.cat9555.set_ports([0x11, 0x31])
        elif param >= 32:
            param = self.calibrate("set_CR", param, 1)
            cdw_r = int(512 * param)
            byte1 = (cdw_r >> 8) & 0xFF
            byte2 = cdw_r & 0xFF
            self.i2c.write(0x30, [48, byte1, byte2])
            self.cat9555.set_ports([0x31, 0x29])
        else:
            param = self.calibrate("set_CR", param, 0)
            cdw_r = int(2048 * param)
            byte1 = (cdw_r >> 8) & 0xFF
            byte2 = cdw_r & 0xFF
            self.i2c.write(0x30, [48, byte1, byte2])
            self.cat9555.set_ports([0x71, 0x21])

        return "done"

    def read_volt(self):
        '''
        Do one time sample from adc, return the measurement result.

        Returns:
            dict, {'raw_data': raw_data, 'voltage': voltage}, raw data and voltage value with unit.

        Examples:
            result = luggage.read_volt()
            print(result)

        '''
        volt_dict = self._voltage_read()
        raw_data = volt_dict['raw_data']
        voltage = [volt_dict['voltage'], 'mV']

        return {'raw_data': raw_data, 'voltage': voltage}

    def read_curr(self):
        '''
        Do one time sample from adc, return the measurement result.

        Returns:
            dict, {'raw_data': raw_data, 'current': current}, raw data and current value with unit.

        Examples:
            result = luggage.read_curr()
            print(result)

        '''
        curr_dict = self._current_read()
        raw_data = curr_dict['raw_data']
        current = [curr_dict['current'], 'mA']
        return {'raw_data': raw_data, 'current': current}

    def init_to(self, channel):
        '''
        Switch to one of (cc,cv,cr,cr_c) channels.
        If channel is cc or cv, the ADC (ADS1119) and DAC (MAX5318) will also be reset.

        Args:
            channel:        string, ["cc", "cv", "cr", "cr_c"], the channel to init.

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage.init_to("cc")

        '''
        assert channel in LuggageDef.FUNCTION_RANGE["init_to"]

        if channel == "cc":
            self.cat9555.set_ports([0xf1, 0x41])
            self.cat9555.set_ports([0xf0, 0x40])
            self.cat9555.set_ports([0xf1, 0x41])
        elif channel == "cv":
            self.cat9555.set_ports([0xf1, 0xc1])
            self.cat9555.set_ports([0xf0, 0xc0])
            self.cat9555.set_ports([0xf1, 0xc1])
        elif channel == "cr":
            self.i2c.write(0x30, [0x30, 0xff, 0xff])
            self.cat9555.set_ports([0x01, 0x79])
        else:
            if not self.is_use_cal_data():
                result = self.read_nvmem(LuggageDef.CALIBRATION_COE_MAP[LuggageDef.CRoffset][0],
                                         LuggageDef.CRoffset_READ_CAL_BYTE)
                bytesStr = ("%02x" % result[0]) + ("%02x" % result[1]) + ("%02x" % result[2])
                if bytesStr == "ffffff":
                    CR_offset = 0x17ffff
                else:
                    CR_offset = int(bytesStr, 16)
            else:
                CR_offset = self._calibration_table[LuggageDef.CRoffset][0]["offset_raw_code"]
            byte1 = (CR_offset >> 16)
            byte2 = (CR_offset >> 8) & 0xFF
            byte3 = CR_offset & 0xFF
            self.i2c.write(0x30, [0x30, 0xff, 0xff])
            self.cat9555.set_ports([0x01, 0x79])
            self.spi.write([byte1, byte2, byte3])

        return "done"

    def set_CV(self, value):
        '''
        Luggage set the output voltage.

        Args:
            value:          float, [100~32000], unit mV

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage.set_CV(6000)

        '''
        assert isinstance(value, (int, float))
        assert LuggageDef.FUNCTION_RANGE["set_CV"](value)

        self._voltage_set(value)
        return "done"

    def set_CC(self, value):
        '''
        Luggage set the output current.

        Args:
            value:          float, [0~4000], unit mA

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage.set_CC(500)

        '''
        assert isinstance(value, (int, float))
        assert LuggageDef.FUNCTION_RANGE["set_CC"](value)

        self._current_set(value)
        return "done"

    def set_CR(self, value):
        '''
        Luggage set the output resistance.

        Args:
            value:          float, [0.005~2048], unit ohm

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage.set_CR(500)

        '''
        assert isinstance(value, (int, float))
        assert LuggageDef.FUNCTION_RANGE["set_CR"](value)

        self._resistance_set(value)
        return "done"

    def read_local_temperature(self):
        '''
        Luggage read the local temperature.

        The MAX6642 temperature sensor with I2C interface.

        Returns:
            list, [value, unit], unit C

        Examples:
            result = luggage.read_local_temperature()
            print(result)

        '''
        val = self.sensor.get_temperature('local', extended=True)
        return [val, "C"]

    def read_remote_temperature(self):
        '''
        Luggage read the remote temperature.

        The MAX6642 temperature sensor with I2C interface.

        Returns:
            list, [value, unit], unit C

        Examples:
            result = luggage.read_remote_temperature()
            print(result)

        '''
        val = self.sensor.get_temperature('remote', extended=True)
        return [val, "C"]

    def write_CRoffset(self, offset):
        '''
        Set constant resistance output offset.

        Args:
            offset:         float, constant resistance output offset.

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage.write_CRoffset(500.0)

        '''
        assert isinstance(offset, (int, float))

        offset = float(offset)
        intToWrite = int(1048576 + offset * 256 + 0.5)

        s = struct.Struct(">i")
        pack_data = s.pack(intToWrite)

        s = struct.Struct("4B")
        data = s.unpack(pack_data)

        self.write_nvmem(LuggageDef.CALIBRATION_COE_MAP[LuggageDef.CRoffset][0], list(data[1:]))
        return "done"

    def read_CRoffset(self):
        '''
        Read constant resistance output offset.

        Returns:
            float, constant resistance output offset.

        Examples:
            result = luggage.read_CRoffset()
            print(result)

        '''
        data = self.read_nvmem(LuggageDef.CALIBRATION_COE_MAP[LuggageDef.CRoffset][0],
                               LuggageDef.CRoffset_READ_CAL_BYTE)
        data = [0] + list(data)

        s = struct.Struct("4B")
        pack_data = s.pack(*data)

        s = struct.Struct(">i")
        result = s.unpack(pack_data)[0]
        ret = (result - 1048576) / 256.0
        return ret

    def usb_connect_set(self, status):
        '''
        USB connect to dut enable or disable

        Args:
            status:         string, ["enable", "disable"].

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage.usb_connect_set("enable")

        '''
        assert status in ["enable", "disable"]
        if status == "enable":
            level = 1
        else:
            level = 0
        self.gpio_switch.set_level(level)

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
        assert range_name != LuggageDef.CRoffset, "Please use write_CRoffset interface."
        assert index >= 0

        gain = float(gain) - 1
        if range_name == 'set_CV' or range_name == 'read_volt':
            offset /= 1000.0

        s = struct.Struct(LuggageDef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(gain, 0xFF, 0xFF, 0xFF, 0xFF, offset, 0xFF, 0xFF, 0xFF, 0xFF)
        s = struct.Struct(LuggageDef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        addr = LuggageDef.CALIBRATION_COE_MAP[range_name][index]
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
            dict:           {"gain": value, "offset": value, "threshold": value, "is_use": value}
        '''
        assert cal_index >= 0
        assert range_name in self._range_table
        assert range_name != LuggageDef.CRoffset, "Please use read_CRoffset interface."
        assert index >= 0

        addr = LuggageDef.CALIBRATION_COE_MAP[range_name][index]
        data = self.read_nvmem(addr, LuggageDef.CAL_CELL_LEN)

        s = struct.Struct(LuggageDef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(LuggageDef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        gain = result[0]
        offset = result[5]
        if math.isnan(gain):
            gain = 1.0
        else:
            gain += 1.0
        if math.isnan(offset):
            offset = 0.0
        else:
            offset = offset

        if range_name == "set_CV" or range_name == "read_volt":
            offset *= 1000.0

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
        assert isinstance(level, int)
        assert isinstance(data, (int, float))

        items = self._calibration_table[range_name]
        if len(items) == 0:
            return data

        return items[level]['gain'] * data + items[level]['offset']

    def load_calibration(self, calibration_cell_index=LuggageDef.LATEST_CAL):
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

        if calibration_cell_index == LuggageDef.LATEST_CAL:
            try:
                cal_index = self.read_latest_calibration_index()
            except Exception as e:
                self._cal_common_error = LuggageException(str(e))
                return "done"
        else:
            cal_index = calibration_cell_index

        try:
            read_data = self.read_calibration_cell(cal_index)
        except Exception as e:
            self._cal_common_error = LuggageException("Read calibration cell error: " + str(e))
            return "done"

        self.cal_index = cal_index

        data_size = self._get_cal_size(cal_index)
        start_address = self._get_cal_address(cal_index)

        for range_name, index in self._range_table.items():
            self._calibration_table[range_name] = []
            cal_item_addr = LuggageDef.CALIBRATION_COE_MAP[range_name][0]
            cal_pos = cal_item_addr - start_address
            # Special treatment for croffset.
            if range_name == LuggageDef.CRoffset:
                # Compatible with 2.8.4 calibration previously shipped but not using croffset.
                if cal_pos >= data_size:
                    continue
                # check cal_pos range
                if cal_pos < 0:
                    err_info = LuggageException("Range {} count pos 0x{:x} is invalid".format(range_name, cal_pos))
                    self._range_err_table[range_name] = err_info
                    continue
                cal_len = LuggageDef.CRoffset_READ_CAL_BYTE
                cal_data = read_data[cal_pos:(cal_pos + cal_len)]

                bytesStr = ("%02x" % cal_data[0]) + ("%02x" % cal_data[1]) + ("%02x" % cal_data[2])
                if bytesStr == "ffffff":
                    CR_offset = 0x17ffff
                else:
                    CR_offset = int(bytesStr, 16)
                offset = (CR_offset - 1048576) / 256.0
                self._calibration_table[range_name].append({"offset_raw_code": CR_offset, "offset": offset})
                continue
            # check cal_pos range
            if cal_pos < 0 or cal_pos >= data_size:
                err_info = LuggageException("Range {} count pos 0x{:x} is invalid".format(range_name, cal_pos))
                self._range_err_table[range_name] = err_info
                continue
            count = len(LuggageDef.CALIBRATION_COE_MAP[range_name])
            cal_len = count * LuggageDef.CAL_CELL_LEN
            if range_name == 'set_CR':
                cal_len -= 4
            cal_data = read_data[cal_pos:(cal_pos + cal_len)]

            for i in range(count):
                item_pos = i * LuggageDef.CAL_CELL_LEN
                data = cal_data[item_pos:(item_pos + LuggageDef.POS_CAL_DATA_LEN)]

                s = struct.Struct('12B')
                pack_data = s.pack(*data)

                s = struct.Struct('f4Bf')
                result = s.unpack(pack_data)

                gain = result[0]
                offset = result[5]
                if math.isnan(gain):
                    gain = 1.0
                else:
                    gain += 1.0
                if math.isnan(offset):
                    offset = 0.0
                else:
                    offset = offset

                if range_name == 'set_CV' or range_name == 'read_volt':
                    offset *= 1000

                self._calibration_table[range_name].append({"gain": gain, "offset": offset})
        return "done"
