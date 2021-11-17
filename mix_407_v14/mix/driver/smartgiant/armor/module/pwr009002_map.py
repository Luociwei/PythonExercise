# -*- coding: utf-8 -*-
from mix.driver.core.ic.cat24cxx import CAT24C32
from mix.driver.core.ic.nct75 import NCT75
from mix.driver.smartgiant.common.ic.ad56x7r import AD5667R
from mix.driver.smartgiant.common.ic.mcp4725 import MCP4725
from mix.driver.smartgiant.common.ic.pca9536 import PCA9536
from mix.driver.smartgiant.common.ic.ad527x import AD5272
from mix.driver.smartgiant.common.module.sg_module_driver import SGModuleDriver
import time


__author__ = 'zicheng.huang@SmartGiant'
__version__ = 'V0.1.6'


armor_range_table = {
    "batt": 0,
    "ppvrect": 1,
    "vddmain": 2,
    "eload": 3
}


class ArmorDef:

    IO_SET = 0x00
    DEFAULT_TIMEOUT = 1  # s

    BATT_CURR_LIMIT = 1500  # mA
    MAIN_CURR_LIMIT = 500  # mA
    DBG_CURR_LIMIT = 500  # mA
    DAC_VOLTAGE_REF = 2500  # mV
    DAC3_VOLTAGE_REF = 3300  # mV
    DAC1_DEV_ADDR = 0x0C
    DAC2_DEV_ADDR = 0x0F
    DAC3_DEV_ADDR = 0x60
    RES_1_ADDR = 0x2C
    RES_2_ADDR = 0x2F
    DAC_CHANNEL = {'A': 0, 'B': 1, 'ALL': 2}
    ENABLE_LEVEL = 1
    DISABLE_LEVEL = 0
    BATT_PIN = 0
    RECT_PIN = 1
    MAIN_PIN = 2
    RES_CMD_ADDR = 0x07
    RES_CMD_DATA = 0x02
    RES_WORK_MODE = 'normal'
    SLEEP_TIME = 0.005

    MAX_VOLTAGE = 2500.0
    MIN_VOLTAGE = 0.0

    EEPROM_DEV_ADDR = 0x50
    SENSOR_DEV_ADDR = 0x48
    IO_EXP_DEV_ADDR = 0x41

    UNIT_CONVERSION = 1000.0

    MODULE_RANGE_TABLE = ('BATT', 'MAIN', 'DBG', 'ELOAD')
    DAC_CHANNEL_LIST = ('BATT', 'MAIN', 'DBG')
    DAC_RANGE_DICT = {"BATT": {"min": 0, "max": 5000},
                      "MAIN": {"min": 0, "max": 5000},
                      "DBG": {"min": 0, "max": 8000},
                      "ELOAD": {"min": 0, "max": 500}}


CURR_LIMIT = {
    "BATT": lambda threshold: 200 <= threshold <= 1500,
    "MAIN": lambda threshold: 200 <= threshold <= 600,
    "DBG": lambda threshold: 200 <= threshold <= 600
}


formula = {
    # VOUT = 2.24 * DAC - 30.6
    "batt": lambda vout: (((vout) + 30.6) / 2.24),
    # VOUT = 1.62 * (2.24 * DAC) - 30.6
    "vddmain": lambda vout: (((vout) + 30.6) / 2.24),
    # VOUT = 2.24 * DAC - 30.6
    "ppvrect": lambda vout: (((vout / 1.62) + 30.6) / 2.24),
    # CURR = (2.24*DAC-30.6) / 3.1
    "eload": lambda curr: (((curr) * 3.1 + 30.6) / 2.24),
    # limit = (9800 * 1.18 / resistor)
    "vddmain_limit": lambda res: (((1.18 / res) * 9800)),
    # limit = (4.75 - 2 * Vout) / 13750 * 15000
    "ppvrect_limit": lambda res: (((13750.0 / 15000.0 * res - 4.75) / (-2.0))),
    # limit = (9800 * 1.18 / resistor)
    "batt_limit": lambda res: (((1.18 / res) * 9800)),
    # Vback = I * 0.1 * 100
    "vddmain_readback": lambda vback: (vback / (0.1 * 100)),
    # Vback = I * 0.1 * 100
    "ppvrect_readback": lambda vback: (vback / (0.1 * 100)),
    # Vback = I * 0.1 * 40.83
    "batt_readback": lambda vback: (vback / (0.1 * 40.83)),
    # Vback = I * 0.1 * 100
    "eload_readback": lambda vback: (vback / (0.1 * 100)),
}


