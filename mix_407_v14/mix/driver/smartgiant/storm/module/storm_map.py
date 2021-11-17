# -*- coding: utf-8 -*-
import struct
import time
import math
from mix.driver.core.ic.cat24cxx import CAT24C64
from mix.driver.core.ic.pca9554 import PCA9554
from mix.driver.smartgiant.common.ic.ads1112 import ADS1112
from mix.driver.smartgiant.common.ic.ads1119 import ADS1119
from mix.driver.smartgiant.common.ic.ad569x import AD5696
from mix.driver.smartgiant.common.ic.max6642 import MAX6642
from mix.driver.smartgiant.common.ic.mcp23008 import MCP23008
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.bus.ft4222 import FT4222
from mix.driver.smartgiant.common.bus.ft_gpio import FTGPIO
from mix.driver.smartgiant.common.bus.ft_spi import FTSPI


__author__ = 'weiping.mo@SmartGiant'
__version__ = 'V0.0.2'


class StormException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


storm_range_table = {
    'a_volt': 0,
    'b_volt': 1,
    'a_sink_curr': 2,
    'b_sink_curr': 3,
    'a_src_curr': 4,
    'b_src_curr': 5
}


class StormDef:
    # the definition can be found in Driver ERS
    EEPROM_DEV_ADDR = 0x52
    SPILL_SENSOR_DEV_ADDR = 0x48
    BACKPACK_SENSOR_DEV_ADDR = 0x49
    ADC_DEV_ADDR = 0x4A
    DAC_DEV_ADDR = 0x0D
    MCP23008_DEV_ADDR = 0x22

    # Calibration Coefficients Map
    # float-format(4_byte)
    CAL_DATA_LEN = 4
    CAL_DATA_PACK_FORMAT = "4B"
    CAL_DATA_UNPACK_FORMAT = "f"

    CALIBRATION_COE_MAP = {
        'a_volt': [0x0500, 0x0503],
        'b_volt': [0x0508, 0x050B],
        'a_sink_curr': [0x0510, 0x0513],
        'b_sink_curr': [0x0518, 0x051B],
        'a_src_curr': [0x0520, 0x0523],
        'b_src_curr': [0x0528, 0x052B],
    }

    # ADC channel and minimum anolog input
    ADC_VOLT_CHANNEL = 2  # AIN0-AIN3
    ADC_VOLT_RATIO = 7.8
    ADC_CURR_SINK_CHANNEL = 3  # AIN1-AIN3
    ADC_CURR_SINK_RATIO = 4.0
    ADC_CURR_SRC_CHANNEL = 1  # AIN2-AIN3
    ADC_CURR_SRC_RATIO = 4.0

    # AD5696 VREF is 2500 mV
    DAC_VREF = 2500  # mV
    DAC_CHANNEL = 0  # 'DAC_A'

    # LTC3892-2 VOUT max 12.8V, min 7.2V
    MAX_BUCK_OUT = 12800  # mV
    MIN_BUCK_OUT = 7200  # mV

    # AD7606: FT4222 USB-SPI interface, 5V range
    AD7606_RANGE = 5  # V
    CONVST_DELAY = 0.0001  # 100uS
    DEFAULT_TIMEOUT = 100
    # MCP23008 Pins
    PIN_ADC_RST = 1  # AD7606
    PIN_ADC_CONVST = 2  # AD7606
    PIN_ADC_BUSY = 3  # AD7606 input

    TIMEOUT = 1  # s
    LATEST_CAL = -1

    I2C_EXP_RST_INV = 2
    ADS1119_DEV_ADDR = 0x40
    PCA9554_DEV_ADDR = 0x22
    CONFIG_LIST = ["740", "030", "040"]
    ADS1119_REF_MODE = "EXTERNAL"
    ADS1119_MVREF = 4096.0  # mV
    ADS1119_SAMPLE_RATE = 1000
    AD5696_MVREF = 4096  # mV
    CONFIG_ADDR = 0x15


