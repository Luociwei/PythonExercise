# -*- coding: utf-8 -*-
import math
import time
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.tca9538 import TCA9538
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667R
from mix.driver.smartgiant.common.ic.mcp4725 import MCP4725
from mix.driver.smartgiant.common.ipcore.mix_psu001_sg_r import MIXPSU001SGR
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
from mix.driver.smartgiant.common.module.mixmoduleerror import (InvalidHardwareChannel, InvalidHardwareChannelType,
                                                                InvalidRange, InvalidSampleRate, InvalidSampleCount,
                                                                InvalidTimeout, InvalidCalibrationIndex,
                                                                ModuleDoesNotSupportCalibration,
                                                                AllCalibrationCellsInvalid,
                                                                InvalidCalibrationDataLength,
                                                                InvalidCalibrationDate)

__author__ = 'jihuajiang@SmartGiant'
__version__ = '0.8'


psu001_range_table = {
    "BATT": 0,
    "CHARGE": 1,
    "BATT_VOLT_READ": 2,
    "BATT_CURR_READ_1A": 3,
    "BATT_CURR_READ_1mA": 4,
    "CHARGE_VOLT_READ": 5,
    "CHARGE_CURR_READ": 6,
    "CHARGE_CURR_SET": 7
}


class PSU001014Exception(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class PSU001014Def:
    BATT = 'BATT'
    CHARGE = 'CHARGE'
    BATT_VOLT_READ = 'BATT_VOLT_READ'
    BATT_CURR_READ_1A = 'BATT_CURR_READ_1A'
    BATT_CURR_READ_1mA = 'BATT_CURR_READ_1mA'
    CHARGE_VOLT_READ = 'CHARGE_VOLT_READ'
    CHARGE_CURR_READ = 'CHARGE_CURR_READ'
    CHARGE_CURR_SET = 'CHARGE_CURR_SET'

    DAC_RANGE_DICT = {1: {"min": 0, "max": 4800},
                      2: {"min": 0, "max": 7500}}
    CHANNEL_0 = 0
    CHANNEL_1 = 1
    CHANNEL_BOTH = 2
    BATT_CURR_READ_RANGE_1mA = '1mA'
    BATT_CURR_READ_RANGE_1A = '1A'
    UNIT_mV = 'mV'
    UNIT_mA = 'mA'
    UNIT_uA = 'uA'
    DEFAULT_LEVEL = 0x19
    BATT_ENABLE_BIT = 0
    CHARGE_ENABLE_BIT = 1
    BATT_READ_CURR_RANGE_BIT = 2
    READ_CURR_BIT = 3
    READ_VOLT_BIT = 4
    CHARGE_FLAG_BIT = 5

    CHARGE_FLAG_VOLT = 6000.0

    HIGH_LEVEL = 1
    LOW_LEVEL = 0
    CHARGE_MAX = 8000
    DIR_OUTPUT = 0x00
    VOLTAGE_MIN = 0
    CURRENT_LIMIT_MAX = 1000.0
    EEPROM_DEV_ADDR = 0x50
    NCT75_DEV_ADDR = 0x48
    TCA9538_ADDR = 0x73
    DAC_BATT_ADDR = 0x0c
    DAC_CHARGE_ADDR = 0x0f
    DAC_MCP4725_ADDR = 0x60

    MCP4725_MAX_VOLTAGE = 4600
    MCP4725_MIN_VOLTAGE = 400

    CHARGE_VOLT_DEF = 2000.0
    CHARGE_DIFF = 200.0

    BATT_VOLT_REF = 2100.0
    BATT_DIFF = 500.0
    # default sampling rate is 5 Hz which is defined in Driver ERS
    DEFAULT_AD7175_SAMPLE_RATE = 5
    MCP4725_VREF = 5000.0
    DAC_REF_MODE = 'INTERNAL'
    DAC_VREF = 2500.0
    MAX_VOLTAGE = 5000.0  # mV
    # AD7175 reference voltage
    MVREF = 2500.0
    # Using crystal as AD7175 clock
    CLOCK = 'crystal'
    # AD7175 input voltage is bipolar
    POLAR = 'bipolar'
    AD7175_REF_MODE = 'internal'
    PLAD7175_REG_SIZE = 256
    MIX_PSU001_REG_SIZE = 65536
    AD7175_CONFIG = {"ch0": {"P": "AIN0", "N": "AIN1"}, "ch1": {"P": "AIN2", "N": "AIN3"}}
    DEFAULT_TIMEOUT = 1  # s


class PSU001014(SGModuleDriver):
    '''
    PSU001014(psu001011) is a battery and power supply module.

    compatible = ["GQQ-P128-5-130", "GQQ-P128-5-140"]

    The battery and power supply module provides an isolated battery emulator and a
    charger supply for audio and accessory test stations.

    Args:
        i2c_ext:    instance(I2C), which is used to control nct75, tca9538 and cat24c32.
        i2c_power:  instance(I2C), which is used to control ad5667.
        ipcore:     instance(MIXPSU001SGR)/None, MIXPSU001SGR ip driver instance, if given, user should not use ad7175.

    Examples:
        Example for using aggregate IP:
            # normal init
            i2c_ext = I2C('/dev/i2c-1')
            i2c_power = I2C('/dev/i2c-2')
            psu001 = MIXPSU001SGR('/dev/MIX_PSU001_SG_R_0',ad717x_chip='AD7175',
                                  ad717x_mvref=5000,use_spi=False, use_gpio=False)
            odin = PSU001014(i2c_ext, i2c_power, ipcore=psu001)

            # using ipcore device name
            i2c_ext = I2C('/dev/i2c-1')
            i2c_power = I2C('/dev/i2c-2')
            odin = PSU001014(i2c_ext, i2c_power, ipcore='/dev/MIX_PSU001_SG_R_0')

        Example for measuring single voltage:
            odin.configure_input_channel(1, 'battery', 1000)
            result = odin.read(1)
            print(result)

        Example for measuring multipoint voltage:
            odin.configure_input_channel(1, 'battery', 1000)
            odin.start_buffered_acquisition(1)
            result = odin.read_buffer_statistics(1, 10)
            print(result)
            odin.stop_buffered_acquisition(1)

        Example for measuring single current:
            odin.configure_input_channel(2, 'battery', 1000, 1000)
            result = odin.read(1)
            print(result)

        Example for measuring multipoint current:
            odin.configure_input_channel(2, 'battery', 1000, 1000)
            odin.start_buffered_acquisition(2)
            result = odin.read_buffer_statistics(2, 10)
            print(result)

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-P128-5-130", "GQQ-P128-5-140"]

    rpc_public_api = ["configure_output_channel", "get_output_channel_configuration",
                      "configure_input_channel", "get_input_channel_configuration", "read",
                      "start_buffered_acquisition", "read_buffer", "read_buffer_statistics",
                      "stop_buffered_acquisition", "set_mcp4725_volt", "set_ad5667_volt"
                      ] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c_ext, i2c_power, ipcore):

        if i2c_ext and i2c_power and ipcore:
            eeprom = CAT24C32(PSU001014Def.EEPROM_DEV_ADDR, i2c_ext)
            nct75 = NCT75(PSU001014Def.NCT75_DEV_ADDR, i2c_ext)
            self.tca9538 = TCA9538(PSU001014Def.TCA9538_ADDR, i2c_ext)
            self.ad5667_batt = AD5667R(PSU001014Def.DAC_BATT_ADDR, i2c_power,
                                       ref_mode=PSU001014Def.DAC_REF_MODE, mvref=PSU001014Def.DAC_VREF)
            self.ad5667_charge = AD5667R(PSU001014Def.DAC_CHARGE_ADDR, i2c_power,
                                         ref_mode=PSU001014Def.DAC_REF_MODE, mvref=PSU001014Def.DAC_VREF)
            self.mcp4725 = MCP4725(PSU001014Def.DAC_MCP4725_ADDR, i2c_power, mvref=PSU001014Def.MCP4725_VREF)

            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, PSU001014Def.MIX_PSU001_REG_SIZE)
                self.ipcore = MIXPSU001SGR(axi4_bus, 'AD7175', ad717x_mvref=PSU001014Def.MVREF,
                                           code_polar=PSU001014Def.POLAR, reference=PSU001014Def.AD7175_REF_MODE,
                                           clock=PSU001014Def.CLOCK, use_gpio=False)
            else:
                self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x
            super(PSU001014, self).__init__(eeprom, nct75, range_table=psu001_range_table)
        else:
            raise PSU001014Exception("Invalid parameter, please check")
        self.ch1_output_config = dict()
        self.ch2_output_config = dict()
        self.ch1_input_config = dict()
        self.ch2_input_config = dict()
        self.volt_diff = 3000.0
        self.charge_current_vdac = 0
        self.battery_current_vdac = 0

    def post_power_on_init(self, timeout=PSU001014Def.DEFAULT_TIMEOUT):
        '''
        Init PSU001014 module to a know harware state.

        This function will set io direction to output and set dac to 0 V.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=PSU001014Def.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                self.ad5667_batt.set_reference(PSU001014Def.DAC_REF_MODE)
                self.ad5667_charge.set_reference(PSU001014Def.DAC_REF_MODE)
                self.ad5667_batt.output_volt_dc(PSU001014Def.CHANNEL_BOTH, 0)
                self.ad5667_charge.output_volt_dc(PSU001014Def.CHANNEL_BOTH, 0)
                self.tca9538.set_ports([PSU001014Def.DEFAULT_LEVEL])
                self.tca9538.set_pins_dir([PSU001014Def.DIR_OUTPUT])
                self.tca9538.set_pin(PSU001014Def.BATT_READ_CURR_RANGE_BIT, PSU001014Def.LOW_LEVEL)
                self.ad7175.config = PSU001014Def.AD7175_CONFIG
                self.ad7175.channel_init()
                self.active_channel = None
                self.continuous_sample_mode = False
                self.configure_output_channel(1, PSU001014Def.VOLTAGE_MIN, PSU001014Def.CURRENT_LIMIT_MAX)
                self.configure_output_channel(2, PSU001014Def.VOLTAGE_MIN, PSU001014Def.CURRENT_LIMIT_MAX)
                self.configure_input_channel(1, 'battery', PSU001014Def.DEFAULT_AD7175_SAMPLE_RATE)
                self.configure_input_channel(2, 'battery', PSU001014Def.DEFAULT_AD7175_SAMPLE_RATE, max_range=1000)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise PSU001014Exception("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=PSU001014Def.DEFAULT_TIMEOUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set DAC to output 0 and set output disable.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()

        while True:
            try:
                self.configure_output_channel(1, PSU001014Def.VOLTAGE_MIN, PSU001014Def.CURRENT_LIMIT_MAX)
                self.configure_output_channel(2, PSU001014Def.VOLTAGE_MIN, PSU001014Def.CURRENT_LIMIT_MAX)
                self.configure_input_channel(1, 'battery', PSU001014Def.DEFAULT_AD7175_SAMPLE_RATE)
                self.configure_input_channel(2, 'battery', PSU001014Def.DEFAULT_AD7175_SAMPLE_RATE, max_range=1000)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise PSU001014Exception("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def configure_output_channel(self, channel, voltage, current_limit=None):
        '''
        Configure output channel.

        The set voltage and current_limit is calibrated if calibration mode is `cal`.
        The voltage is calibrated in mV and the current_limit is calibrated in mA.

        Args:
            channel: int, [1, 2], 1 mean the channel for 'battery', 2 mean the channel for 'charge'.
            voltage: float/int, [0~7500], unit is mV, the output voltage value. 0 effectively disables output.
                                'battery' output range is 0~4800 mV,
                                'charge' output range is 0~7500 mV.
            current_limit: float/int, [0~1100], unit is mA, default None, only supported for charge output,
                                      recommended range is [0~1000], [0~1100] is just for debug.

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2.
            InvalidRange() if the provided arguments voltage or current_limit are out of range.

        Returns:
            dict, actual channel configuration. e.g. {"channel": "charge", "voltage": 4000, "current_limit": 1000}.

        Examples:
            config = odin.configure_output_channel(1, 4000, 1000)
            print(config)

        '''
        if channel not in [1, 2]:
            raise InvalidHardwareChannel("Invalid channel")

        if voltage < PSU001014Def.DAC_RANGE_DICT[channel]["min"]:
            raise InvalidRange("Invalid voltage range")
        elif voltage > PSU001014Def.DAC_RANGE_DICT[channel]["max"]:
            raise InvalidRange("Invalid voltage range")

        if current_limit or current_limit == 0:
            if current_limit < 0 or current_limit > 1100:
                raise InvalidRange("Invalid current_limit range")

        dac_output = {1: self.ad5667_batt, 2: self.ad5667_charge}
        output_config = {1: self.ch1_output_config, 2: self.ch2_output_config}
        ad5667 = dac_output[channel]

        if channel == 1:
            self.ch1_output_config['channel'] = 'battery'
            self.ch1_output_config['voltage'] = voltage
            self.ch1_output_config['current_limit'] = None
            self.tca9538.set_pin(PSU001014Def.BATT_ENABLE_BIT, PSU001014Def.HIGH_LEVEL)
            vdac = self.calibrate(PSU001014Def.BATT, voltage)
            enable_bit = PSU001014Def.BATT_ENABLE_BIT
        else:
            if voltage > PSU001014Def.CHARGE_FLAG_VOLT:
                self.tca9538.set_pin(PSU001014Def.CHARGE_FLAG_BIT, PSU001014Def.HIGH_LEVEL)
            else:
                self.tca9538.set_pin(PSU001014Def.CHARGE_FLAG_BIT, PSU001014Def.LOW_LEVEL)

            self.ch2_output_config['channel'] = 'charge'
            self.ch2_output_config['voltage'] = voltage
            if voltage == PSU001014Def.DAC_RANGE_DICT[channel]["min"]:
                self.tca9538.set_pin(PSU001014Def.CHARGE_ENABLE_BIT, PSU001014Def.LOW_LEVEL)
            else:
                self.tca9538.set_pin(PSU001014Def.CHARGE_ENABLE_BIT, PSU001014Def.LOW_LEVEL)

            volt = self.calibrate(PSU001014Def.CHARGE, voltage)
            vdac = volt / 2.0
            enable_bit = PSU001014Def.CHARGE_ENABLE_BIT

        if vdac > PSU001014Def.MAX_VOLTAGE:
            vdac = PSU001014Def.MAX_VOLTAGE

        if vdac < PSU001014Def.VOLTAGE_MIN:
            vdac = PSU001014Def.VOLTAGE_MIN

        if channel == 2:
            # V_dcdc = R1 * (0.6 / R2 + 0.6 / R3 - VDC_SET / R3) + 0.6, R1=165000, R2=10000, R3=100000
            # VDC_SET = R3 * (0.6 / R2 + 0.6 / R3 -(V_dcdc - 0.6) / R1)
            #         = 0.6 * (R3 / R2 + 1) - R3 * (V_dcdc -0.6) / R1
            v_dcdc = (voltage + self.volt_diff) / 1000.0
            r1, r2, r3 = 165000, 10000, 100000
            vdc_set = (0.6 * (r3 / r2 + 1) - r3 * (v_dcdc - 0.6) / r1) * 1000.0

            if voltage < PSU001014Def.CHARGE_VOLT_DEF:
                vdc_set -= PSU001014Def.CHARGE_DIFF
            if vdc_set < PSU001014Def.MCP4725_MIN_VOLTAGE:
                vdc_set = PSU001014Def.MCP4725_MIN_VOLTAGE
            elif vdc_set > PSU001014Def.MCP4725_MAX_VOLTAGE:
                vdc_set = PSU001014Def.MCP4725_MAX_VOLTAGE
            if self.charge_current_vdac <= vdac:
                self.mcp4725.fast_output_volt_dc(vdc_set)
        elif channel == 1:
            # V_dcdc= R1 * (0.6 / R2 + 0.6 / R3 - VDC_SET / R3) + 0.6, R1=75000, R2=10000, R3=100000
            # VDC_SET = R3 * (0.6 / R2 + 0.6 / R3 -(V_dcdc - 0.6) / R1)
            #         = 0.6 * (R3 / R2 + 1) - R3 * (V_dcdc -0.6) / R1
            if voltage <= PSU001014Def.BATT_VOLT_REF:
                v_dcdc = 2.5
            else:
                v_dcdc = (voltage + PSU001014Def.BATT_DIFF) / 1000.0
            r1, r2, r3 = 75000, 10000, 100000
            vdc_set = (0.6 * (r3 / r2 + 1) - r3 * (v_dcdc - 0.6) / r1) * 1000.0
            if vdc_set > PSU001014Def.MAX_VOLTAGE:
                vdc_set = PSU001014Def.MAX_VOLTAGE
            elif vdc_set < PSU001014Def.VOLTAGE_MIN:
                vdc_set = PSU001014Def.VOLTAGE_MIN
            if self.battery_current_vdac <= vdac:
                self.ad5667_batt.output_volt_dc(PSU001014Def.CHANNEL_1, vdc_set)

        if voltage == 0 and channel == 1:
            ad5667.output_volt_dc(PSU001014Def.CHANNEL_0, PSU001014Def.VOLTAGE_MIN)
            self.tca9538.set_pin(enable_bit, PSU001014Def.LOW_LEVEL)
        else:
            ad5667.output_volt_dc(PSU001014Def.CHANNEL_0, vdac)

        if channel == 2:
            if self.charge_current_vdac > vdac:
                self.mcp4725.fast_output_volt_dc(vdc_set)
            self.charge_current_vdac = vdac

        if current_limit and channel == 2:
            self.ch2_output_config['current_limit'] = current_limit
            threshold = self.calibrate(PSU001014Def.CHARGE_CURR_SET, current_limit)
            # I = (Vdac - 24.7) / 2
            vdac = threshold * 2.0 + 24.7

            if vdac > PSU001014Def.MAX_VOLTAGE:
                vdac = PSU001014Def.MAX_VOLTAGE

            if vdac < PSU001014Def.VOLTAGE_MIN:
                vdac = PSU001014Def.VOLTAGE_MIN

            self.ad5667_charge.output_volt_dc(PSU001014Def.CHANNEL_1, vdac)

        return output_config[channel]

    def get_output_channel_configuration(self, channel):
        '''
        Get the configuration of the specified output channel.

        Args:
            channel: int, [1, 2], 1 mean the channel for 'battery', 2 mean the channel for 'charge'.

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2.

        Returns:
            dict, actual channel configuration. e.g. {"channel": "charge", "voltage": 4000, "current_limit": 1000}.

        Examples:
            config = odin.get_output_channel_configuration(1)
            print(config)
        '''
        if channel not in [1, 2]:
            raise InvalidHardwareChannel("Invalid channel")

        output_config = {1: self.ch1_output_config, 2: self.ch2_output_config}
        return output_config[channel]

    def configure_input_channel(self, channel, type, sample_rate, max_range=None):
        '''
        Configure input channel.

        Args:
            channel: int, [1, 2], 1 mean the channel for 'voltage', 2 mean the channel for 'current'.
            type: string, ['battery', 'charge'], types are supported.
            sample_rate: float, [5~250000], unit is Hz, adc measure sampling rate, which not continuouse,
                                                please refer ad7175 datasheet.
            max_range: int, [1, 1000], unit is mA,  maximum range of current, only supported for 'current' of 'battery'

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2.
            InvalidHardwareChannelType() if provided type is not "battery" or "charge".
            InvalidSampleRate() if sample_rate is bad.
            InvalidRange() if max_range are bad values.

        Returns:
            dict, actual channel configuration.
            e.g. {"channel": "current", "type": "battery", "sample_rate": 1000, "max_range": 1000}.

        Examples:
            config = odin.configure_input_channel(2, 'battery', 1000, 1000)
            print(config)

        '''
        if channel not in [1, 2]:
            raise InvalidHardwareChannel("Invalid channel")

        if type not in ['battery', 'charge']:
            raise InvalidHardwareChannelType("Invalid channel type")

        if sample_rate < 5 or sample_rate > 250000:
            raise InvalidSampleRate("Invalid sampling rate range")

        if max_range or max_range == 0:
            if max_range not in [1, 1000]:
                raise InvalidRange("Invalid range")

        pin_level = {'battery': PSU001014Def.HIGH_LEVEL, 'charge': PSU001014Def.LOW_LEVEL}
        input_config = {1: self.ch1_input_config, 2: self.ch2_input_config}
        if channel == 1:
            self.tca9538.set_pin(PSU001014Def.READ_VOLT_BIT, pin_level[type])
            self.ad7175.set_sampling_rate(PSU001014Def.CHANNEL_0, sample_rate)
            self.ch1_input_config['channel'] = 'voltage'
            self.ch1_input_config['type'] = type
            self.ch1_input_config['sample_rate'] = sample_rate
            self.ch1_input_config['max_range'] = None
        else:
            self.tca9538.set_pin(PSU001014Def.READ_CURR_BIT, pin_level[type])
            self.ad7175.set_sampling_rate(PSU001014Def.CHANNEL_1, sample_rate)
            self.ch2_input_config['channel'] = 'current'
            self.ch2_input_config['type'] = type
            self.ch2_input_config['sample_rate'] = sample_rate
            if type == 'battery':
                if max_range == 1:
                    self.ch2_input_config['max_range'] = 1
                    self.tca9538.set_pin(PSU001014Def.BATT_READ_CURR_RANGE_BIT, PSU001014Def.HIGH_LEVEL)
                else:
                    self.ch2_input_config['max_range'] = 1000
                    self.tca9538.set_pin(PSU001014Def.BATT_READ_CURR_RANGE_BIT, PSU001014Def.LOW_LEVEL)
            else:
                self.ch2_input_config['max_range'] = None

        return input_config[channel]

    def get_input_channel_configuration(self, channel):
        '''
        Get the configuration of the input channel.

        Args:
            channel: int, [1, 2], 1 mean the channel for 'voltage', 2 mean the channel for 'current'.

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2.

        Returns:
            dict, actual channel configuration.
            e.g. {"channel": "current", "type": "battery", "sample_rate": 1000, "max_range": 1000}.

        Examples:
            config = odin.get_input_channel_configuration(2)
            print(config)
        '''
        if channel not in [1, 2]:
            raise InvalidHardwareChannel("Invalid channel")

        input_config = {1: self.ch1_input_config, 2: self.ch2_input_config}
        return input_config[channel]

    def read(self, channels, samples_per_channel=1, timeout=10.0):
        '''
        Reads the specified number of samples from each channel.

        Values read are in mV or mA, which is determined by DRI.

        The returned value is calibrated if calibration mode is `cal`. The data read back from the voltage channel
            is calibrated in mV. The data read back in the current channel is calibrated in uA when max_range is 1,
            and it is calibrated in mA when max_range is 1000.

        Args:
            channels: int, [1, 2], 1 mean the channel for 'voltage', 2 mean the channel for 'current'.
            samples_per_channel: int, (>=1), default 1, the number of samples to read from each channel.
            timeout: float, (>=0), default 10.0, the maximum duration the acquisition can take,
                                   in seconds, before returning an exception.

        Exception:
            InvalidHardwareChannel() if provided channel is not 1 or 2.
            InvalidSampleCount() if provided samples_per_channel is not an integer or is <1.
            InvalidTimeout() if provided timeout is <0.

        Returns:
            list, [value1, ..., valueN], measured value defined by configure_input_channel()
                    voltage channel always in mV
                    current channel always in mA

        Examples:
            odin.configure_input_channel(2, 'battery', 1000, 1000)
            result = odin.read(2)
            print(result)
        '''
        if channels not in [1, 2]:
            raise InvalidHardwareChannel("Invalid channel")

        if not isinstance(samples_per_channel, int) or samples_per_channel < 1:
            raise InvalidSampleCount("Invalid sample count")

        if timeout < 0:
            raise InvalidTimeout("Invalid timeout")

        target_data = list()
        if channels == 1:
            if self.ch1_input_config['type'] == 'battery':
                cal_type = PSU001014Def.BATT_VOLT_READ
                self.tca9538.set_pin(PSU001014Def.READ_VOLT_BIT, PSU001014Def.HIGH_LEVEL)
            elif self.ch1_input_config['type'] == 'charge':
                cal_type = PSU001014Def.CHARGE_VOLT_READ
                self.tca9538.set_pin(PSU001014Def.READ_VOLT_BIT, PSU001014Def.LOW_LEVEL)

            for x in range(samples_per_channel):
                volt_raw = self.ad7175.read_volt(PSU001014Def.CHANNEL_0)
                # if channel is battery: Vout = Vadc * 2.5, if channel is charge: Vout = Vadc * 4
                volt = map(lambda x: (x * 2.5) if
                           self.ch1_input_config['type'] == 'battery' else (x * 4.0), [volt_raw])[0]
                volt = self.calibrate(cal_type, volt)

                target_data.append(volt)

            # set pin to default level.
            if self.ch1_input_config['type'] == 'charge':
                self.tca9538.set_pin(PSU001014Def.READ_VOLT_BIT, PSU001014Def.HIGH_LEVEL)

        else:
            if self.ch2_input_config['type'] == 'battery':
                if self.ch2_input_config['max_range'] == 1:
                    cal_type = PSU001014Def.BATT_CURR_READ_1mA
                elif self.ch2_input_config['max_range'] == 1000:
                    cal_type = PSU001014Def.BATT_CURR_READ_1A

                self.tca9538.set_pin(PSU001014Def.READ_CURR_BIT, PSU001014Def.HIGH_LEVEL)
            elif self.ch2_input_config['type'] == 'charge':
                cal_type = PSU001014Def.CHARGE_CURR_READ
                self.tca9538.set_pin(PSU001014Def.READ_CURR_BIT, PSU001014Def.LOW_LEVEL)

            for x in range(samples_per_channel):
                volt = self.ad7175.read_volt(PSU001014Def.CHANNEL_1)
                # if channel is battery: 1mA: I = Vadc/2, 1A: I = Vadc, if channel is charge: I = (Vadc - 24.7mV) / 2
                if self.ch2_input_config['type'] == 'charge':
                    current = (volt - 24.7) / 2.0
                elif cal_type == PSU001014Def.BATT_CURR_READ_1mA:
                    current = volt / 2.0
                else:
                    current = volt

                current = self.calibrate(cal_type, current)
                if self.ch2_input_config['max_range'] == 1:
                    # uA convert to mA
                    current = current / 1000.0

                target_data.append(current)

            # set pin to default level.
            if self.ch2_input_config['type'] == 'charge':
                self.tca9538.set_pin(PSU001014Def.READ_CURR_BIT, PSU001014Def.HIGH_LEVEL)

        return target_data

    def start_buffered_acquisition(self, channels, down_sampling_factor=1, down_sampling_calculation='max'):
        '''
        This function enables continuous sampling and data throughput upload to upper stream.

        Down sampling is supported. For example, when down_sampling_factor =5, down_sampling_calculation=max,
            select the maximal value from every 5 samples, so the actual data rate is reduced by 5.
        During continuous sampling, the functions, like configure_input_channel() read(), cannot be called.

        Args:
            channels: int, [1, 2], 1 mean the channel for 'voltage', 2 mean the channel for 'current'.
            down_sampling_factor: int, (>0), default 1, down sample rate for decimation.
            down_sampling_calculation: string, ['max', 'min'], default 'max'. This parameter takes effect
                                               as long as down_sampling_factor is higher than 1. Default 'max'.

        Exception:
            InvalidHardwareChannel() if provided channels is not 1 or 2.
            InvalidRange() if provided down_sampling_factor is not an integer or is <1.
            InvalidRange() if provided down_sampling_calculation is not 'max' or 'min'.

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.configure_input_channel(1, 'battery', 1000)
            odin.start_buffered_acquisition(1)
            result = odin.read_buffer_statistics(1, 10)
            print(result)
            odin.stop_buffered_acquisition(1)
        '''
        if channels not in [1, 2]:
            raise InvalidHardwareChannel("Invalid channel")

        if not isinstance(down_sampling_factor, int) or down_sampling_factor < 1:
            raise InvalidRange("Invalid range")

        if down_sampling_calculation not in ['max', 'min']:
            raise InvalidRange("Invalid range")

        ch_input_config_dict = {1: self.ch1_input_config, 2: self.ch2_input_config}
        ch_input_config = ch_input_config_dict[channels]
        if ch_input_config['channel'] == 'current':
            pin_id, adc_channel = (PSU001014Def.READ_CURR_BIT, PSU001014Def.CHANNEL_1)
        else:
            pin_id, adc_channel = (PSU001014Def.READ_VOLT_BIT, PSU001014Def.CHANNEL_0)
        pin_level = PSU001014Def.HIGH_LEVEL if ch_input_config['type'] == 'battery' else PSU001014Def.LOW_LEVEL
        sampling_rate = ch_input_config['sample_rate']
        self.tca9538.set_pin(pin_id, pin_level)
        self.ad7175.disable_continuous_sampling(adc_channel)
        time.sleep(0.001)
        self.ad7175.enable_continuous_sampling(adc_channel, sampling_rate,
                                               down_sampling_factor, down_sampling_calculation)

        self.active_channel = channels
        self.continuous_sample_mode = True

        return "done"

    def read_buffer(self, session_id, samples_per_channel=1, timeout=10.0):
        '''
        This function takes a number of samples raw data of the set of sampled value.

        Values read are in mV, which is determined by DRI.

        This function can only be called in continuous mode, a.k.a, after configure_input_channel(),
            start_buffered_acquisition() function is called. Return 0 for the channels that are not enabled.
        During continuous sampling, the functions, like configure_input_channel() read(), cannot be called.

        Args:
            session_id: int, [1, 2], 1 mean the channel for 'voltage', 2 mean the channel for 'current'.
            samples_per_channel: int, [1~512], defualt 1, samples count taken for calculation.
            timeout: float, (>=0), default 10.0, the maximum duration the acquisition can take,
                                   in seconds, before returning an exception.

        Exception:
            InvalidHardwareChannel() if provided session_id is not 1 or 2.
            InvalidSampleCount() if provided samples_per_channel is not an integer or is <1 or >512.
            InvalidTimeout() if provided timeout is <0.

        Returns:
            list, [value,...] the unit of elements in the list is mV.

        Examples:
            odin.configure_input_channel(1, 'battery', 1000)
            odin.start_buffered_acquisition(1)
            result = odin.read_buffer(1, 10)
            print(result)
            odin.stop_buffered_acquisition(1)
        '''
        if session_id not in [1, 2]:
            raise InvalidHardwareChannel("Invalid channel")

        if not isinstance(samples_per_channel, int) or samples_per_channel < 1 or samples_per_channel > 512:
            raise InvalidSampleCount("Invalid sample count")

        if timeout < 0:
            raise InvalidTimeout("Invalid timeout")

        if not self.continuous_sample_mode:
            return 0

        if not self.active_channel:
            return 0

        raw_data = list()
        channel = self.active_channel
        ch_input_config_dict = {1: self.ch1_input_config, 2: self.ch2_input_config}
        ch_input_config = ch_input_config_dict[channel]
        if ch_input_config['channel'] == 'current':
            pin_id, adc_channel = (PSU001014Def.READ_CURR_BIT, PSU001014Def.CHANNEL_1)
        else:
            pin_id, adc_channel = (PSU001014Def.READ_VOLT_BIT, PSU001014Def.CHANNEL_0)
        pin_level = PSU001014Def.HIGH_LEVEL if ch_input_config['type'] == 'battery' else PSU001014Def.LOW_LEVEL
        self.tca9538.set_pin(pin_id, pin_level)

        try:
            raw_data = self.ad7175.get_continuous_sampling_voltage(adc_channel, samples_per_channel)
        except Exception:
            raise

        return raw_data

    def read_buffer_statistics(self, session_id, samples_per_channel=1, timeout=10.0):
        '''
        This function takes a number of samples to calculate RMS/average/max/min value of the set of sampled value.

        Values read are in mV or mA, which is determined by DRI.

        This function can only be called in continuous mode, a.k.a, after configure_input_channel(),
            start_buffered_acquisition() function is called. Return 0 for the channels that are not enabled.
        The returned value is calibrated if calibration mode is `cal`. The data read back from the voltage channel
            is calibrated in mV. The data read back in the current channel is calibrated in uA when max_range is 1,
            and it is calibrated in mA when max_range is 1000.
        During continuous sampling, the functions, like configure_input_channel() read(), cannot be called.

        Args:
            session_id: int, [1, 2], 1 mean the channel for 'voltage', 2 mean the channel for 'current'.
            samples_per_channel: int, [1~512], defualt 1, samples count taken for calculation.
            timeout: float, (>=0), default 10.0, the maximum duration the acquisition can take,
                                   in seconds, before returning an exception.

        Exception:
            InvalidHardwareChannel() if provided session_id is not 1 or 2.
            InvalidSampleCount() if provided samples_per_channel is not an integer or is <1 or >512.
            InvalidTimeout() if provided timeout is <0.

        Returns:
            dict, the channel data to be measured. {
                (rms, unit),
                (avg, unit),
                (max, unit),
                (min, unit)
            },
            for voltage channel #1 current channel #2.

        Examples:
            odin.configure_input_channel(1, 'battery', 1000)
            odin.start_buffered_acquisition(1)
            result = odin.read_buffer_statistics(1, 10)
            print(result)
            odin.stop_buffered_acquisition(1)
        '''
        if session_id not in [1, 2]:
            raise InvalidHardwareChannel("Invalid channel")

        if not isinstance(samples_per_channel, int) or samples_per_channel < 1 or samples_per_channel > 512:
            raise InvalidSampleCount("Invalid sample count")

        if timeout < 0:
            raise InvalidTimeout("Invalid timeout")

        if not self.continuous_sample_mode:
            return 0

        if not self.active_channel:
            return 0
        channel = self.active_channel
        channel_data = list()
        result = dict()
        ch_input_config_dict = {1: self.ch1_input_config, 2: self.ch2_input_config}
        ch_input_config = ch_input_config_dict[channel]
        if ch_input_config['channel'] == 'current':
            pin_id, adc_channel = (PSU001014Def.READ_CURR_BIT, PSU001014Def.CHANNEL_1)
        else:
            pin_id, adc_channel = (PSU001014Def.READ_VOLT_BIT, PSU001014Def.CHANNEL_0)
        pin_level = PSU001014Def.HIGH_LEVEL if ch_input_config['type'] == 'battery' else PSU001014Def.LOW_LEVEL
        self.tca9538.set_pin(pin_id, pin_level)

        if channel == 1:
            cal_type = PSU001014Def.BATT_VOLT_READ if ch_input_config['type'] == 'battery' \
                else PSU001014Def.CHARGE_VOLT_READ
        else:
            if ch_input_config['type'] == 'battery':
                if ch_input_config['max_range'] == 1:
                    cal_type = PSU001014Def.BATT_CURR_READ_1mA
                elif ch_input_config['max_range'] == 1000:
                    cal_type = PSU001014Def.BATT_CURR_READ_1A
            else:
                cal_type = PSU001014Def.CHARGE_CURR_READ

        try:
            channel_data = self.ad7175.get_continuous_sampling_voltage(adc_channel, samples_per_channel)
        except Exception:
            raise

        min_data = min(channel_data)
        max_data = max(channel_data)
        avg_data = sum(channel_data) / len(channel_data)
        rms_data = math.sqrt(sum([x**2 for x in channel_data]) / len(channel_data))

        if channel == 1:
            unit = PSU001014Def.UNIT_mV
            # battery channel: Vout = Vadc * 2.5, charge channel: Vout = Vadc * 4.0
            min_data, max_data, avg_data, rms_data = map(lambda volt: volt * 2.5
                                                         if ch_input_config['type'] == 'battery'
                                                         else volt * 4.0, [min_data, max_data, avg_data, rms_data])
            avg_data = self.calibrate(cal_type, avg_data)
            # set pin to default level.
            if ch_input_config['type'] == 'charge':
                self.tca9538.set_pin(PSU001014Def.READ_VOLT_BIT, PSU001014Def.HIGH_LEVEL)
        else:
            unit = PSU001014Def.UNIT_mA
            if ch_input_config['type'] == 'battery':
                if cal_type == PSU001014Def.BATT_CURR_READ_1mA:
                    min_data, max_data, avg_data, rms_data = map(lambda volt: volt / 2.0,
                                                                 [min_data, max_data, avg_data, rms_data])
                else:
                    min_data, max_data, avg_data, rms_data = map(lambda volt: volt,
                                                                 [min_data, max_data, avg_data, rms_data])
            else:
                # charge channel: I = (Vadc - 24.7mV) / 2
                min_data, max_data, avg_data, rms_data = map(lambda volt: (volt - 24.7) / 2.0,
                                                             [min_data, max_data, avg_data, rms_data])

            avg_data = self.calibrate(cal_type, avg_data)

            if ch_input_config['max_range'] == 1:
                # uA convert to mA
                min_data, max_data, avg_data, rms_data = map(lambda volt: volt / 1000.0,
                                                             [min_data, max_data, avg_data, rms_data])
            # set pin to default level.
            if ch_input_config['type'] == 'charge':
                self.tca9538.set_pin(PSU001014Def.READ_CURR_BIT, PSU001014Def.HIGH_LEVEL)

        result['rms'] = (rms_data, unit + 'rms')
        result['avg'] = (avg_data, unit)
        result['max'] = (max_data, unit)
        result['min'] = (min_data, unit)

        return result

    def stop_buffered_acquisition(self, session_id):
        '''
        This function disables continuous sampling and data throughput upload to upper stream.

        This function can only be called in continuous mode, a.k.a, after start_buffered_acquisition()
            function is called. Return 0 for the channels that are not enabled.

        Args:
            session_id: int, [1, 2], 1 mean the channel for 'voltage', 2 mean the channel for 'current'.

        Exception:
            InvalidHardwareChannel() if provided session_id is not 1 or 2.

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.configure_input_channel(1, 'battery', 1000)
            odin.start_buffered_acquisition(1)
            result = odin.read_buffer_statistics(1, 10)
            print(result)
            odin.stop_buffered_acquisition(1)
        '''
        if session_id not in [1, 2]:
            raise InvalidHardwareChannel("Invalid channel")

        if not self.active_channel:
            return 0
        channel = self.active_channel
        ch_input_config_dict = {1: self.ch1_input_config, 2: self.ch2_input_config}
        ch_input_config = ch_input_config_dict[channel]
        if ch_input_config['channel'] == 'current':
            pin_id, adc_channel = (PSU001014Def.READ_CURR_BIT, PSU001014Def.CHANNEL_1)
        else:
            pin_id, adc_channel = (PSU001014Def.READ_VOLT_BIT, PSU001014Def.CHANNEL_0)
        # set pin to default level.
        self.tca9538.set_pin(pin_id, PSU001014Def.HIGH_LEVEL)
        self.ad7175.disable_continuous_sampling(adc_channel)
        self.active_channel = None
        self.continuous_sample_mode = False

        return "done"

    def set_mcp4725_volt(self, volt):
        '''
        This function set mcp4725 volt, this is a debug function.

        Args:
            volt: float, (0~5000).

        Returns:
            string, "done", api execution successful.

        '''
        assert isinstance(volt, (int, float))
        assert 0.0 <= volt <= PSU001014Def.MCP4725_VREF
        self.mcp4725.fast_output_volt_dc(volt)
        return "done"

    def set_ad5667_volt(self, volt, chan=1, ic="battery"):
        '''
        This function set ad5667 volt, this is a debug function.

        Args:
            volt: float, (0~5000).
            chan: int, [0,1], default 1.
            ic:   string, ['battery', 'charge'], default battery.

        Returns:
            string, "done", api execution successful.

        '''
        assert isinstance(volt, (int, float))
        assert chan in [0, 1]
        assert ic in ["battery", "charge"]
        assert 0.0 <= volt <= PSU001014Def.MAX_VOLTAGE
        dac_output = {"battery": self.ad5667_batt, "charge": self.ad5667_charge}
        ad5667 = dac_output[ic]
        ad5667.output_volt_dc(chan, volt)
        return "done"