class ArmorException(Exception):
    def __init__(self, err_str):
        self.err_reason = '%s.' % (err_str)

    def __str__(self):
        return self.err_reason


class ArmorBase(SGModuleDriver):
    '''
    Base class of Armor and ArmorCompatible.

    Providing common Armor methods.

    Args:
        dac_i2c:                 instance(I2C),  which is used to control ad5667, ad5272 and mcp4725.
        eeprom_i2c:              instance(I2C),  which is used to control nct75, cat24c32 and pca9536.
        ocp_main_pin:            instance(Pin),  which is used to check 'MAIN' output source OCP status.
        ocp_batt_pin:            instance(Pin),  which is used to check 'BATT' output source OCP status.
        ocp_dbg_pin:             instance(Pin),  which is used to check 'DBG' output source OCP status.

    '''

    rpc_public_api = ['set_current_limit', 'get_current_limit', 'write_output_voltage', 'get_output_voltage',
                      'get_ocp_status', 'set_clear_ocp', 'enable_output_voltage', 'disable_output_voltage',
                      'write_eload_current', 'enable_eload', 'disable_eload'] + SGModuleDriver.rpc_public_api

    def __init__(self, dac_i2c=None, eeprom_i2c=None, ocp_main_pin=None, ocp_batt_pin=None, ocp_dbg_pin=None):

        self.dac1 = AD5667R(ArmorDef.DAC1_DEV_ADDR, dac_i2c, ArmorDef.DAC_VOLTAGE_REF)
        self.dac2 = AD5667R(ArmorDef.DAC2_DEV_ADDR, dac_i2c, ArmorDef.DAC_VOLTAGE_REF)
        self.dac3 = MCP4725(ArmorDef.DAC3_DEV_ADDR, dac_i2c, ArmorDef.DAC3_VOLTAGE_REF)
        self.res1 = AD5272(ArmorDef.RES_1_ADDR, dac_i2c)
        self.res2 = AD5272(ArmorDef.RES_2_ADDR, dac_i2c)
        self.eeprom = CAT24C32(ArmorDef.EEPROM_DEV_ADDR, eeprom_i2c)
        self.sensor = NCT75(ArmorDef.SENSOR_DEV_ADDR, eeprom_i2c)
        self.pca9536 = PCA9536(ArmorDef.IO_EXP_DEV_ADDR, eeprom_i2c)
        self.dac_output_volt = dict()
        self.current_limit = dict()
        self.ocp_status = dict()
        self.eload_current = 0
        self.ocp_main_pin = ocp_main_pin
        self.ocp_batt_pin = ocp_batt_pin
        self.ocp_dbg_pin = ocp_dbg_pin

        super(ArmorBase, self).__init__(self.eeprom, self.sensor, range_table=armor_range_table)

    def post_power_on_init(self, timeout=ArmorDef.DEFAULT_TIMEOUT):
        '''
        Init Armor module to a know harware state.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        self.reset(timeout)

    def reset(self, timeout=ArmorDef.DEFAULT_TIMEOUT):
        '''
        Reset the instrument module to a know hardware state.

        This function will set pca9536 io direction to output and
        set the AD5667, MCP4725 and AD5272.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.

        '''
        start_time = time.time()

        while True:
            try:
                self.pca9536.set_pins_dir([ArmorDef.IO_SET])
                self.pca9536.set_ports([ArmorDef.IO_SET])
                self.dac1.select_work_mode(ArmorDef.DAC_CHANNEL['ALL'])
                self.dac1.set_reference("EXTERN")
                self.dac2.select_work_mode(ArmorDef.DAC_CHANNEL['ALL'])
                self.dac2.set_reference("EXTERN")
                self.res1.write_command(ArmorDef.RES_CMD_ADDR, ArmorDef.RES_CMD_DATA)
                self.res2.write_command(ArmorDef.RES_CMD_ADDR, ArmorDef.RES_CMD_DATA)
                self.res1.set_work_mode(ArmorDef.RES_WORK_MODE)
                self.res2.set_work_mode(ArmorDef.RES_WORK_MODE)
                self.set_current_limit("BATT", ArmorDef.BATT_CURR_LIMIT)
                self.set_current_limit("MAIN", ArmorDef.MAIN_CURR_LIMIT)
                self.set_current_limit("DBG", ArmorDef.DBG_CURR_LIMIT)
                self.eload_current = 0

                for channel in ArmorDef.DAC_CHANNEL_LIST:
                    self.ocp_status[channel] = 1
                    self.dac_output_volt[channel] = 0
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise ArmorException("Timeout: {}".format(e.message))

    def pre_power_down(self, timeout=ArmorDef.DEFAULT_TIMEOUT):
        '''
        Put the hardware in a safe state to be powered down.

        This function will set DAC to output 0 and set power board output disable.

        Args:
            timeout:      float, (>=0), default 1, unit Second, execute timeout.
        '''
        start_time = time.time()

        while True:
            try:
                self.dac1.output_volt_dc(ArmorDef.DAC_CHANNEL['A'], 0)
                self.dac1.output_volt_dc(ArmorDef.DAC_CHANNEL['B'], 0)
                self.dac2.output_volt_dc(ArmorDef.DAC_CHANNEL['A'], 0)
                self.dac2.output_volt_dc(ArmorDef.DAC_CHANNEL['B'], 0)
                self.pca9536.set_ports([ArmorDef.IO_SET])
                self.dac_output_volt.clear()
                self.current_limit.clear()
                self.ocp_status.clear()
                self.eload_current = 0
                return
            except Exception as e:
                if time.time() - start_time > timeout:
                    raise ArmorException("Timeout: {}".format(e.message))

    def get_driver_version(self):
        '''
        Get Armor driver version.

        Returns:
            string, current driver version.
        '''
        return __version__

    def set_current_limit(self, channel, threshold):
        '''
        Set current limit.

        Args:
            channel:        string,     ['BATT', 'MAIN', 'DBG'], select the armor board current limit source.
            threshold:      float/int,  [200~1500], set the source limit current,unit is mA,
                                        'BATT' limit current range is 200~1500 mA,
                                        'MAIN' limit current range is 200~600 mA,
                                        'DBG' limit current range is 200~600 mA.

        Returns:
            string, "done", api execution successful.

        Examples:
            armor.set_current_limit('BATT', 1000)

        '''
        assert channel in ArmorDef.DAC_CHANNEL_LIST
        assert isinstance(threshold, (int, float))
        assert CURR_LIMIT[channel](threshold)

        if "BATT" == channel:
            cal_item = "batt_limit"
        elif "MAIN" == channel:
            cal_item = "vddmain_limit"
        elif "DBG" == channel:
            cal_item = "ppvrect_limit"
        else:
            raise ArmorException("channel is error")

        dac_output = threshold / ArmorDef.UNIT_CONVERSION
        output = round(formula[cal_item](dac_output), 4)

        if cal_item == 'batt_limit':
            self.res1.set_resistor(output)
        elif cal_item == 'ppvrect_limit':
            output *= ArmorDef.UNIT_CONVERSION
            self.dac3.output_volt_dc(output)
        else:
            self.res2.set_resistor(output)

        self.current_limit[channel] = threshold

        return "done"

    def get_current_limit(self, channel):
        '''
        Get current limit.

        Args:
            channel:    string, ['BATT', 'MAIN', 'DBG'], select the armor board current limit source.

        Returns:
            int/float, back current limit, unit mA.

        Examples:
            armor.get_current_limit('BATT')

        '''
        assert channel in ArmorDef.DAC_CHANNEL_LIST

        return self.current_limit[channel]

    def write_output_voltage(self, channel, vout):
        '''
        Set and enable the voltage output.

        Args:
            channel:        string,     ['BATT', 'MAIN', 'DBG'], select output source.
            vout:           float/int,   [0~8000], set the source output voltage, unit is mV,
                                        'BATT' output range is 0~5000 mV,
                                        'DBG' output range is 0~8000 mV,
                                        'MAIN' output range is 0~5000 mV.

        Returns:
            string, "done", api execution successful.

        Examples:
            armor.write_output_voltage('BATT', 1000)

        '''
        assert channel in ArmorDef.DAC_CHANNEL_LIST
        assert isinstance(vout, (int, float))
        assert vout >= ArmorDef.DAC_RANGE_DICT[channel]["min"] and vout <= ArmorDef.DAC_RANGE_DICT[channel]["max"]

        if "BATT" == channel:
            cal_item = "batt"
            dac = self.dac1
            dac_channel = ArmorDef.DAC_CHANNEL['B']
        elif "MAIN" == channel:
            cal_item = "vddmain"
            dac = self.dac2
            dac_channel = ArmorDef.DAC_CHANNEL['A']
        elif "DBG" == channel:
            cal_item = "ppvrect"
            dac = self.dac2
            dac_channel = ArmorDef.DAC_CHANNEL['B']
        else:
            raise ArmorException("channel is error")

        output = self.calibrate(cal_item, vout)
        dac_output = round(formula[cal_item](output), 3)

        if ArmorDef.MAX_VOLTAGE < dac_output:
            dac_output = ArmorDef.MAX_VOLTAGE
        if ArmorDef.MIN_VOLTAGE > dac_output:
            dac_output = 0

        dac.output_volt_dc(dac_channel, dac_output)
        self.dac_output_volt[channel] = vout

        return "done"

    def get_output_voltage(self, channel):
        '''
        Get output voltage.

        Args:
            channel:    string, ['BATT', 'MAIN', 'DBG'], select output source.

        Returns:
            float/int, back output voltage value, unit mV.

        Examples:
            armor.get_output_voltage('BATT')

        '''
        assert channel in ArmorDef.DAC_CHANNEL_LIST

        return self.dac_output_volt[channel]

    def get_ocp_status(self, channel):
        '''
        Check OCP status.

        Args:
            channel:    string, ['BATT', 'MAIN', 'DBG'], select output source.

        Returns:
            int, ocp_status, 0/1, 1 means no OCP occurs, 0 means OCP occurred.

        Examples:
            armor.get_ocp_status('BATT')

        '''
        assert channel in ArmorDef.DAC_CHANNEL_LIST

        if "BATT" == channel:
            ocp_pin = self.ocp_batt_pin
        elif "MAIN" == channel:
            ocp_pin = self.ocp_main_pin
        elif "DBG" == channel:
            ocp_pin = self.ocp_dbg_pin
        else:
            raise ArmorException("channel is error")

        ocp_status = ocp_pin.get_level()
        self.ocp_status[channel] = ocp_status

        return ocp_status

    def set_clear_ocp(self, channel):
        '''
        Clear OCP status.

        Args:
            channel:    string, ['BATT', 'MAIN', 'DBG'], select output source.

        Returns:
            string, "done", api execution successful.

        Examples:
            armor.set_clear_ocp('BATT')

        '''
        assert channel in ArmorDef.DAC_CHANNEL_LIST

        self.ocp_status[channel] = 1

        return "done"

    def enable_output_voltage(self, channel):
        '''
        Enable voltage output.

        Args:
            channel:    string, ['BATT', 'MAIN', 'DBG'], select output source.

        Returns:
            string, "done", api execution successful.

        Examples:
            armor.enable_output_voltage('BATT')

        '''
        assert channel in ArmorDef.DAC_CHANNEL_LIST

        if 'BATT' == channel:
            pin = ArmorDef.BATT_PIN
        elif "MAIN" == channel:
            pin = ArmorDef.MAIN_PIN
        elif "DBG" == channel:
            pin = ArmorDef.RECT_PIN
        else:
            raise ArmorException("channel is error")

        self.pca9536.set_pin(pin, ArmorDef.ENABLE_LEVEL)

        return "done"

    def disable_output_voltage(self, channel):
        '''
        Disable voltage output.

        Args:
            channel:    string, ['BATT', 'MAIN', 'DBG'], select output source.

        Returns:
            string, "done", api execution successful.

        Examples:
            armor.disable_output_voltage('BATT')

        '''
        assert channel in ArmorDef.DAC_CHANNEL_LIST

        if 'BATT' == channel:
            pin = ArmorDef.BATT_PIN
        elif "MAIN" == channel:
            pin = ArmorDef.MAIN_PIN
        elif "DBG" == channel:
            pin = ArmorDef.RECT_PIN
        else:
            raise ArmorException("channel is error")

        self.pca9536.set_pin(pin, ArmorDef.DISABLE_LEVEL)

        return "done"

    def write_eload_current(self, load):
        '''
        Set and enable the e-load current.

        Args:
            load:    float/int, [0~500], unit mA.

        Returns:
            string, "done", api execution successful.

        Examples:
            armor.write_eload_current(500)

        '''
        assert isinstance(load, (int, float))
        assert load >= ArmorDef.DAC_RANGE_DICT["ELOAD"]["min"] and load <= ArmorDef.DAC_RANGE_DICT["ELOAD"]["max"]

        cal_item = 'eload'
        output = self.calibrate(cal_item, load)
        dac_output = round(formula[cal_item](output), 3)

        if ArmorDef.MAX_VOLTAGE < dac_output:
            dac_output = ArmorDef.MAX_VOLTAGE
        if ArmorDef.MIN_VOLTAGE > dac_output:
            dac_output = 0

        self.eload_current = dac_output

        return "done"

    def enable_eload(self):
        '''
        Enable eload current.

        Returns:
            string, "done", api execution successful.

        Examples:
            armor.enable_eload()

        '''
        self.dac1.output_volt_dc(ArmorDef.DAC_CHANNEL['A'], self.eload_current)

        return "done"

    def disable_eload(self):
        '''
        Disable eload current.

        Returns:
            string, "done", api execution successful.

        Examples:
            armor.disable_eload()

        '''
        self.dac1.output_volt_dc(ArmorDef.DAC_CHANNEL['A'], 0)

        return "done"

    def write_module_calibration(self, channel, calibration_vectors):
        '''
        Calculate module calibration and write to eeprom.

        Args:
            channel:    string, ['BATT', 'DBG', 'MAIN', 'ELOAD'], module range.
            calibration_vectors:    list, it contains value pairs of module raw reading
                                        and benchmark value got from external equipments.
                                        [[module_raw1, benchmark1], [module_raw2, benchmark2],
                                         ...,[module_rawN, benchmarkN]]
        Returns:
            string, "done", execute successfully.
        '''
        assert channel in ArmorDef.MODULE_RANGE_TABLE

        if "BATT" == channel:
            channel = "batt"
        elif "MAIN" == channel:
            channel = "vddmain"
        elif "DBG" == channel:
            channel = "ppvrect"
        elif "ELOAD" == channel:
            channel = "eload"
        else:
            raise ArmorException("channel is error")

        super(ArmorBase, self).write_module_calibration(channel, calibration_vectors)

        return "done"


class Armor(ArmorBase):
    '''
    Power009002 Module is used for output the voltage and set the current limit.

    compatible = ["GQQ-Q177-5-02A"]

    Armor(PWR-009) is a high performance digital power module.DAC has a 16-bit resolution, and it has four
    channels: channel 1 is the primary power supply, channel 2 is the standby power supply, channel
    3 is the battery simulation, and channel 4 is e-load, which supports CC mode.In addition, it also has
    over current protection, and the output current over current protection current size can be set.

    Args:
        dac_i2c:            instance(I2C),  which is used to control ad5667, ad5272 and mcp4725.
        eeprom_i2c:         instance(I2C),  which is used to control nct75, cat24c32 and pca9536.
        ocp_main_pin:       instance(Pin),  which is used to check 'MAIN' output source OCP status.
        ocp_batt_pin:       instance(Pin),  which is used to check 'BATT' output source OCP status.
        ocp_dbg_pin:        instance(Pin),  which is used to check 'DBG' output source OCP status.


    Examples:

    .. code-block:: python

        dac_i2c = I2C('/dev/i2c-3')
        eeprom_i2c = I2C('/dev/i2c-7')
        i2c = I2C('/dev/i2c-0')
        cat9555 = CAT9555(0x20, i2c)
        ocp_main_pin = Pin(cat9555, 0)
        ocp_batt_pin = Pin(cat9555, 1)
        ocp_dbg_pin = Pin(cat9555, 2)
        armor = Armor(dac_i2c, eeprom_i2c, ocp_main_pin, ocp_batt_pin, ocp_dbg_pin)

        # power board output the voltage
        result = armor.post_power_on_init()
        result = armor.write_output_voltage('BATT', 1000)
        armor.enable_output_voltage('BATT')
        set the source 'BATT' (A02) output 1000mV
        return 'done'

        # power board disable output the voltage
        result = armor.post_power_on_init()
        result = armor.disable_output_voltage('BATT')
        disable the source 'BATT' (A02) output
        return 'done'

        # power board set the over current protect
        result = armor.post_power_on_init()
        result = armor.set_current_limit('BATT', 1500)
        set the OCP
        return 'done'
    '''
    # launcher will use this to match driver compatible string and load driver if matched.
    compatible = ["GQQ-Q177-5-02A", "GQQ-Q177-5-020"]

    def __init__(self, dac_i2c=None, eeprom_i2c=None, ocp_main_pin=None, ocp_batt_pin=None, ocp_dbg_pin=None):

        super(Armor, self).__init__(dac_i2c, eeprom_i2c, ocp_main_pin, ocp_batt_pin, ocp_dbg_pin)
