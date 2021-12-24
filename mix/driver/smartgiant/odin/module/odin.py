# -*- coding: utf-8 -*-
import math
import time
from mix.driver.core.ic.tca9538 import TCA9538
from mix.driver.core.ic.tca9538_emulator import TCA9538Emulator
from mix.driver.smartgiant.common.module.mix_board import MIXBoard
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667R
from mix.driver.smartgiant.common.ic.ad56x7_emulator import AD5667REmulator
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_daqt1_sg_r import MIXDAQT1SGR
from mix.driver.smartgiant.common.ipcore.mix_ad717x_sg import MIXAd7175SG
from mix.driver.smartgiant.common.ipcore.mix_ad7175_sg_emulator import MIXAd7175SGEmulator


__author__ = 'jihuajiang@SmartGiant'
__version__ = '0.2'


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

    CH_TYPE_BATTERY = 'battery'
    CH_TYPE_CHARGE = 'charge'
    MEASURE_TYPE_CURR = 'current'
    MEASURE_TYPE_VOLT = 'voltage'
    CHANNEL_0 = 0
    CHANNEL_1 = 1
    CHANNEL_ALL = 2
    BATT_CURR_READ_RANGE_1mA = '1mA'
    BATT_CURR_READ_RANGE_1A = '1A'
    UNIT_mV = 'mV'
    UNIT_mA = 'mA'
    UNIT_uA = 'uA'
    DEFAULT_LEVEL = 0x18
    BATT_ENABLE_BIT = 0
    CHARGE_ENABLE_BIT = 1
    BATT_READ_CURR_RANGE_BIT = 2
    READ_CURR_BIT = 3
    READ_VOLT_BIT = 4
    HIGH_LEVEL = 1
    LOW_LEVEL = 0
    CHARGE_ENABLE = 1
    BATT_CURR_1MA_ENABLE = 0x04
    OUTPUT_DISABLE = 0x00
    BATT_MAX = 5000
    CHARGE_MAX = 8000
    DIR_OUTPUT = 0x00
    VOLTAGE_MIN = 0
    CURRENT_LIMIT_MAX = 1000.0
    CURRENT_LIMIT_MIN = 0
    EEPROM_DEV_ADDR = 0x50
    NCT75_DEV_ADDR = 0x48
    TCA9538_ADDR = 0x73
    DAC_BATT_ADDR = 0x0c
    DAC_CHARGE_ADDR = 0x0f
    POINTS_MAX = 512
    POINTS_MIN = 1
    MUX_DELAY_MAX = 10000
    MUX_DELAY_MIN = 0
    TO_SECONE = 0.001
    # default sampling rate is 5 Hz which is defined in Driver ERS
    DEFAULT_AD7175_SAMPLE_RATE = 5
    AD7175_SAMPLE_RATE_MIN = 5
    AD7175_SAMPLE_RATE_MAX = 250000
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
    MIX_DAQT1_REG_SIZE = 65535
    AD7175_CONFIG = {"ch0": {"P": "AIN0", "N": "AIN1"}, "ch1": {"P": "AIN2", "N": "AIN3"}}


