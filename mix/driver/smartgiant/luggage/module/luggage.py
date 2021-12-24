# -*- coding: utf-8 -*-
from __future__ import division
import math
import time
import struct
from mix.driver.core.ic.cat24cxx import CAT24C64
from mix.driver.core.ic.cat9555 import CAT9555
from mix.driver.core.ic.cat9555_emulator import CAT9555Emulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.smartgiant.common.bus.gpio_emulator import GPIOEmulator
from mix.driver.smartgiant.common.bus.i2c_bus_emulator import I2CBusEmulator
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg_emulator import MIXQSPISGEmulator
from mix.driver.smartgiant.common.ic.max6642 import MAX6642
from mix.driver.smartgiant.common.ic.max6642_emulator import MAX6642Emulator
from mix.driver.smartgiant.common.ic.eeprom_emulator import EepromEmulator


__author__ = 'xuboyan@SmartGiant'
__version__ = '0.4'


class LuggageDef:

    CAT9555_ADDR = 0x22
    EEPROM_DEV_ADDR = 0x52
    SENSOR_DEV_ADDR = 0x48

    # Calibration Coefficients Map
    # float-format(16_byte)
    CAL_DATA_LEN = 16
    WRITE_CAL_DATA_PACK_FORMAT = "f4Bf4B"
    WRITE_CAL_DATA_UNPACK_FORMAT = "16B"

    READ_CAL_BYTE = 16
    READ_CAL_DATA_PACK_FORMAT = "16B"
    READ_CAL_DATA_UNPACK_FORMAT = "f4Bf4B"

    CALIBRATION_COE_MAP = {
        "read_volt": [0x0500],
        "read_curr": [0x0510, 0x0520],
        "set_CV": [0x0600],
        "set_CC": [0x0610],
        "set_CR": [0x0620, 0x0630, 0x0640, 0x0650]
    }

    CRoffset_MAP = 0x0660
    CRoffset_READ_CAL_BYTE = 3

    IO_INIT_DIR = [0x06, 0x06]
    IO_INIT_STATE = [0x00, 0x00]

    TEMP_LOCAL_HIGH_LIMIT = 110
    TEMP_REMOTE_HIGH_LIMIT = 110

    SPI_CLOCK_SPEED = 100000  # 100KHz
    SPI_BUS_MODE = "MODE1"

    PLI2CBUS_EMULATOR_REG_SIZE = 256
    MIXQSPISG_EMULATOR_REG_SIZE = 256

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


