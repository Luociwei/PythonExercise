# -*- coding: utf-8 -*-
import math
import time
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.core.ic.tca9538 import TCA9538
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667R
from mix.driver.smartgiant.common.ipcore.mix_psu001_sg_r import MIXPSU001SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
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


odin_range_table = {
    "BATT": 0,
    "CHARGE": 1,
    "BATT_VOLT_READ": 2,
    "BATT_CURR_READ_1A": 3,
    "BATT_CURR_READ_1mA": 4,
    "CHARGE_VOLT_READ": 5,
    "CHARGE_CURR_READ": 6,
    "CHARGE_CURR_SET": 7
}


class OdinException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class OdinDef:
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
    DEFAULT_LEVEL = 0x1b
    BATT_ENABLE_BIT = 0
    CHARGE_ENABLE_BIT = 1
    BATT_READ_CURR_RANGE_BIT = 2
    READ_CURR_BIT = 3
    READ_VOLT_BIT = 4
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
    # default sampling rate is 5 Hz which is defined in Driver ERS
    DEFAULT_AD7175_SAMPLE_RATE = 5
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
    ADC_ERROR_BIT = (1 << 6)
    STATUS_REG_ADDR = 0x00
    DATA_REG_ADDR = 0x04
    BATT_VOLT_RANGE = 6.25  # V
    CHARGE_VOLT_RANGE = 10.0  # V
    BATT_CURR_RANGE_1mA = 0.0025  # A
    BATT_CURR_RANGE_1A = 2.5  # A
    CHARGE_CURR_RANGE = 1.23765  # A