class Odin(MIXBoard):
    '''
    Odin(psu001010) is a battery and power supply module.

    compatible = ["GQQ-PSU001011-001"]

    The battery and power supply module provides an isolated battery emulator and a
    charger supply for audio and accessory test stations.

    Args:
        i2c_ext:  instance(I2C)/None, which is used to control nct75, tca9538 and cat24c32.
                 If not given, emulator will be created.
        i2c_power:  instance(I2C)/None, which is used to control ad5667. If not given,
                     emulator will be created.
        ad7175:     instance(ADC)/None, Class instance of AD7175, if not using this parameter, will create emulator.

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
            wolverine = Wolverine(i2c_ext, i2c_power, '/dev/MIX_AD717X_0')

        Example for using aggregate IP:
            # normal init
            i2c_ext = I2C('/dev/i2c-1')
            i2c_power = I2C('/dev/i2c-2')
            daqt1 = MIXDAQT1SGR('/dev/MIX_DAQT1',ad717x_chip='AD7175',ad717x_mvref=5000,use_spi=False, use_gpio=False)
            odin = Odin(i2c_ext, i2c_power, ipcore=daqt1)

            # using ipcore device name
            i2c_ext = I2C('/dev/i2c-1')
            i2c_power = I2C('/dev/i2c-2')
            odin = Odin(i2c_ext, i2c_power, ipcore='/dev/MIX_DAQT1')

        Example for measuring single voltage:
            result = odin.voltage_measure('battery')
            print("voltage={}, unit={}".format(result[0], result[1]))

        Example for measuring multipoint voltage:
            odin.enable_continuous_measure('battery', 'voltage', 1000)
            result = odin.voltage_sample('battery', 100, 0, True)
            print(result)
            odin.disable_continuous_measure('battery')

        Example for measuring single current:
            result = odin.current_measure('2mA', 5)
            print("current={}, unit={}".format(result[0], result[1]))

        Example for measuring multipoint current:
            odin.enable_continuous_measure('battery', 'current', 1000)
            result = odin.current_sample('battery', 100, 0, True)
            print(result)
            odin.disable_continuous_measure('battery')

    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-PSU001011-001"]

    rpc_public_api = ['module_init', 'enable_battery_output', 'disable_battery_output',
                      'enable_continuous_measure', 'disable_continuous_measure', 'voltage_sample',
                      'current_sample', 'set_current_limit', 'set_measure_path', 'get_measure_path',
                      'voltage_measure', 'current_measure', 'enable_charge_output', 'disable_charge_output',
                      'set_sample_rate', 'get_sample_rate',
                      'datalogger_start', 'datalogger_stop'] + MIXBoard.rpc_public_api

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
                axi4_bus = AXI4LiteBus(ipcore, OdinDef.MIX_DAQT1_REG_SIZE)
                self.ipcore = MIXDAQT1SGR(axi4_bus, 'AD7175', ad717x_mvref=OdinDef.MVREF,
                                          code_polar=OdinDef.POLAR, reference=OdinDef.AD7175_REF_MODE,
                                          clock=OdinDef.CLOCK, use_gpio=False)
            else:
                self.ipcore = ipcore
            self.ad7175 = self.ipcore.ad717x

        elif not ad7175 and not ipcore:
            self.ad7175 = MIXAd7175SGEmulator("ad7175_emulator", OdinDef.PLAD7175_REG_SIZE)

        if i2c_ext and i2c_power:
            eeprom = CAT24C32(OdinDef.EEPROM_DEV_ADDR, i2c_ext)
            nct75 = NCT75(OdinDef.NCT75_DEV_ADDR, i2c_ext)
            self.tca9538 = TCA9538(OdinDef.TCA9538_ADDR, i2c_ext)
            self.ad5667_batt = AD5667R(OdinDef.DAC_BATT_ADDR, i2c_power,
                                       ref_mode=OdinDef.DAC_REF_MODE, mvref=OdinDef.DAC_VREF)
            self.ad5667_charge = AD5667R(OdinDef.DAC_CHARGE_ADDR, i2c_power,
                                         ref_mode=OdinDef.DAC_REF_MODE, mvref=OdinDef.DAC_VREF)
            super(Odin, self).__init__(eeprom, nct75, range_table=odin_range_table)

        elif not i2c_ext and not i2c_power:
            self.tca9538 = TCA9538Emulator(OdinDef.TCA9538_ADDR)
            self.ad5667_batt = AD5667REmulator('ad5667_emulator')
            self.ad5667_charge = AD5667REmulator('ad5667_emulator')
            super(Odin, self).__init__(None, None, cal_table={}, range_table=odin_range_table)

        else:
            raise OdinException("Invalid parameter, please check")

    def module_init(self):
        '''
        Init odin module. This function will set io direction to output and set dac to 0 V.

        Returns:
            string, "done", api execution successful.

        '''
        self.load_calibration()
        self.tca9538.set_pins_dir([OdinDef.DIR_OUTPUT])
        self.tca9538.set_ports([OdinDef.DEFAULT_LEVEL])
        self.ad5667_batt.set_reference(OdinDef.DAC_REF_MODE)
        self.ad5667_charge.set_reference(OdinDef.DAC_REF_MODE)
        self.ad5667_batt.output_volt_dc(OdinDef.CHANNEL_ALL, OdinDef.VOLTAGE_MIN)
        self.ad5667_charge.output_volt_dc(OdinDef.CHANNEL_ALL, OdinDef.VOLTAGE_MIN)
        self.set_measure_path(OdinDef.CH_TYPE_BATTERY, OdinDef.BATT_CURR_READ_RANGE_1A)
        self.ad7175.reset()
        # Need some time to wait for reset.
        time.sleep(0.002)
        self.ad7175.config = OdinDef.AD7175_CONFIG
        self.ad7175.channel_init()
        self.ad7175.set_sampling_rate(OdinDef.CHANNEL_0, OdinDef.DEFAULT_AD7175_SAMPLE_RATE)
        self.ad7175.set_sampling_rate(OdinDef.CHANNEL_1, OdinDef.DEFAULT_AD7175_SAMPLE_RATE)

        self.set_current_limit(OdinDef.CURRENT_LIMIT_MAX)

        self.ad7175_sampling_rate = OdinDef.DEFAULT_AD7175_SAMPLE_RATE
        self.measure_path = OdinDef.BATT_CURR_READ_RANGE_1A
        self.batt_flag = False
        self.charge_flag = False

        return "done"

    def enable_battery_output(self, voltage):
        '''
        battery output enable.

        Args:
            voltage: int, from 0 to 5000 mV,unit is mV.

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.enable_battery_output(1000)
        '''
        assert OdinDef.VOLTAGE_MIN <= voltage
        assert voltage <= OdinDef.BATT_MAX

        if not self.batt_flag:
            self.tca9538.set_pin(OdinDef.BATT_ENABLE_BIT, OdinDef.HIGH_LEVEL)
            self.batt_flag = True
        vdac = self.calibrate(OdinDef.BATT, voltage)

        if vdac > OdinDef.MAX_VOLTAGE:
            vdac = OdinDef.MAX_VOLTAGE

        if vdac < OdinDef.VOLTAGE_MIN:
            vdac = OdinDef.VOLTAGE_MIN

        self.ad5667_batt.output_volt_dc(OdinDef.CHANNEL_0, vdac)

        return "done"

    def disable_battery_output(self):
        '''
        battery output disable.

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.disable_battery_output()
        '''
        self.ad5667_batt.output_volt_dc(OdinDef.CHANNEL_0, OdinDef.VOLTAGE_MIN)

        self.tca9538.set_pin(OdinDef.BATT_ENABLE_BIT, OdinDef.LOW_LEVEL)

        self.batt_flag = False

        return "done"

    def enable_continuous_measure(self, ch_type, measure_type, sampling_rate):
        '''
        enable charge or battery channel adc as continuous mode.

        Args:
            ch_type:    string, ('battery','charge').
            measure_type:  string, ('voltage','current').
            sampling_rate: int, (5-250000).

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.enable_continuous_measure('battery', 'voltage', 1000)
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]
        assert measure_type in [OdinDef.MEASURE_TYPE_CURR, OdinDef.MEASURE_TYPE_VOLT]

        channel = OdinDef.CHANNEL_0 if measure_type == OdinDef.MEASURE_TYPE_VOLT else OdinDef.CHANNEL_1
        self.ad7175.enable_continuous_sampling(channel, sampling_rate)

        return "done"

    def disable_continuous_measure(self, ch_type):
        '''
        enable charge or battery channel adc as continuous mode.

        Args:
            ch_type: string, ('battery','charge').

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.disable_continuous_measure('battery')
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]

        self.ad7175.disable_continuous_sampling(OdinDef.CHANNEL_0)

        return "done"

    def voltage_sample(self, ch_type, points, mux_delay=0, raw=True):
        '''
        readback charge or battery channel voltage in continuous mode.

        Args:
            ch_type:    string, ('battery','charge').
            points:     int, (1-512), read counts value.
            mux_delay:  int, (0-10000), unit is ms, delay time then read counts value.
            raw:    bool, True for raw data, False for cal data.

        Returns:
            dict, {"rms":[value, unit], "mean":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
            odin.enable_continuous_measure('battery','voltage',1000)
            volt = odin.voltage_sample('battery', 100, 0, True)
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]
        assert OdinDef.POINTS_MIN <= points
        assert points <= OdinDef.POINTS_MAX
        assert OdinDef.MUX_DELAY_MIN <= mux_delay
        assert mux_delay <= OdinDef.MUX_DELAY_MAX
        assert raw in [True, False]

        if mux_delay > 0:
            time.sleep(mux_delay * OdinDef.TO_SECONE)

        if ch_type == OdinDef.CH_TYPE_BATTERY:
            cal_type = OdinDef.BATT_VOLT_READ
            self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.HIGH_LEVEL)
        else:
            cal_type = OdinDef.CHARGE_VOLT_READ
            self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.LOW_LEVEL)

        value = self.ad7175.get_continuous_sampling_voltage(OdinDef.CHANNEL_0, points)
        # set pin to default level.
        if ch_type == OdinDef.CH_TYPE_CHARGE:
            self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.HIGH_LEVEL)

        min_volt = min(value)
        max_volt = max(value)
        mean_volt = sum(value) / len(value)
        rms = math.sqrt(sum([x**2 for x in value]) / len(value))

        # battery channel: Vout = Vadc * 2.5, charge channel: Vout = Vadc * 4.0
        min_volt, max_volt, mean_volt, rms = map(lambda volt: volt * 2.5 if ch_type == OdinDef.CH_TYPE_BATTERY else
                                                 volt * 4.0, [min_volt, max_volt, mean_volt, rms])

        if not raw:
            mean_volt = self.calibrate(cal_type, mean_volt)

        return {"rms": [rms, OdinDef.UNIT_mV], "mean": [mean_volt, OdinDef.UNIT_mV],
                "max": [max_volt, OdinDef.UNIT_mV], "min": [min_volt, OdinDef.UNIT_mV]}

    def current_sample(self, ch_type, points, mux_delay=0, raw=True):
        '''
        readback charge or battery channel voltage in continuous mode.

        Args:
            ch_type:    string, ('battery','charge').
            points:     int, (1-512), read counts value.
            mux_delay:  int, (0-10000), unit is ms, delay time then read counts value.
            raw:    bool, True for raw data, False for cal data.

        Returns:
            dict, {"rms":[value, unit], "mean":[value, unit], "max":[value, unit], "min":[value, unit]}.

        Examples:
            odin.enable_continuous_measure('battery','current',1000)
            volt = odin.current_sample('battery', 100, 0, True)
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]
        assert OdinDef.POINTS_MIN <= points
        assert points <= OdinDef.POINTS_MAX
        assert OdinDef.MUX_DELAY_MIN <= mux_delay
        assert mux_delay <= OdinDef.MUX_DELAY_MAX
        assert raw in [True, False]

        if mux_delay > 0:
            time.sleep(mux_delay * OdinDef.TO_SECONE)

        unit = OdinDef.UNIT_mA
        if ch_type == OdinDef.CH_TYPE_BATTERY:
            cal_type, unit = (OdinDef.BATT_CURR_READ_1A, OdinDef.UNIT_mA) if \
                self.measure_path == OdinDef.BATT_CURR_READ_RANGE_1A else (OdinDef.BATT_CURR_READ_1mA, OdinDef.UNIT_uA)
            self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.HIGH_LEVEL)
        else:
            cal_type = OdinDef.CHARGE_CURR_READ
            self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.LOW_LEVEL)

        value = self.ad7175.get_continuous_sampling_voltage(OdinDef.CHANNEL_1, points)
        # set pin to default level.
        if ch_type == OdinDef.CH_TYPE_CHARGE:
            self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.HIGH_LEVEL)

        min_volt = min(value)
        max_volt = max(value)
        mean_volt = sum(value) / len(value)
        rms = math.sqrt(sum([x**2 for x in value]) / len(value))

        # battery channel 1A range: I = Vadc, battery channel 1mA range: I = 10 * Vadc.
        if ch_type == OdinDef.CH_TYPE_BATTERY:
            if self.measure_path == OdinDef.BATT_CURR_READ_RANGE_1A:
                min_curr, max_curr, mean_curr, rms = map(lambda volt: volt, [min_volt, max_volt, mean_volt, rms])
            else:
                min_curr, max_curr, mean_curr, rms = map(lambda volt: 10.0 * volt, [min_volt, max_volt, mean_volt, rms])
        else:
            # charge channel: I = (Vadc - 24.7mV) / 2
            min_curr, max_curr, mean_curr, rms = map(lambda volt: (
                volt - 24.7) / 2.0, [min_volt, max_volt, mean_volt, rms])

        if not raw:
            mean_volt = self.calibrate(cal_type, mean_volt)

        return {"rms": [rms, unit], "mean": [mean_curr, unit], "max": [max_curr, unit], "min": [min_curr, unit]}

    def set_current_limit(self, threshold):
        '''
        set charge channel limit curretn, battery channel not need to set.

        Args:
            threshold: float, (0-1000), unit is mA.

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.set_current_limit(200)
        '''
        assert OdinDef.CURRENT_LIMIT_MIN <= threshold
        assert threshold <= OdinDef.CURRENT_LIMIT_MAX

        threshold = self.calibrate(OdinDef.CHARGE_CURR_SET, threshold)
        # I = (Vdac - 24.7) / 2
        vdac = threshold * 2.0 + 24.7
        self.ad5667_charge.output_volt_dc(OdinDef.CHANNEL_1, vdac)

        return 'done'

    def set_measure_path(self, ch_type, scope):
        '''
        set battery channel measure path, charge channel not need to set.

        Args:
            ch_type:    string, ('battery').
            scope:    string, ('1A','1mA').

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.set_measure_path('battery','1mA')
        '''
        assert ch_type == OdinDef.CH_TYPE_BATTERY
        assert scope in [OdinDef.BATT_CURR_READ_RANGE_1mA, OdinDef.BATT_CURR_READ_RANGE_1A]

        level = OdinDef.HIGH_LEVEL if scope == OdinDef.BATT_CURR_READ_RANGE_1mA else OdinDef.LOW_LEVEL

        self.tca9538.set_pin(OdinDef.BATT_READ_CURR_RANGE_BIT, level)

        self.measure_path = scope

        return 'done'

    def get_measure_path(self, ch_type):
        '''
        set battery channel measure path, charge channel not need to set.

        Args:
            ch_type:    string, ('battery').

        Returns:
            string, scope value.

        Examples:
            odin.get_measure_path('battery')
        '''
        assert ch_type == OdinDef.CH_TYPE_BATTERY

        return self.measure_path

    def voltage_measure(self, ch_type, mux_delay=0):
        '''
        readback charge or battery channel voltage.

        Args:
            ch_type:    string, ('battery','charge').
            mux_delay:  int, (0-10000), unit is ms, delay time then read counts value.

        Returns:
            list, [voltage, 'mV'].

        Examples:
            volt = odin.voltage_measure('battery', 0)
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]
        assert OdinDef.MUX_DELAY_MIN <= mux_delay
        assert mux_delay <= OdinDef.MUX_DELAY_MAX

        if mux_delay > 0:
            time.sleep(mux_delay * OdinDef.TO_SECONE)

        if ch_type == OdinDef.CH_TYPE_BATTERY:
            cal_type = OdinDef.BATT_VOLT_READ
            self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.HIGH_LEVEL)
        else:
            cal_type = OdinDef.CHARGE_VOLT_READ
            self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.LOW_LEVEL)

        volt_raw = self.ad7175.read_volt(OdinDef.CHANNEL_0)
        # set pin to default level.
        if ch_type == OdinDef.CH_TYPE_CHARGE:
            self.tca9538.set_pin(OdinDef.READ_VOLT_BIT, OdinDef.HIGH_LEVEL)
        # if channel is battery: Vout = Vadc * 2.5, if channel is charge: Vout = Vadc * 4
        volt = map(lambda x: (x * 2.5) if ch_type == OdinDef.CH_TYPE_BATTERY else (x * 4.0), [volt_raw])[0]

        volt = self.calibrate(cal_type, volt)

        return [volt, OdinDef.UNIT_mV]

    def current_measure(self, ch_type, mux_delay=0):
        '''
        readback charge or battery channel current.

        Args:
            ch_type:    string, ('battery','charge').
            mux_delay:  int, (0-10000), unit is ms, delay time then read counts value.

        Returns:
            list, [current, 'mA'].

        Examples:
            volt = odin.current_measure('battery', 0)
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]
        assert OdinDef.MUX_DELAY_MIN <= mux_delay
        assert mux_delay <= OdinDef.MUX_DELAY_MAX

        if mux_delay > 0:
            time.sleep(mux_delay * OdinDef.TO_SECONE)

        unit = OdinDef.UNIT_mA
        if ch_type == OdinDef.CH_TYPE_BATTERY:
            cal_type, unit = (OdinDef.BATT_CURR_READ_1A, OdinDef.UNIT_mA) if \
                self.measure_path == OdinDef.BATT_CURR_READ_RANGE_1A else (OdinDef.BATT_CURR_READ_1mA, OdinDef.UNIT_uA)
            self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.HIGH_LEVEL)
        else:
            cal_type = OdinDef.CHARGE_CURR_READ
            self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.LOW_LEVEL)

        volt = self.ad7175.read_volt(OdinDef.CHANNEL_1)
        # set pin to default level.
        if ch_type == OdinDef.CH_TYPE_CHARGE:
            self.tca9538.set_pin(OdinDef.READ_CURR_BIT, OdinDef.HIGH_LEVEL)
        # battery channel 1A range: I = Vadc, battery channel 1mA range: I = 10 * Vadc.
        if ch_type == OdinDef.CH_TYPE_BATTERY:
            current = volt

        else:
            # charge channel: I = (Vadc - 24.7mV) / 2
            current = (volt - 24.7) / 2.0

        current = self.calibrate(cal_type, current)

        return [current, unit]

    def enable_charge_output(self, voltage):
        '''
        charge output enable.

        Args:
            voltage: int, (0-8000), unit is mV.

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.enable_charge_output(1000)
        '''
        assert OdinDef.VOLTAGE_MIN <= voltage
        assert voltage <= OdinDef.CHARGE_MAX

        if not self.charge_flag:
            self.tca9538.set_pin(OdinDef.CHARGE_ENABLE_BIT, OdinDef.HIGH_LEVEL)

            self.charge_flag = True

        voltage = self.calibrate(OdinDef.CHARGE, voltage)
        # Vout = 1.62 * Vdac
        vdac = voltage / 2.0

        if vdac > OdinDef.MAX_VOLTAGE:
            vdac = OdinDef.MAX_VOLTAGE

        if vdac < OdinDef.VOLTAGE_MIN:
            vdac = OdinDef.VOLTAGE_MIN

        self.ad5667_charge.output_volt_dc(OdinDef.CHANNEL_0, vdac)

        return 'done'

    def disable_charge_output(self):
        '''
        charge output disable.

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.disable_charge_output()
        '''
        self.ad5667_charge.output_volt_dc(OdinDef.CHANNEL_0, OdinDef.VOLTAGE_MIN)

        self.tca9538.set_pin(OdinDef.CHARGE_ENABLE_BIT, OdinDef.LOW_LEVEL)

        self.charge_flag = False

        return 'done'

    def set_sample_rate(self, ch_type, sampling_rate):
        '''
        set adc sample rate.

        Args:
            ch_type: string, ('battery','charge').
            sampling_rate: int, (5-250000), adc sampling rate.

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.set_sample_rate('battery', 1000)
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]
        assert OdinDef.AD7175_SAMPLE_RATE_MIN <= sampling_rate
        assert sampling_rate <= OdinDef.AD7175_SAMPLE_RATE_MAX

        self.ad7175.set_sampling_rate(OdinDef.CHANNEL_0, sampling_rate)
        self.ad7175.set_sampling_rate(OdinDef.CHANNEL_1, sampling_rate)
        self.ad7175_sampling_rate = sampling_rate

        return 'done'

    def get_sample_rate(self, ch_type):
        '''
        get adc sample rate.

        Args:
            ch_type: string, ('battery','charge').

        Returns:
            int, sample rate.

        Examples:
            sampling_rate = odin.get_sample_rate('battery')
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]

        return self.ad7175.get_sampling_rate(OdinDef.CHANNEL_0)

    def datalogger_start(self, ch_type, measure_type):
        '''
        start datalogger.

        Args:
            ch_type: string, ('battery','charge').
            measure_type: string, ('voltage','current').

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.datalogger_start('battery', 'current')
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]
        assert measure_type in [OdinDef.MEASURE_TYPE_VOLT, OdinDef.MEASURE_TYPE_CURR]

        pin_bit, ch = (OdinDef.READ_CURR_BIT, OdinDef.CHANNEL_1) if measure_type == OdinDef.MEASURE_TYPE_CURR else (
            OdinDef.READ_VOLT_BIT, OdinDef.CHANNEL_0)

        pin_level = OdinDef.HIGH_LEVEL if ch_type == OdinDef.CH_TYPE_BATTERY else OdinDef.LOW_LEVEL

        self.tca9538.set_pin(pin_bit, pin_level)
        self.ad7175.enable_continuous_sampling(ch, self.ad7175_sampling_rate)

        return 'done'

    def datalogger_stop(self, ch_type, measure_type):
        '''
        stop datalogger.

        Args:
            ch_type: string, ('battery','charge').
            measure_type: string, ('voltage','current').

        Returns:
            string, "done", api execution successful.

        Examples:
            odin.datalogger_stop('battery', 'current')
        '''
        assert ch_type in [OdinDef.CH_TYPE_BATTERY, OdinDef.CH_TYPE_CHARGE]
        assert measure_type in [OdinDef.MEASURE_TYPE_VOLT, OdinDef.MEASURE_TYPE_CURR]

        pin_bit = OdinDef.READ_CURR_BIT if measure_type == OdinDef.MEASURE_TYPE_CURR else OdinDef.READ_VOLT_BIT
        # set pin to default level.
        self.tca9538.set_pin(pin_bit, OdinDef.HIGH_LEVEL)

        if measure_type == OdinDef.MEASURE_TYPE_CURR:
            self.ad7175.disable_continuous_sampling(OdinDef.CHANNEL_1)
        else:
            self.ad7175.disable_continuous_sampling(OdinDef.CHANNEL_0)

        return 'done'
