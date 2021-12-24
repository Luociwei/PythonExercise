# -*- coding: utf-8 -*-
import os
import struct
import time
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.core.ic.cat24cxx import CAT24C64
from mix.driver.core.ic.pca9554 import PCA9554
from mix.driver.smartgiant.common.ic.ads1112 import ADS1112
from mix.driver.smartgiant.common.ic.ads1119 import ADS1119
from mix.driver.smartgiant.common.ic.ad569x import AD5696
from mix.driver.smartgiant.common.ic.max6642 import MAX6642
from mix.driver.smartgiant.common.ic.mcp23008 import MCP23008


__author__ = 'weiping.mo@SmartGiant'
__version__ = '0.4'


class StormException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class StormDef:
    # the definition can be found in Driver ERS
    EEPROM_DEV_ADDR = 0x52
    SENSOR_DEV_ADDR = 0x48
    ADC_DEV_ADDR = 0x4A
    DAC_DEV_ADDR = 0x0D
    MCP23008_DEV_ADDR = 0x22
    ICI_CONFIG_ADDR = 0x15

    # Calibration Coefficients Map
    # float-format(4_byte)
    CAL_DATA_LEN = 4
    WRITE_CAL_DATA_PACK_FORMAT = "f"
    WRITE_CAL_DATA_UNPACK_FORMAT = "4B"
    READ_CAL_BYTE = 4
    READ_CAL_DATA_PACK_FORMAT = "4B"
    READ_CAL_DATA_UNPACK_FORMAT = "f"

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

    BACKPACK_SENSOR_DEV_ADDR = 0x49
    ADS1119_DEV_ADDR = 0x40
    PCA9554_DEV_ADDR = 0x22
    CONFIG_LIST = ["740", "030", "040"]
    ADS1119_REF_MODE = "EXTERNAL"
    ADS1119_MVREF = 4096.0  # mV
    ADS1119_SAMPLE_RATE = 1000
    AD5696_MVREF = 4096  # mV


