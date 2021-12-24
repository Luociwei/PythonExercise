# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.armor.module.armor import Armor
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.utility import utility

__author__ = 'zicheng.huang@SmartGiant'
__version__ = '0.1'


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
    def do_module_init(self, line):
        '''module_init
        Need to call it once after module instance is created'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.module_init()
        print("Done.")

    @handle_errors
    def do_power_output(self, line):
        '''power_output
        Armor dac output
            channel:        string('vddmain', 'ppvrect', 'batt', 'eload'), select output source.
            output:         int/float([0, 8000], Range value, vddmain output range is (0-5000mV),
                                      ppvrect output range is (0-8000mV),
                                      batt    output range is (0-5000mV),
                                      eload   output range is (0-500mA).)
            eg:             power_output 'batt' 1000'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.armor.power_output(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_power_enable(self, line):
        '''power_enable
        Enable Armor power output
        channel:    string('vddmain', 'ppvrect', 'batt', 'eload'), select output source.
        eg: power_disable 'batt' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.power_enable(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_power_disable(self, line):
        '''power_disable channel
        Disable Armor power output
        channel:    string('vddmain', 'ppvrect', 'batt', 'eload'), select output source.
        eg: power_disable 'batt' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.power_disable(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_power_curr_readback(self, line):
        '''power_curr_readback
        Armor adc readback current
            channel:        string('vddmain', 'ppvrect', 'batt', 'eload'),
                            select output source.
            voltage:        float/int([-6500~6500], Range value, vddmain voltage range is (0-6500mV),
                                        ppvrect voltage range is (0-6500mV),
                                        batt    voltage range is ((-6500)-6500mV),
                                        eload   voltage range is (0-6500mV).)
            eg:             power_curr_readback 'vddmain' 1000'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.armor.power_curr_readback(*list(eval(line)))
        print("%f" % result)

    @handle_errors
    def do_resistor_set(self, line):
        '''resistor_set
        Armor resistor set
            channel:    string('batt', 'vddmain', 'ppvrect'), select the armor board current limit source.
            limit:      float/int(0~1200), set the source limit current,unit is mA, batt limit current range is
                                  0-1200mA,vddmain limit current range is 0-500mA, ppvrect limit current range is
                                  0-500mA,
        eg: resistor_set 'batt' 500 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.armor.resistor_set(*list(eval(line)))
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
    def do_write_calibration_cell(self, line):
        '''write_calibration_cell unit_index gain offset threshold
        MIXBoard calibration data write
        unit_index:   int,    calibration unit index
        gain:         float,  calibration gain
        offset:       float,  calibration offset
        threshold:    float,  if value < threshold,
                            use this calibration unit data
        eg: write_calibration_cell 0,1.1,0.1,100 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.armor.legacy_write_calibration_cell(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_calibration_cell(self, line):
        '''read_calibration_cell
        MIXBoard read calibration data
        unit_index: int, calibration unit index
        eg: read_calibration_cell 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.legacy_read_calibration_cell(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_erase_calibration_cell(self, line):
        '''erase_calibration_cell
        MIXBoard erase calibration unit
        unit_index: int, calibration unit index
        eg: erase_calibration_cell 1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.armor.legacy_erase_calibration_cell(*list(eval(line)))
        print("Done.")

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
    def do_is_use_cal_data(self, line):
        '''is_use_cal_data
        Armor query calibration mode if is enabled'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.armor.is_use_cal_data()
        print('Result:')
        print(result)

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