class Luggage(MIXBoard):
    '''
    Luggage module supports three modes: constant current, constant voltage, constant resistance.

    compatible = ["GQQ-UEL001003-000"]

    Luggage is supplied from single external voltage (12Vdc), can be used as stand alone module controlled by
    single USB connection from mac (I2C+SPI over USB), or by direct I2C + SPI interface from Xavier controller.
    Luggage can be ordered in different BOM options, supporting functionality limited to the exact needs for
    cost saving, and for different maximum dissipated power options (this includes different sizes of
    the attached heat sink and cooling fans).

    Args:
        i2c:                instance(I2C)/None,         Which is used to control cat9555, max6642, ads1119, LTC2606
                                                        and cat24c64. If not given, emulator will be created.
        spi:                instance(MIXQSPISG)/None,   If not given, MIXQSPISG emulator will be created.
        gpio_switch:        instance(GPIO),             This can be Pin or xilinx gpio, used to switch control mode.

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-UEL001003-000"]

    rpc_public_api = ['module_init', 'init_to', 'set_CC', 'set_CV', 'set_CR',
                      'read_curr', 'read_volt', 'read_local_temperature', 'read_remote_temperature',
                      'write_CRoffset', 'read_CRoffset', 'usb_connect_set',
                      'write_calibration', 'read_calibration', 'erase_calibration'] + MIXBoard.rpc_public_api

    def __init__(self, i2c, spi, gpio_switch=None):

        if i2c:
            self.i2c = i2c
            self.cat9555 = CAT9555(LuggageDef.CAT9555_ADDR, i2c)
            self.eeprom = CAT24C64(LuggageDef.EEPROM_DEV_ADDR, i2c)
            self.sensor = MAX6642(LuggageDef.SENSOR_DEV_ADDR, i2c)
        else:
            self.i2c = I2CBusEmulator("i2c_emulator", LuggageDef.PLI2CBUS_EMULATOR_REG_SIZE)
            self.cat9555 = CAT9555Emulator(LuggageDef.CAT9555_ADDR, None, None)
            self.eeprom = EepromEmulator("eeprom_emulator")
            self.sensor = MAX6642Emulator("max6642_emulator")

        if spi:
            self.spi = spi
        else:
            self.spi = MIXQSPISGEmulator("mix_qspi_sg_emulator", LuggageDef.MIXQSPISG_EMULATOR_REG_SIZE)

        if gpio_switch:
            self.gpio_switch = gpio_switch
        else:
            self.gpio_switch = GPIOEmulator("gpio_switch_emulator")
        super(Luggage, self).__init__(self.eeprom, None)

    def module_init(self):
        '''
        UEL00103 module init.

        This function will set SPI config and make MAX6642 chip initial.

        Returns:
            string, "done", api execution successful.

        Examples:
            luggage.module_init()
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

        return "done"

    def _current_read(self):
        '''
        Do one time sample from adc, return the measurement result.

        Returns:
            dict, {'raw_data': raw_data, 'current': current}, raw data and current value.

        Examples:
            result = luggage._current_read()
            print(result)

        '''
        self.i2c.write(0x40, [0x40, 0x23])
        time.sleep(0.05)
        self.i2c.write(0x40, [0x08])
        self.i2c.write(0x40, [0x10])
        result = self.i2c.read(0x40, 2)
        cdw = ("%02x" % result[0]) + ("%02x" % result[1])
        cdw = int("0x" + cdw, 16)

        if cdw < 0x2000:
            level = 1
            self.i2c.write(0x40, [0x40, 0x33])
            time.sleep(0.05)
            self.i2c.write(0x40, [0x08])
            self.i2c.write(0x40, [0x10])
            result = self.i2c.read(0x40, 2)
            cdw = ("%02x" % result[0]) + ("%02x" % result[1])
            cdw = int("0x" + cdw, 16)
            raw_data = cdw
            if cdw > 0x7FFF:
                cdw -= pow(2, 16)
            cdw = cdw / 4
        else:
            level = 2
            raw_data = cdw
            if cdw > 0x7FFF:
                cdw -= pow(2, 16)

        current = 4096 * cdw / 32768
        current = self.calibrate("read_curr", level, current)
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
        param = self.calibrate("set_CC", 1, param)
        amps_to_send = int(1048576 + param * 256)
        byte1 = (amps_to_send >> 16) & 255
        byte2 = (amps_to_send >> 8) & 255
        byte3 = amps_to_send & 255
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
        self.i2c.write(0x40, [0x40, 0x03])
        self.i2c.write(0x40, [0x08])
        self.i2c.write(0x40, [0x10])
        result = self.i2c.read(0x40, 2)
        cdw = ("%02x" % result[0]) + ("%02x" % result[1])
        cdw = int("0x" + cdw, 16)
        raw_data = cdw

        voltage = 8 * 4096 * (1 - cdw / 32768)
        voltage = self.calibrate("read_volt", 1, voltage)

        return {'raw_data': raw_data, 'voltage': voltage}

    def read_volt(self):
        '''
        Do one time sample from adc, return the measurement result.

        Returns:
            dict, {'raw_data': raw_data, 'voltage': voltage}, raw data and voltage value with unit.

        Examples:
            result = luggage.read_volt()
            print(result)

        '''
        # the first one discarded
        self._voltage_read()
        time.sleep(0.05)
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
        # the first one discarded
        self._current_read()
        time.sleep(0.05)
        curr_dict = self._current_read()
        raw_data = curr_dict['raw_data']
        current = [curr_dict['current'], 'mA']
        return {'raw_data': raw_data, 'current': current}

    def init_to(self, channel):
        '''
        Switch to one of (cc,cv,cr,cr_c) channels.

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
            result = self.read_eeprom(LuggageDef.CRoffset_MAP, LuggageDef.CRoffset_READ_CAL_BYTE)
            bytesStr = ("%02x" % result[0]) + ("%02x" % result[1]) + ("%02x" % result[2])
            if bytesStr == "ffffff":
                CR_offset = 0x17ffff
            else:
                CR_offset = int(bytesStr, 16)
            byte1 = (CR_offset >> 16)
            byte2 = (CR_offset >> 8) & 255
            byte3 = CR_offset & 255
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

        param = float(value)
        self.cat9555.set_ports([0xf1, 0x81])
        param = self.calibrate("set_CV", 1, param)
        volt_to_send = int(1048576 + 4 * 262144 * (1 - param / 32768))
        byte1 = (volt_to_send >> 16) & 255
        byte2 = (volt_to_send >> 8) & 255
        byte3 = volt_to_send & 255
        self.spi.write([byte1, byte2, byte3])

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

        param = float(value)
        self.cat9555.set_ports([0x01, 0x79])

        if param >= 2048:
            raise LuggageException("resistance over the range of 2048ohm max")
        elif param >= 512:
            param = self.calibrate("set_CR", 4, param)
            if param >= 2048:
                raise LuggageException("resistance over the range (2048ohm max after cal correction)")

            cdw_r = int(32 * param)
            byte1 = (cdw_r >> 8) & 255
            byte2 = cdw_r & 255
            self.i2c.write(0x30, [48, byte1, byte2])
            self.cat9555.set_ports([0x01, 0x39])
        elif param >= 128:
            param = self.calibrate("set_CR", 3, param)
            cdw_r = int(128 * param)
            byte1 = (cdw_r >> 8) & 255
            byte2 = cdw_r & 255
            self.i2c.write(0x30, [48, byte1, byte2])
            self.cat9555.set_ports([0x11, 0x31])
        elif param >= 32:
            param = self.calibrate("set_CR", 2, param)
            cdw_r = int(512 * param)
            byte1 = (cdw_r >> 8) & 255
            byte2 = cdw_r & 255
            self.i2c.write(0x30, [48, byte1, byte2])
            self.cat9555.set_ports([0x31, 0x29])
        else:
            param = self.calibrate("set_CR", 1, param)
            cdw_r = int(2048 * param)
            byte1 = (cdw_r >> 8) & 255
            byte2 = cdw_r & 255
            self.i2c.write(0x30, [48, byte1, byte2])
            self.cat9555.set_ports([0x71, 0x21])

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

        self.write_eeprom(LuggageDef.CRoffset_MAP, list(data[1:]))
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
        data = self.read_eeprom(LuggageDef.CRoffset_MAP, LuggageDef.CRoffset_READ_CAL_BYTE)
        data = [0] + data

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

    def write_calibration(self, cal_item, level, gain, offset):
        '''
        MIXBoard calibration data write.

        Args:
            cal_item:       string, ["read_volt", "read_curr", "set_CV", "set_CC", "set_CR"], calibration item.
            level:          int, calibration level index.
            gain:           float, gain value.
            offset:         float, offset value.

        Returns:
            string, "done", api execution successful.

        '''
        assert cal_item in LuggageDef.CALIBRATION_COE_MAP
        assert isinstance(level, int)
        assert 1 <= level <= len(LuggageDef.CALIBRATION_COE_MAP[cal_item])
        assert isinstance(gain, (int, float))
        assert isinstance(offset, (int, float))

        gain = float(gain) - 1
        offset = float(offset)
        if cal_item == "set_CV" or cal_item == "read_volt":
            offset /= 1000.0

        data = (gain, 0xff, 0xff, 0xff, 0xff, offset, 0xff, 0xff, 0xff, 0xff)
        s = struct.Struct(LuggageDef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(LuggageDef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = LuggageDef.CALIBRATION_COE_MAP[cal_item][level - 1]
        self.write_eeprom(address, data)
        return "done"

    def read_calibration(self, cal_item, level):
        '''
        MIXBoard calibration data read.

        Args:
            cal_item:       string, ["read_volt", "read_curr", "set_CV", "set_CC", "set_CR"], calibration item.
            level:          int, calibration level index.

        '''
        assert cal_item in LuggageDef.CALIBRATION_COE_MAP
        assert isinstance(level, int)
        assert 1 <= level <= len(LuggageDef.CALIBRATION_COE_MAP[cal_item])

        address = LuggageDef.CALIBRATION_COE_MAP[cal_item][level - 1]
        data = self.read_eeprom(address, LuggageDef.READ_CAL_BYTE)

        s = struct.Struct(LuggageDef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(LuggageDef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        gain = result[0]
        offset = result[5]
        if math.isnan(gain):
            gain = 1
        else:
            gain += 1
        if math.isnan(offset):
            offset = 0
        else:
            offset = offset

        if cal_item == "set_CV" or cal_item == "read_volt":
            offset *= 1000

        return {"gain": gain, "offset": offset}

    def erase_calibration(self, cal_item, level):
        '''
        MIXBoard calibration data erase.

        Args:
            cal_item:       string, ["read_volt", "read_curr", "set_CV", "set_CC", "set_CR"], calibration item.
            level:          int, calibration level index.

        Returns:
            string, "done", api execution successful.

        '''
        assert cal_item in LuggageDef.CALIBRATION_COE_MAP
        assert isinstance(level, int)
        assert 1 <= level <= len(LuggageDef.CALIBRATION_COE_MAP[cal_item])

        data = [0xff for i in range(LuggageDef.CAL_DATA_LEN)]
        address = LuggageDef.CALIBRATION_COE_MAP[cal_item][level - 1]
        self.write_eeprom(address, data)
        return "done"

    def calibrate(self, cal_item, level, data):
        '''
        This function is used to calibrate data.

        Args:
            cal_item:       string, ["read_volt", "read_curr", "set_CV", "set_CC", "set_CR"], calibration item.
            level:          int, calibration level index.
            data:           float, raw data which need to be calibrated.

        Returns:
            float, calibrated data.

        '''
        if not self.is_use_cal_data():
            return data
        assert isinstance(cal_item, basestring)
        assert isinstance(level, int)
        assert 1 <= level <= len(LuggageDef.CALIBRATION_COE_MAP[cal_item])
        assert isinstance(data, (int, float))

        result = self.read_calibration(cal_item, level)
        gain = result["gain"]
        offset = result["offset"]

        return data * gain + offset