class StormBase(MIXBoard):
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
        spill:               instance/None,           Class instance of SPILL board.

    '''

    rpc_public_api = ['read_output_voltage', 'read_source_current', 'read_sink_current',
                      'get_local_temperature', 'get_remote_temperature', 'set_output_voltage', 'ft4222_enable_measure',
                      'ft4222_measure', 'legacy_read_calibration_cell', 'legacy_write_calibration_cell',
                      'legacy_erase_calibration_cell'] + MIXBoard.rpc_public_api
    rpc_public_api = list(set(rpc_public_api))

    def __init__(self, i2c, ft4222_gpiow_file, ft4222_spimr_file, eeprom_devaddr, spill=None):
        self.spill = spill
        self.eeprom = CAT24C64(eeprom_devaddr, i2c)
        self._hardware_version = None
        self._hardware_version = self._get_hardware_version()
        if self._hardware_version in StormDef.CONFIG_LIST:
            self.ad5696 = AD5696(StormDef.DAC_DEV_ADDR, i2c, StormDef.AD5696_MVREF)
            self.ads1119 = ADS1119(StormDef.ADS1119_DEV_ADDR, i2c, StormDef.ADS1119_REF_MODE,
                                   StormDef.ADS1119_MVREF, StormDef.ADS1119_SAMPLE_RATE)
            self.pca9554 = PCA9554(StormDef.PCA9554_DEV_ADDR, i2c)
            self.backpack_max6642 = MAX6642(StormDef.BACKPACK_SENSOR_DEV_ADDR, i2c)
        else:
            self.ads1112 = ADS1112(StormDef.ADC_DEV_ADDR, i2c)
            self.ad5696 = AD5696(StormDef.DAC_DEV_ADDR, i2c)
            self.max6642 = MAX6642(StormDef.SENSOR_DEV_ADDR, i2c)
            self.mcp23008 = MCP23008(StormDef.MCP23008_DEV_ADDR, i2c)

        self.ft4222_gpiow_file = ft4222_gpiow_file
        self.ft4222_spimr_file = ft4222_spimr_file
        super(StormBase, self).__init__(self.eeprom, None)

    def _get_hardware_version(self):
        if not self._hardware_version:
            version = self.eeprom.read(0, 1)[0]
            if version >= 2:
                version = self._hardware_version = self.eeprom.read(StormDef.ICI_CONFIG_ADDR, 3)
                version = ''.join([chr(ch) for ch in version])
        return version

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

        if self.is_use_cal_data():
            volt_val = volt_val / 1000.0  # mV convert to V
            a_volt = self.legacy_read_calibration_cell('a_volt')
            b_volt = self.legacy_read_calibration_cell('b_volt')
            volt_val = self.cal_pipe(a_volt, b_volt, volt_val)
            volt_val = volt_val * 1000.0  # V convert to mV

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

        if self.is_use_cal_data():
            curr_val = curr_val / 1000.0  # mA convert to A
            a_src_curr = self.legacy_read_calibration_cell('a_src_curr')
            b_src_curr = self.legacy_read_calibration_cell('b_src_curr')
            curr_val = self.cal_pipe(a_src_curr, b_src_curr, curr_val)
            curr_val = curr_val * 1000.0  # A convert to mA

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

        if self.is_use_cal_data():
            curr_val = curr_val / 1000.0  # mA convert to A
            a_sink_curr = self.legacy_read_calibration_cell('a_sink_curr')
            b_sink_curr = self.legacy_read_calibration_cell('b_sink_curr')
            curr_val = self.cal_pipe(a_sink_curr, b_sink_curr, curr_val)
            curr_val = curr_val * 1000.0  # A convert to mA

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
        assert os.access(self.ft4222_gpiow_file, os.F_OK | os.X_OK), 'path <{}> not exist or execute'.format(
            self.ft4222_gpiow_file)

        # Run `gpiow 0 2 1` and get the stdout
        cmd = self.ft4222_gpiow_file + ' 0 2 1'
        output = os.popen(cmd).read()

        if 'locID =' in output:
            # Configure AD7608 RST,CONVST,BUSY direction.
            if self._hardware_version in StormDef.CONFIG_LIST:
                self.pca9554.set_pin_dir(StormDef.PIN_ADC_BUSY, 'input')
                self.pca9554.set_pin_dir(StormDef.PIN_ADC_RST, 'output')
                self.pca9554.set_pin_dir(StormDef.PIN_ADC_CONVST, 'output')
            else:
                self.mcp23008.set_pin_dir(StormDef.PIN_ADC_BUSY, 'input')
                self.mcp23008.set_pin_dir(StormDef.PIN_ADC_RST, 'output')
                self.mcp23008.set_pin_dir(StormDef.PIN_ADC_CONVST, 'output')
        else:
            raise StormException('FT4222H is not connected, please check it!')

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
        assert os.access(self.ft4222_spimr_file, os.F_OK | os.X_OK), 'path <{}> not exist or execute'.format(
            self.ft4222_spimr_file)

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
            source_curr = StormDef.ADC_CURR_SRC_RATIO * StormDef.AD7606_RANGE * cdw / 32768
            source_curr *= 1000

            result = {}
            result['voltage'] = (volt, 'mV')
            result['sink_current'] = (sink_curr, 'mA')
            result['source_current'] = (source_curr, 'mA')
            return result
        else:
            raise StormException('FT4222H is not connected, please check it!')

    def legacy_write_calibration_cell(self, cal_item, cal_value):
        '''
        MIXBoard calibration data write.

        Args:
            cal_item:   string, ['a_volt', 'b_volt', 'a_sink_curr', 'b_sink_curr',
                                 'a_src_curr', 'b_src_curr'], calibration item.
            cal_value:  int/float, calibration value.

        Returns:
            string, "done", api execution successful.

        '''
        assert cal_item in StormDef.CALIBRATION_COE_MAP
        assert isinstance(cal_value, (int, float))

        s = struct.Struct(StormDef.WRITE_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(float(cal_value))
        s = struct.Struct(StormDef.WRITE_CAL_DATA_UNPACK_FORMAT)
        data = s.unpack(pack_data)
        address = StormDef.CALIBRATION_COE_MAP[cal_item][0]
        self.write_eeprom(address, data)
        return "done"

    def legacy_read_calibration_cell(self, cal_item):
        '''
        MIXBoard calibration data read.

        Args:
            cal_item:   string, ['a_volt', 'b_volt', 'a_sink_curr', 'b_sink_curr',
                                'a_src_curr', 'b_src_curr'],  calibration item.

        '''
        assert cal_item in StormDef.CALIBRATION_COE_MAP

        address = StormDef.CALIBRATION_COE_MAP[cal_item][0]
        data = self.read_eeprom(address, StormDef.READ_CAL_BYTE)

        s = struct.Struct(StormDef.READ_CAL_DATA_PACK_FORMAT)
        pack_data = s.pack(*data)

        s = struct.Struct(StormDef.READ_CAL_DATA_UNPACK_FORMAT)
        result = s.unpack(pack_data)[0]

        return result

    def legacy_erase_calibration_cell(self, cal_item):
        '''
        MIXBoard calibration data erase.

        Args:
            cal_item:   string, ['a_volt', 'b_volt', 'a_sink_curr', 'b_sink_curr',
                                'a_src_curr', 'b_src_curr'],  calibration item.

        Returns:
            string, "done", api execution successful.

        '''

        data = [0xff for i in range(StormDef.CAL_DATA_LEN)]
        address = StormDef.CALIBRATION_COE_MAP[cal_item][0]
        self.write_eeprom(address, data)
        return "done"

    def cal_pipe(self, coe_a, coe_b, raw_data):
        '''
        MIXBoard get the calibrated results.

        Args:
            coe_a:    int/float, calibration coefficients.
            coe_b:    int/float, calibration coefficients.
            raw_data: int/float, raw data.

        Formula:
            Result = raw_data * (1 + coe_a)  + coe_b

        '''
        assert isinstance(coe_a, (int, float))
        assert isinstance(coe_b, (int, float))
        assert isinstance(raw_data, (int, float))

        return raw_data * (1 + coe_a) + coe_b


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
        i2c:                 instance(I2C)/None, Class instance of PLI2CBus, which is used to access
                                                 CAT24C64,MCP23008, ADS1112, AD5696, CAT9555, MAX6642.
        ft4222_gpiow_file:   string,             FT4222 gpiow firmware file absolute path.
        ft4222_spimr_file:   string,             FT4222 spimr firmware file absolute path.
        eeprom_devaddr:      int,                Eeprom device address.

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
    compatible = ["GQQ-MJ28-020", "GQQ-MJ28-02A", "GQQ-MJ28-02B",
                  "GQQ-MJ28-730", "GQQ-MJ28-73A", "GQQ-MJ28-73B",
                  "GQQ-MJ28-02E", "GQQ-MJ28-73E"]

    def __init__(self, i2c=None, ft4222_gpiow_file='', ft4222_spimr_file=''):
        super(Storm, self).__init__(i2c, ft4222_gpiow_file, ft4222_spimr_file,
                                    StormDef.EEPROM_DEV_ADDR)
