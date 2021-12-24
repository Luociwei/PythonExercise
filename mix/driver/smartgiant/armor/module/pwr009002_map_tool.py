# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.armor.module.pwr009002_map import Armor
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.utility import utility

__author__ = 'zicheng.huang@SmartGiant'
__version__ = 'V0.1.5'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


def get_function_doc(self=None):
    '''Get function.__doc__ '''
    func_name = inspect.stack()[1][3]
    if self is None:
        return eval('%s' % func_name).__doc__
    else:
        return getattr(self, func_name).__doc__


class ArmorDebuger(cmd.Cmd):
    prompt = 'Armor>'
    intro = 'Xavier Armor debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_post_power_on_init(self, line):
        '''post_power_on_init timeout
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.post_power_on_init(eval(line))
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset timeout
        Armor reset the instrument module to a know hardware state.
        eg:           reset
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.reset(eval(line))
        print("Done.")

    @handle_errors
    def do_pre_power_down(self, line):
        '''pre_power_down timeout'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.pre_power_down(eval(line))
        print("Done.")

    @handle_errors
    def do_get_driver_version(self, line):
        '''get_driver_version
        Get Armor driver version.
        eg.         get_driver_version
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.get_driver_version()
        print("Result:")
        print(result)

    @handle_errors
    def do_set_current_limit(self, line):
        '''set_current_limit
        Set current limit.
            channel:    string('MAIN', 'DBG', 'BATT'), select output source.
            threshold:      float/int,  [0~1200], set the source limit current,unit is mA,
                                        'BATT' limit current range is 10~1500 mA,
                                        'MAIN' limit current range is 10~500 mA,
                                        'DBG' limit current range is 10~500 mA.
        eg.        do_set_current_limit 'BATT' 1500
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.armor.set_current_limit(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_current_limit(self, line):
        '''get_current_limit
        Get current limit.
            channel:    string('MAIN', 'DBG', 'BATT'), select output source.
        eg.        do_get_current_limit 'BATT'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.get_current_limit(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_write_output_voltage(self, line):
        '''write_output_voltage
        Set and enable the voltage output.
            channel:        string,     ['BATT', 'MAIN', 'DBG'], select output source.
            vout:           float/int,   [-30.6~8000], set the source output voltage, unit is mV,
                                        'BATT' output range is -30.6~5495 mV,
                                        'DBG' output range is -30.6~8000 mV,
                                        'MAIN' output range is -30.6~5495 mV.
        eg.        do_write_output_voltage 'BATT' 1500
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.armor.write_output_voltage(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_get_output_voltage(self, line):
        '''get_output_voltage
        Get output voltage.
            channel:    string('MAIN', 'DBG', 'BATT'), select output source.
        eg.        do_get_output_voltage 'BATT'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.get_output_voltage(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_get_ocp_status(self, line):
        '''get_ocp_status
        Check OCP status.
            channel:    string('MAIN', 'DBG', 'BATT'), select output source.
        eg.        do_get_ocp_status 'BATT'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.get_ocp_status(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_set_clear_ocp(self, line):
        '''set_clear_ocp
        Clear OCP status.
            channel:        string,     ['BATT', 'MAIN', 'DBG'], select output source.
        eg.        do_set_clear_ocp 'BATT'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.set_clear_ocp(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_enable_output_voltage(self, line):
        '''enable_output_voltage
        Enable voltage output.
            channel:        string,     ['BATT', 'MAIN', 'DBG'], select output source.
        eg.        do_enable_output_voltage 'BATT'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.enable_output_voltage(eval(line))
        print("Done.")

    @handle_errors
    def do_disable_output_voltage(self, line):
        '''disable_output_voltage
        Disable voltage output.
            channel:        string,     ['BATT', 'MAIN', 'DBG'], select output source.
        eg.        do_disable_output_voltage 'BATT'
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.disable_output_voltage(eval(line))
        print("Done.")

    @handle_errors
    def do_write_eload_current(self, line):
        '''write_eload_current
        Set and enable the e-load current.
            load:    float/int, [0~500], unit mA.
        eg.        do_write_eload_current 400
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.write_eload_current(eval(line))
        print("Done.")

    @handle_errors
    def do_enable_eload(self, line):
        '''enable_eload
        Enable eload current.
        eg.        do_enable_eload
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.enable_eload()
        print("Done.")

    @handle_errors
    def do_disable_eload(self, line):
        '''disable_eload
        Enable eload current.
        eg.        do_disable_eload
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.disable_eload()
        print("Done.")

    @handle_errors
    def do_write_module_calibration(self, line):
        '''write_module_calibration
        Calculate module calibration and write to eeprom.
        eg.        do_write_module_calibration BATT [[100, 101.2], ...]
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.armor.write_module_calibration(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_temperature(self, line):
        '''temperature
        Armor read temperature from sensor
        '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.get_temperature()
        print("%f" % result)

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode
        Armor enable calibration mode
        mode: str("raw", "cal")
        eg: set_calibration_mode "raw"'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.set_calibration_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_get_calibration_mode(self, line):
        '''get_calibration_mode
        Armor get calibration mode
        eg: get_calibration_mode'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.get_calibration_mode()
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit
        Exit'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        return True

    @handle_errors
    def do_help(self, line):
        '''help
        Usage'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_armor_dbg(dac_i2c_bus_name, eeprom_i2c_bus_name):
    armor_dbg = ArmorDebuger()

    if dac_i2c_bus_name == '':
        dac_i2c_bus = None
    else:
        if utility.is_pl_device(dac_i2c_bus_name):
            axi4_bus = AXI4LiteBus(dac_i2c_bus_name, 256)
            dac_i2c_bus = MIXI2CSG(axi4_bus)
        else:
            dac_i2c_bus = I2C(dac_i2c_bus_name)

    if eeprom_i2c_bus_name == '':
        eeprom_i2c_bus = None
    else:
        if utility.is_pl_device(eeprom_i2c_bus_name):
            axi4_bus = AXI4LiteBus(eeprom_i2c_bus_name, 256)
            eeprom_i2c_bus = MIXI2CSG(axi4_bus)
        else:
            eeprom_i2c_bus = I2C(eeprom_i2c_bus_name)

    armor_dbg.armor = Armor(dac_i2c_bus, eeprom_i2c_bus)
    return armor_dbg


if __name__ == '__main__':
    '''
    ***setup:
        module_init
    ***enable output power step:
        1.power_output 'batt' 1000
        2.power_enable 'batt'
    ***set the resistor limit step:
        1.resistor_set 'vddmain' 300
    ***when you control the power must be module init first.
    '''

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dac_i2c', help='dac i2c bus name',
                        default='/dev/i2c-7')
    parser.add_argument('-e', '--eeprom_i2c', help='eeprom i2c bus name',
                        default='/dev/i2c-4')

    args = parser.parse_args()
    armor_dbg = create_armor_dbg(args.dac_i2c, args.eeprom_i2c)

    armor_dbg.cmdloop()