class StormBase(SGModuleDriver):
    '''
    Storm (Battery Emulator) is a bi-directional DC power supply.

    It can simulate the charging and discharging functions of battery
    with the maximum output power of 120W and the maximum sink current of 6A.

    Args:
        i2c:                 instance(I2C), Class instance of I2C, which is used to access
                                                 CAT24C64,MCP23008, ADS1112, AD5696, CAT9555, MAX6642.
        using_ft4222:       boolean,            enable ft4222 and init spi and gpio of ft4222.
        eeprom_devaddr:      int,                Eeprom device address.
        spill:              instance, Class instance of SPILL board.

    '''

    rpc_public_api = ['read_output_voltage', 'read_source_current', 'read_sink_current', 'get_local_temperature',
                      'get_remote_temperature', 'set_output_voltage', 'ft4222_enable_measure',
                      'ft4222_measure'] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c, using_ft4222=False, eeprom_devaddr=StormDef.EEPROM_DEV_ADDR, spill=None):

        self.eeprom = CAT24C64(eeprom_devaddr, i2c)
        self.using_ft4222 = using_ft4222
        self.i2c = i2c
        self._hardware_version = ''
        self.spill = spill
        super(StormBase, self).__init__(self.eeprom, None, range_table=storm_range_table)

    def post_power_on_init(self, timeout=StormDef.TIMEOUT):
        '''
        Init module to a know harware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        if self.using_ft4222:
            ft4222 = FT4222('0')
            self.ftspi = FTSPI(ft4222, ioline='SPI',
                               speed=64, mode='MODE3',
                               ssomap='SS0O')
            ft4222 = FT4222('1')
            self.ftgpio = FTGPIO(ft4222, 0)
        self._hardware_version = self.read_hardware_config()
        if self._hardware_version in StormDef.CONFIG_LIST:
            self.ad5696 = AD5696(StormDef.DAC_DEV_ADDR, self.i2c, StormDef.AD5696_MVREF)
            self.ads1119 = ADS1119(StormDef.ADS1119_DEV_ADDR, self.i2c, StormDef.ADS1119_REF_MODE,
                                   StormDef.ADS1119_MVREF, StormDef.ADS1119_SAMPLE_RATE)
            self.pca9554 = PCA9554(StormDef.PCA9554_DEV_ADDR, self.i2c)
            self.backpack_max6642 = MAX6642(StormDef.BACKPACK_SENSOR_DEV_ADDR, self.i2c)
        else:
            self.ad5696 = AD5696(StormDef.DAC_DEV_ADDR, self.i2c)
            self.ads1112 = ADS1112(StormDef.ADC_DEV_ADDR, self.i2c)
            self.mcp23008 = MCP23008(StormDef.MCP23008_DEV_ADDR, self.i2c)
            self.max6642 = MAX6642(StormDef.SPILL_SENSOR_DEV_ADDR, self.i2c)

        self.reset(timeout)

    def reset(self, timeout=StormDef.TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        This function will set AD5696 output 0 mV to make Storm output maximum voltage 12800 mV.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                self.ad5696.output_volt(StormDef.DAC_CHANNEL, 0)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise StormException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def read_hardware_config(self):
        '''
        returns a string that represents the config
        '''
        return "".join([chr(c) for c in self.read_nvmem(StormDef.CONFIG_ADDR, 3)])

    def read_output_voltage(self):
        '''
        Storm measure the output voltage via the ADS1112 ADC with I2C interface.

        Returns:
            list,   [value, 'mV'].

        Examples:
            storm.read_output_voltage()

        '''
        volt_val = self.ads1112.read_volt(StormDef.ADC_VOLT_CHANNEL)
        volt_val *= StormDef.ADC_VOLT_RATIO
        a_volt = self.calibrate('a_volt', volt_val, 0)
        volt_val = self.calibrate('b_volt', a_volt, 0)

        return [volt_val, 'mV']

    def read_source_current(self):
        '''
        Storm measure the source current via the ADS1112 ADC with I2C interface.

        Returns:
            list,   [value, 'mA'].

        Examples:
            storm.read_source_current()

        '''
        curr_val = self.ads1112.read_volt(StormDef.ADC_CURR_SRC_CHANNEL)
        curr_val *= StormDef.ADC_CURR_SRC_RATIO
        a_src_curr = self.calibrate('a_src_curr', curr_val, 0)
        curr_val = self.calibrate('b_src_curr', a_src_curr, 0)

        return [curr_val, 'mA']

    def read_sink_current(self):
        '''
        Storm measure the sink current via the ADS1112 ADC with I2C interface.

        Returns:
            list,   [value, 'mA'].

        Examples:
            storm.read_sink_current()
        '''
        curr_val = self.ads1112.read_volt(StormDef.ADC_CURR_SINK_CHANNEL)
        curr_val *= StormDef.ADC_CURR_SINK_RATIO
        a_sink_curr = self.calibrate('a_sink_curr', curr_val, 0)
        curr_val = self.calibrate('b_sink_curr', a_sink_curr, 0)

        return [curr_val, 'mA']

    def get_local_temperature(self):
        '''
        Storm get the local temperature.

        The MAX6642 temperature sensor with I2C interface.

        Returns:
            list,   [value, 'Celsius'].

        Examples:
            storm.get_local_temperature()
        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            raise StormException("No concerte implmenetation for get local temperature in this driver")
        else:
            val = self.max6642.get_temperature('local', extended=True)
        return [val, 'Celsius']

    def get_remote_temperature(self):
        '''
        Storm get the remote temperature.

        The MAX6642 temperature sensor with I2C interface.

        Returns:
            list,   [value, 'Celsius'].

        Examples:
            storm.get_remote_temperature()

        '''
        if self._hardware_version in StormDef.CONFIG_LIST:
            raise StormException("No concerte implmenetation for get remote temperature in this driver")
        else:
            val = self.max6642.get_temperature('remote', extended=True)
        return [val, 'Celsius']

    def _volt_to_dac(self, volt):
        '''
        Storm transform voltage to dac value.

        Args:
            volt:    int/float, unit mV.

        Examples:
            storm._volt_to_dac(12800)
        '''
        dac_ratio = float(StormDef.MAX_BUCK_OUT - StormDef.MIN_BUCK_OUT) / StormDef.DAC_VREF
        return float(StormDef.MAX_BUCK_OUT - volt) / dac_ratio

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

        volt_val = self._volt_to_dac(volt)
        self.ad5696.output_volt(StormDef.DAC_CHANNEL, volt_val)
        return "done"

    def ft4222_enable_measure(self):
        '''
        Storm Enable measure output voltage and output current.

        1) FT4222H GPIO2 (tied to MCP23008's RST pin) should output high.
            command: gpiow device port-number(0-3) value(0-1) [delay]
                     gpiow 0 2 1
                     Terminal shows 'locID = xxxx'
        2) Configure AD7606 pins:
            PIN_RST = 1  # AD7606
            PIN_CONVST = 2  # AD7606
            PIN_BUSY = 3  # AD7606 input

        Examples:
            storm.ft4222_enable_measure()

        Returns:
            string, "done", api execution successful.

        '''
        # enable MCP23008/PCA9554
        self.ftgpio.set_pin_dir(2, 'output')
        self.ftgpio.set_pin(StormDef.I2C_EXP_RST_INV, 1)

        # Configure AD7608 RST,CONVST,BUSY direction.
        if self._hardware_version in StormDef.CONFIG_LIST:
            self.pca9554.set_pin_dir(StormDef.PIN_ADC_BUSY, 'input')
            self.pca9554.set_pin_dir(StormDef.PIN_ADC_RST, 'output')
            self.pca9554.set_pin_dir(StormDef.PIN_ADC_CONVST, 'output')
        else:
            self.mcp23008.set_pin_dir(StormDef.PIN_ADC_BUSY, 'input')
            self.mcp23008.set_pin_dir(StormDef.PIN_ADC_RST, 'output')
            self.mcp23008.set_pin_dir(StormDef.PIN_ADC_CONVST, 'output')

        return "done"

    def ft4222_measure(self):
        '''
        Storm Measure output voltage and output current through USB interface to SPI bridge.

        Command: spimr device ioLine clockDiv clockPolarity clockPhase ssoMap number-of-bytes-to-read
                 spimr 0 1 64 1 1 1 8
                 Terminal shows: ['locID = xxxx\n', '2a63001d00273086\n']

        Returns:
            dict, {"voltage":[value, 'mV'], "sink_current":[value, 'mA'], "source_current":[value, 'mA']}.

        Examples:
            storm.ft4222_enable_measure()
            result = storm.ft4222_measure()
            print(result)

        Raise:
            StormException('AD7606 Check busy state timeout!')
            StormException('FT4222H is not connected, please check it!')

        '''

        # Maximum 0.5ms delay between CONVST A,CONVST B rising edges
        self.mcp23008.set_pin(StormDef.PIN_ADC_CONVST, 0)
        time.sleep(StormDef.CONVST_DELAY)
        self.mcp23008.set_pin(StormDef.PIN_ADC_CONVST, 1)

        # Check AD7606 BUSY_PIN state, The BUSY output remains high
        # until the conversion process for all channels is complete.
        last_time = time.time()
        while(time.time() - last_time < StormDef.DEFAULT_TIMEOUT):
            time.sleep(StormDef.CONVST_DELAY)
            if self.mcp23008.get_pin(StormDef.PIN_ADC_BUSY) == 0:
                break
        if time.time() - last_time >= StormDef.DEFAULT_TIMEOUT:
            raise StormException('AD7606 Check busy state timeout!')

        data = self.ftspi.read(8)
        cdw = (data[0] << 8) | data[1]
        volt = StormDef.ADC_VOLT_RATIO * StormDef.AD7606_RANGE * cdw / 32768
        volt *= 1000

        cdw = (data[2] << 8) | data[3]
        sink_curr = StormDef.ADC_CURR_SINK_RATIO * StormDef.AD7606_RANGE * cdw / 32768
        sink_curr *= 1000

        cdw = (data[4] << 8) | data[5]
        source_curr = StormDef.ADC_CURR_SRC_RATIO * StormDef.AD7606_RANGE * cdw / 32768
        source_curr *= 1000

        result = {}
        result['voltage'] = (volt, 'mV')
        result['sink_current'] = (sink_curr, 'mA')
        result['source_current'] = (source_curr, 'mA')
        return result

    def load_calibration(self, calibration_cell_index=StormDef.LATEST_CAL):
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

        if calibration_cell_index == StormDef.LATEST_CAL:
            try:
                cal_index = self.read_latest_calibration_index()
            except Exception as e:
                self._cal_common_error = StormException(str(e))
                return "done"
        else:
            cal_index = calibration_cell_index

        try:
            read_data = self.read_calibration_cell(cal_index)
        except Exception as e:
            self._cal_common_error = StormException("Read calibration cell error: " + str(e))
            return "done"

        self.cal_index = cal_index

        data_size = self._get_cal_size(cal_index)
        start_address = self._get_cal_address(cal_index)

        for range_name, index in self._range_table.items():
            self._calibration_table[range_name] = []
            cal_item_addr = StormDef.CALIBRATION_COE_MAP[range_name][0]
            cal_pos = cal_item_addr - start_address
            # check cal_pos range
            if cal_pos < 0 or cal_pos >= data_size:
                err_info = StormException("Range {} count pos 0x{:x} is invalid".format(range_name, cal_pos))
                self._range_err_table[range_name] = err_info
                continue

            count = len(StormDef.CALIBRATION_COE_MAP[range_name])
            cal_len = count * StormDef.CAL_DATA_LEN
            cal_data = read_data[cal_pos:(cal_pos + cal_len)]

            for i in range(count):
                item_pos = i * StormDef.CAL_DATA_LEN
                data = cal_data[item_pos:(item_pos + StormDef.CAL_DATA_LEN)]

                s = struct.Struct(StormDef.CAL_DATA_PACK_FORMAT)
                pack_data = s.pack(*data)

                s = struct.Struct(StormDef.CAL_DATA_UNPACK_FORMAT)
                result = s.unpack(pack_data)

                if range_name == 'a_volt' or range_name == 'a_sink_curr' or range_name == 'a_src_curr':
                    gain = result[0]
                    offset = 0.0
                elif range_name == 'b_volt' or range_name == 'b_sink_curr' or range_name == 'b_src_curr':
                    gain = 1.0
                    offset = result[0]

                if math.isnan(gain):
                    gain = 1.0

                if math.isnan(offset):
                    offset = 0.0

                self._calibration_table[range_name].append({"gain": gain, "offset": offset})
        return "done"

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

        addr = StormDef.CALIBRATION_COE_MAP[range_name][index]
        data = self.read_nvmem(addr, StormDef.CAL_DATA_LEN)

        s = struct.Struct(StormDef.CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(StormDef.CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)

        if range_name == 'a_volt' or range_name == 'a_sink_curr' or range_name == 'a_src_curr':
            gain = result[0]
            offset = 0.0
        elif range_name == 'b_volt' or range_name == 'b_sink_curr' or range_name == 'b_src_curr':
            gain = 1.0
            offset = result[0]

        if math.isnan(gain):
            gain = 1.0

        if math.isnan(offset):
            offset = 0.0

        return {"gain": gain, "offset": offset}

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

        if range_name == 'a_volt' or range_name == 'a_sink_curr' or range_name == 'a_src_curr':
            w_data = gain
        elif range_name == 'b_volt' or range_name == 'b_sink_curr' or range_name == 'b_src_curr':
            w_data = offset
        else:
            raise StormException("Range {} is invalid".format(range_name))

        addr = StormDef.CALIBRATION_COE_MAP[range_name][index]
        s = struct.Struct('f')
        pack_data = s.pack(w_data)
        s = struct.Struct('4B')
        data = s.unpack(pack_data)
        self.write_nvmem(addr, data)
        return "done"


class Storm(StormBase):
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
        i2c:                instance(I2C), Class instance of I2C, which is used to access
                                                 CAT24C64,MCP23008, ADS1112, AD5696, CAT9555, MAX6642.
        using_ft4222:       boolean, enable ft4222 and init spi and gpio of ft4222. If the using_ft4222 is False,
                                   the ft4222_enable_measure() and ft4222_measure() cannot be used.

   Examples:
        # Create Instance: i2c speed 100KHz
        i2c_bus = I2C('/dev/i2c-0')
        storm = Storm(i2c_bus, using_ft4222=True)

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
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-MJ28-5-020", "GQQ-MJ28-5-02A", "GQQ-MJ28-5-02B",
                  "GQQ-MJ28-5-730", "GQQ-MJ28-5-73A", "GQQ-MJ28-5-73B",
                  "GQQ-MJ28-5-02E", "GQQ-MJ28-5-73E"]

    def __init__(self, i2c=None, using_ft4222=False):
        super(Storm, self).__init__(i2c, using_ft4222,
                                    StormDef.EEPROM_DEV_ADDR)