class Odin(SGModuleDriver):
    '''
    Odin(psu001011) is a battery and power supply module.

    compatible = ["GQQ-P128-5-110", "GQQ-P128-5-120"]

    The battery and power supply module provides an isolated battery emulator and a
    charger supply for audio and accessory test stations.

    Args:
        i2c_ext:    instance(I2C)/None, which is used to control nct75, tca9538 and cat24c32.
        i2c_power:  instance(I2C)/None, which is used to control ad5667. If not given.
        ad7175:     instance(ADC)/None, Class instance of AD7175.
        ipcore:     instance(MIXPSU001SGR)/None, MIXPSU001SGR ip driver instance, if given, user should not use ad7175.

    Examples:
        Example for using no-aggregate IP:
            # normal init
            ad7175 = MIXAd7175SG('/dev/MIX_AD717X_0', 5000)
            i2c_ext = I2C('/dev/i2c-1')
            i2c_power = I2C('/dev/i2c-2')
            odin = Odin(i2c_ext, i2c_power, ad7175)

            # using ipcore device name string
            i2c_ext = I2C('/dev/i2c-1')
            i2c_power = I2C('/dev/i2c-2')
            odin = Odin(i2c_ext, i2c_power, '/dev/MIX_AD717X_0')

        Example for using aggregate IP:
            # normal init
            i2c_ext = I2C('/dev/i2c-1')
            i2c_power = I2C('/dev/i2c-2')
            psu001 = MIXPSU001SGR('/dev/MIX_PSU001_SG_R_0',ad717x_chip='AD7175',
                                  ad717x_mvref=5000,use_spi=False, use_gpio=False)
            odin = Odin(i2c_ext, i2c_power, ipcore=psu001)

            # using ipcore device name
            i2c_ext = I2C('/dev/i2c-1')
            i2c_power = I2C('/dev/i2c-2')
            odin = Odin(i2c_ext, i2c_power, ipcore='/dev/MIX_PSU001_SG_R_0')

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
    compatible = ["GQQ-P128-5-110", "GQQ-P128-5-120"]

    rpc_public_api = ["configure_output_channel", "get_output_channel_configuration",
                      "configure_input_channel", "get_input_channel_configuration", "read",
                      "start_buffered_acquisition", "read_buffer", "read_buffer_statistics",
                      "stop_buffered_acquisition"] + SGModuleDriver.rpc_public_api

    def __init__(self, i2c_ext=None, i2c_power=None, ad7175=None, ipcore=None):

        if ad7175 and not ipcore:
            if isinstance(ad7175, basestring):
                axi4 = AXI4LiteBus(ad7175, OdinDef.PLAD7175_REG_SIZE)
                self.ad7175 = MIXAd7175SG(axi4, mvref=OdinDef.MVREF, code_polar=OdinDef.POLAR,
                                          reference=OdinDef.AD7175_REF_MODE, clock=OdinDef.CLOCK)
            else:
                self.ad7175 = ad7175

        elif not ad7175 and ipcore:
            if isinstance(ipcore, basestring):
                axi4_bus = AXI4LiteBus(ipcore, OdinDef.MIX_PSU001_REG_SIZE)
                self.ipcore = MIXPSU001SGR(axi4_bus, 'AD7175', ad717x_mvref=OdinDef.MVREF,
                                           code_polar=OdinDef.POLAR, reference=OdinDef.AD7175_REF_MODE,
                                           clock=OdinDef.CLOCK, use_gpio=False)
            else:
                self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x

        if i2c_ext and i2c_power:
            eeprom = CAT24C32(OdinDef.EEPROM_DEV_ADDR, i2c_ext)
            nct75 = NCT75(OdinDef.NCT75_DEV_ADDR, i2c_ext)
            self.tca9538 = TCA9538(OdinDef.TCA9538_ADDR, i2c_ext)
            self.ad5667_batt = AD5667R(OdinDef.DAC_BATT_ADDR, i2c_power,
                                       ref_mode=OdinDef.DAC_REF_MODE, mvref=OdinDef.DAC_VREF)
            self.ad5667_charge = AD5667R(OdinDef.DAC_CHARGE_ADDR, i2c_power,
                                         ref_mode=OdinDef.DAC_REF_MODE, mvref=OdinDef.DAC_VREF)
            self.ch1_output_config = dict()
            self.ch2_output_config = dict()
            self.ch1_input_config = dict()
            self.ch2_input_config = dict()
            super(Odin, self).__init__(eeprom, nct75, range_table=odin_range_table)
        else:
            raise OdinException("Invalid parameter, please check")

    def post_power_on_init(self, timeout=OdinDef.DEFAULT_TIMEOUT):
        '''
        Init Odin module to a know harware state.

        This function will set io direction to output and set dac to 0 V.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=OdinDef.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                self.ad5667_batt.set_reference(OdinDef.DAC_REF_MODE)
                self.ad5667_charge.set_reference(OdinDef.DAC_REF_MODE)
                self.ad5667_batt.output_volt_dc(OdinDef.CHANNEL_BOTH, 0)
                self.ad5667_charge.output_volt_dc(OdinDef.CHANNEL_BOTH, 0)
                self.tca9538.set_ports([OdinDef.DEFAULT_LEVEL])
                self.tca9538.set_pins_dir([OdinDef.DIR_OUTPUT])
                self.tca9538.set_pin(OdinDef.BATT_READ_CURR_RANGE_BIT, OdinDef.LOW_LEVEL)
                self.ad7175.config = OdinDef.AD7175_CONFIG
                self.ad7175.channel_init()
                self.active_channel = None
                self.continuous_sample_mode = False
                self.configure_output_channel(1, OdinDef.VOLTAGE_MIN, OdinDef.CURRENT_LIMIT_MAX)
                self.configure_output_channel(2, OdinDef.VOLTAGE_MIN, OdinDef.CURRENT_LIMIT_MAX)
                self.configure_input_channel(1, 'battery', OdinDef.DEFAULT_AD7175_SAMPLE_RATE)
                self.configure_input_channel(2, 'battery', OdinDef.DEFAULT_AD7175_SAMPLE_RATE, max_range=1000)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise OdinException("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=OdinDef.DEFAULT_TIMEOUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set DAC to output 0 and set output disable.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()

        while True:
            try:
                self.configure_output_channel(1, OdinDef.VOLTAGE_MIN, OdinDef.CURRENT_LIMIT_MAX)
                self.configure_output_channel(2, OdinDef.VOLTAGE_MIN, OdinDef.CURRENT_LIMIT_MAX)
                self.configure_input_channel(1, 'battery', OdinDef.DEFAULT_AD7175_SAMPLE_RATE)
                self.configure_input_channel(2, 'battery', OdinDef.DEFAULT_AD7175_SAMPLE_RATE, max_range=1000)
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise OdinException("Timeout: {}".format(e.message))

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
            current_limit: float/int, [0~1000], unit is mA, default None, only supported for charge output.

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

        if voltage < OdinDef.DAC_RANGE_DICT[channel]["min"] or voltage > OdinDef.DAC_RANGE_DICT[channel]["max"]:
            raise InvalidRange("Invalid voltage range")

        if current_limit or current_limit == 0:
            if current_limit < 0 or current_limit > 1000:
                raise InvalidRange("Invalid current_limit range")

        dac_output = {1: self.ad5667_batt, 2: self.ad5667_charge}
        output_config = {1: self.ch1_output_config, 2: self.ch2_output_config}
        ad5667 = dac_output[channel]

        if channel == 1:
            self.ch1_output_config['channel'] = 'battery'
            self.ch1_output_config['voltage'] = voltage
            self.ch1_output_config['current_limit'] = None
            self.tca9538.set_pin(OdinDef.BATT_ENABLE_BIT, OdinDef.HIGH_LEVEL)
            vdac = self.calibrate(OdinDef.BATT, voltage)
            enable_bit = OdinDef.BATT_ENABLE_BIT
        else:
            self.ch2_output_config['channel'] = 'charge'
            self.ch2_output_config['voltage'] = voltage
            self.tca9538.set_pin(OdinDef.CHARGE_ENABLE_BIT, OdinDef.HIGH_LEVEL)
            volt = self.calibrate(OdinDef.CHARGE, voltage)
            vdac = volt / 2.0
            enable_bit = OdinDef.CHARGE_ENABLE_BIT

        if vdac > OdinDef.MAX_VOLTAGE:
            vdac = OdinDef.MAX_VOLTAGE

        if vdac < OdinDef.VOLTAGE_MIN:
            vdac = OdinDef.VOLTAGE_MIN

        if voltage == 0:
            ad5667.output_volt_dc(OdinDef.CHANNEL_0, OdinDef.VOLTAGE_MIN)
            if channel == 1:
                self.tca9538.set_pin(enable_bit, OdinDef.LOW_LEVEL)
        else:
            ad5667.output_volt_dc(OdinDef.CHANNEL_0, vdac)

        if current_limit and channel == 2:
            self.ch2_output_config['current_limit'] = current_limit
            threshold = self.calibrate(OdinDef.CHARGE_CURR_SET, current_limit)
            # I = (Vdac - 24.7) / 2
            vdac = threshold * 2.0 + 24.7

            if vdac > OdinDef.MAX_VOLTAGE:
                vdac = OdinDef.MAX_VOLTAGE

            if vdac < OdinDef.VOLTAGE_MIN:
                vdac = OdinDef.VOLTAGE_MIN

            self.ad5667_charge.output_volt_dc(OdinDef.CHANNEL_1, vdac)

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

        pin_level = {'battery': OdinDef.HIGH_LEVEL, 'charge': OdinDef.LOW_LEVEL}
        input_config = {1: self.ch1_input_config, 2: self.ch2_input_config}
        if channel == 1:
            self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, pin_level[type])
            self.ad7175.set_sampling_rate(OdinDef.CHANNEL_0, sample_rate)
            self.ch1_input_config['channel'] = 'voltage'
            self.ch1_input_config['type'] = type
            self.ch1_input_config['sample_rate'] = sample_rate
            self.ch1_input_config['max_range'] = None
        else:
            self.tca9538.set_pin(OdinDef.READ_CURR_BIT, pin_level[type])
            self.ad7175.set_sampling_rate(OdinDef.CHANNEL_1, sample_rate)
            self.ch2_input_config['channel'] = 'current'
            self.ch2_input_config['type'] = type
            self.ch2_input_config['sample_rate'] = sample_rate
            if type == 'battery':
                if max_range == 1:
                    self.ch2_input_config['max_range'] = 1
                    self.tca9538.set_pin(OdinDef.BATT_READ_CURR_RANGE_BIT, OdinDef.HIGH_LEVEL)
                else:
                    self.ch2_input_config['max_range'] = 1000
                    self.tca9538.set_pin(OdinDef.BATT_READ_CURR_RANGE_BIT, OdinDef.LOW_LEVEL)
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
                cal_type = OdinDef.BATT_VOLT_READ
                self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.HIGH_LEVEL)
            elif self.ch1_input_config['type'] == 'charge':
                cal_type = OdinDef.CHARGE_VOLT_READ
                self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.LOW_LEVEL)

            for x in range(samples_per_channel):
                try:
                    volt_raw = self.ad7175.read_volt(OdinDef.CHANNEL_0)
                except Exception as e:
                    if (OdinDef.ADC_ERROR_BIT & self.ad7175.read_register(OdinDef.STATUS_REG_ADDR)):
                        reg_data = self.ad7175.read_register(OdinDef.DATA_REG_ADDR)

                        if self.ch1_input_config['type'] == 'battery':
                            volt_range = OdinDef.BATT_VOLT_RANGE
                        else:
                            volt_range = OdinDef.CHARGE_VOLT_RANGE

                        if reg_data == 0xFFFFFF:
                            raise OdinException('Overrange! the voltage value exceeds the {}V range'.format(volt_range))
                        elif reg_data == 0x000000:
                            raise OdinException('Underrange! the voltage value is lower than \
                                                 negative {}V range'.format(volt_range))
                        else:
                            raise OdinException("{}".format(e.message))
                    else:
                        raise OdinException("{}".format(e.message))
                # if channel is battery: Vout = Vadc * 2.5, if channel is charge: Vout = Vadc * 4
                volt = map(lambda x: (x * 2.5) if
                           self.ch1_input_config['type'] == 'battery' else (x * 4.0), [volt_raw])[0]
                volt = self.calibrate(cal_type, volt)

                target_data.append(volt)

            # set pin to default level.
            if self.ch1_input_config['type'] == 'charge':
                self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.HIGH_LEVEL)

        else:
            if self.ch2_input_config['type'] == 'battery':
                if self.ch2_input_config['max_range'] == 1:
                    cal_type = OdinDef.BATT_CURR_READ_1mA
                elif self.ch2_input_config['max_range'] == 1000:
                    cal_type = OdinDef.BATT_CURR_READ_1A

                self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.HIGH_LEVEL)
            elif self.ch2_input_config['type'] == 'charge':
                cal_type = OdinDef.CHARGE_CURR_READ
                self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.LOW_LEVEL)

            for x in range(samples_per_channel):
                try:
                    volt = self.ad7175.read_volt(OdinDef.CHANNEL_1)
                except Exception as e:
                    if (OdinDef.ADC_ERROR_BIT & self.ad7175.read_register(OdinDef.STATUS_REG_ADDR)):
                        reg_data = self.ad7175.read_register(OdinDef.DATA_REG_ADDR)

                        if self.ch2_input_config['type'] == 'battery':
                            if self.ch2_input_config['max_range'] == 1:
                                curr_range = OdinDef.BATT_CURR_RANGE_1mA
                            else:
                                curr_range = OdinDef.BATT_CURR_RANGE_1A
                        else:
                            curr_range = OdinDef.CHARGE_CURR_RANGE

                        if reg_data == 0xFFFFFF:
                            raise OdinException('Overrange! the current value exceeds the {}A range'.format(curr_range))
                        elif reg_data == 0x000000:
                            raise OdinException('Underrange! the current value is lower than \
                                                 negative {}A range'.format(curr_range))
                        else:
                            raise OdinException("{}".format(e.message))
                    else:
                        raise OdinException("{}".format(e.message))
                # if channel is battery: I = Vadc, if channel is charge: I = (Vadc - 24.7mV) / 2
                current = (volt - 24.7) / 2.0 if self.ch2_input_config['type'] == 'charge' else volt
                current = self.calibrate(cal_type, current)
                if self.ch2_input_config['max_range'] == 1:
                    # uA convert to mA
                    current = current / 1000.0

                target_data.append(current)

            # set pin to default level.
            if self.ch2_input_config['type'] == 'charge':
                self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.HIGH_LEVEL)

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
        pin_id, adc_channel = (OdinDef.READ_CURR_BIT, OdinDef.CHANNEL_1) if ch_input_config['channel'] == 'current' \
            else (OdinDef.READ_VOLT_BIT, OdinDef.CHANNEL_0)
        pin_level = OdinDef.HIGH_LEVEL if ch_input_config['type'] == 'battery' else OdinDef.LOW_LEVEL
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
        pin_id, adc_channel = (OdinDef.READ_CURR_BIT, OdinDef.CHANNEL_1) if ch_input_config['channel'] == 'current' \
            else (OdinDef.READ_VOLT_BIT, OdinDef.CHANNEL_0)
        pin_level = OdinDef.HIGH_LEVEL if ch_input_config['type'] == 'battery' else OdinDef.LOW_LEVEL
        self.tca9538.set_pin(pin_id, pin_level)

        try:
            raw_data = self.ad7175.get_continuous_sampling_voltage(adc_channel, samples_per_channel)
        except Exception as e:
            self.stop_buffered_acquisition(session_id)
            if (OdinDef.ADC_ERROR_BIT & self.ad7175.read_register(OdinDef.STATUS_REG_ADDR)):
                reg_data = self.ad7175.read_register(OdinDef.DATA_REG_ADDR)

                if channel == 1:
                    if ch_input_config['type'] == 'battery':
                        volt_range = OdinDef.BATT_VOLT_RANGE
                    else:
                        volt_range = OdinDef.CHARGE_VOLT_RANGE

                    if reg_data == 0xFFFFFF:
                        raise OdinException('Overrange! the voltage value exceeds the {}V range'.format(volt_range))
                    elif reg_data == 0x000000:
                        raise OdinException('Underrange! the voltage value is lower than \
                                             negative {}V range'.format(volt_range))
                    else:
                        raise OdinException("{}".format(e.message))

                else:
                    if ch_input_config['type'] == 'battery':
                        if ch_input_config['max_range'] == 1:
                            curr_range = OdinDef.BATT_CURR_RANGE_1mA
                        else:
                            curr_range = OdinDef.BATT_CURR_RANGE_1A
                    else:
                        curr_range = OdinDef.CHARGE_CURR_RANGE

                    if reg_data == 0xFFFFFF:
                        raise OdinException('Overrange! the current value exceeds the {}A range'.format(curr_range))
                    elif reg_data == 0x000000:
                        raise OdinException('Underrange! the current value is lower than \
                                             negative {}A range'.format(curr_range))
                    else:
                        raise OdinException("{}".format(e.message))

            else:
                raise OdinException("{}".format(e.message))

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
        pin_id, adc_channel = (OdinDef.READ_CURR_BIT, OdinDef.CHANNEL_1) if ch_input_config['channel'] == 'current' \
            else (OdinDef.READ_VOLT_BIT, OdinDef.CHANNEL_0)
        pin_level = OdinDef.HIGH_LEVEL if ch_input_config['type'] == 'battery' else OdinDef.LOW_LEVEL
        self.tca9538.set_pin(pin_id, pin_level)

        if channel == 1:
            cal_type = OdinDef.BATT_VOLT_READ if ch_input_config['type'] == 'battery' else OdinDef.CHARGE_VOLT_READ
        else:
            if ch_input_config['type'] == 'battery':
                if ch_input_config['max_range'] == 1:
                    cal_type = OdinDef.BATT_CURR_READ_1mA
                elif ch_input_config['max_range'] == 1000:
                    cal_type = OdinDef.BATT_CURR_READ_1A
            else:
                cal_type = OdinDef.CHARGE_CURR_READ

        try:
            channel_data = self.ad7175.get_continuous_sampling_voltage(adc_channel, samples_per_channel)
        except Exception as e:
            self.stop_buffered_acquisition(session_id)
            if (OdinDef.ADC_ERROR_BIT & self.ad7175.read_register(OdinDef.STATUS_REG_ADDR)):
                reg_data = self.ad7175.read_register(OdinDef.DATA_REG_ADDR)

                if channel == 1:
                    if ch_input_config['type'] == 'battery':
                        volt_range = OdinDef.BATT_VOLT_RANGE
                    else:
                        volt_range = OdinDef.CHARGE_VOLT_RANGE

                    if reg_data == 0xFFFFFF:
                        raise OdinException('Overrange! the voltage value exceeds the {}V range'.format(volt_range))
                    elif reg_data == 0x000000:
                        raise OdinException('Underrange! the voltage value is lower than \
                                             negative {}V range'.format(volt_range))
                    else:
                        raise OdinException("{}".format(e.message))

                else:
                    if ch_input_config['type'] == 'battery':
                        if ch_input_config['max_range'] == 1:
                            curr_range = OdinDef.BATT_CURR_RANGE_1mA
                        else:
                            curr_range = OdinDef.BATT_CURR_RANGE_1A
                    else:
                        curr_range = OdinDef.CHARGE_CURR_RANGE

                    if reg_data == 0xFFFFFF:
                        raise OdinException('Overrange! the current value exceeds the {}A range'.format(curr_range))
                    elif reg_data == 0x000000:
                        raise OdinException('Underrange! the current value is lower than \
                                             negative {}A range'.format(curr_range))
                    else:
                        raise OdinException("{}".format(e.message))

            else:
                raise OdinException("{}".format(e.message))

        min_data = min(channel_data)
        max_data = max(channel_data)
        avg_data = sum(channel_data) / len(channel_data)
        rms_data = math.sqrt(sum([x**2 for x in channel_data]) / len(channel_data))

        if channel == 1:
            unit = OdinDef.UNIT_mV
            # battery channel: Vout = Vadc * 2.5, charge channel: Vout = Vadc * 4.0
            min_data, max_data, avg_data, rms_data = map(lambda volt: volt * 2.5
                                                         if ch_input_config['type'] == 'battery'
                                                         else volt * 4.0, [min_data, max_data, avg_data, rms_data])
            avg_data = self.calibrate(cal_type, avg_data)
            # set pin to default level.
            if ch_input_config['type'] == 'charge':
                self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.HIGH_LEVEL)
        else:
            unit = OdinDef.UNIT_mA
            if ch_input_config['type'] == 'battery':
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
                self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.HIGH_LEVEL)

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
        pin_id, adc_channel = (OdinDef.READ_CURR_BIT, OdinDef.CHANNEL_1) if ch_input_config['channel'] == 'current' \
            else (OdinDef.READ_VOLT_BIT, OdinDef.CHANNEL_0)
        # set pin to default level.
        self.tca9538.set_pin(pin_id, OdinDef.HIGH_LEVEL)
        self.ad7175.disable_continuous_sampling(adc_channel)
        self.active_channel = None
        self.continuous_sample_mode = False

        return "done"
