# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import *
from mix.driver.core.bus.i2c import I2C
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.core.bus.gpio import GPIO
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_qspi_sg import MIXQSPISG
from mix.driver.smartgiant.luggage.module.uel001003a import UEL001003A

__author__ = 'xuboyan@SmartGiant'
__version__ = '1.1'


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


class UEL001003ADebuger(cmd.Cmd):
    prompt = 'uel001003a>'
    intro = 'Xavier uel001003a debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.uel001003a.module_init()
        print("Done.")

    @handle_errors
    def do_init_to(self, line):
        '''init_to <channel>
        <channel>: string, ["cc", "cv", "cr", "cr_c"]
        eg: init_to ["cc"] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.uel001003a.init_to(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_CC(self, line):
        '''set_CC <value>
        <value>: float, [0~5000], unit mA
        eg: set_CC [500] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.uel001003a.set_CC(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_CV(self, line):
        '''set_CV <value>
        <value>: float, [100~32000], unit mV
        eg: set_CV [6000] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.uel001003a.set_CV(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_set_CR(self, line):
        '''set_CR <value>
        <value>: float, [0.005~2048], unit ohm
        eg: set_CR [500] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.uel001003a.set_CR(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_curr(self, line):
        '''read_curr
        return: dict, {'raw_data': raw_data, 'current': current}, raw data and current value with unit.
        eg: read_curr '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.uel001003a.read_curr()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_volt(self, line):
        '''read_volt
        return: dict, {'raw_data': raw_data, 'voltage': voltage}, raw data and voltage value with unit.
        eg: read_volt '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.uel001003a.read_volt()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_local_temperature(self, line):
        '''read_local_temperature
        return: list, [value, unit], unit C
        eg: read_local_temperature '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.uel001003a.read_local_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_remote_temperature(self, line):
        '''read_remote_temperature
        return: list, [value, unit], unit C
        eg: read_remote_temperature '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.uel001003a.read_remote_temperature()
        print("Result:")
        print(result)

    @handle_errors
    def do_write_CRoffset(self, line):
        '''write_CRoffset <offset>
        <offset>: float
        eg: write_CRoffset [500.0] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.uel001003a.write_CRoffset(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_CRoffset(self, line):
        '''read_CRoffset
        return: float
        eg: read_CRoffset '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.uel001003a.read_CRoffset()
        print("Result:")
        print(result)

    @handle_errors
    def do_usb_connect_set(self, line):
        '''usb_connect_set <status>
        <status>:       string, ["enable", "disable"]
        eg: usb_connect_set ["enable"] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.uel001003a.usb_connect_set(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_write_calibration(self, line):
        '''write_calibration <cal_item> <level> <gain> <offset>
        <cal_item>:     string, ["read_volt", "read_curr", "set_CV", "set_CC", "set_CR"]
        <level>:        int, calibration level index
        <gain>:         float, when gain is read here, it will automatically increase by 1.
                               So, when you want to set the gain to 1, you should write 0.
        <offset>:       float
        eg: write_calibration ["set_CC",1,0,1.25] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.uel001003a.write_calibration(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_calibration(self, line):
        '''read_calibration <cal_item> <level>
        <cal_item>:     string, ["read_volt", "read_curr", "set_CV", "set_CC", "set_CR"]
        <level>:        int, calibration level index
        eg: read_calibration ["set_CC",1] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        result = self.uel001003a.read_calibration(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_erase_calibration(self, line):
        '''erase_calibration <cal_item> <level>
        <cal_item>:     string, ["read_volt", "read_curr", "set_CV", "set_CC", "set_CR"]
        <level>:        int, calibration level index
        eg: erase_calibration ["set_CC",1] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        self.uel001003a.erase_calibration(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_write_eeprom(self, line):
        '''write_eeprom addr <address> <data_list>
        <address>: hex, [0~0xFFFF], eeprom memeroy address.
        <data_list>: int, element for byte data, which you want to write into eeprom.
        eg: write_eeprom [0x278,[0x01,0x20,0x05]] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.uel001003a.write_eeprom(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_eeprom(self, line):
        '''read_eeprom <address> <count>
        <address>: hex, [0~0xFFFF], eeprom memory address.
        <count>: int, [0~1024], Count of datas to be read.
        eg: read_eeprom [0x278,5] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        result = self.uel001003a.read_eeprom(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_eeprom_write_string(self, line):
        '''do_eeprom_write_string addr <addr> <data>
        <addr>: int, [0~], the address to write string.
        <data>: string, the string data to be write.
        eg: do_eeprom_write_string [0x278,"abc"] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        self.uel001003a.eeprom_write_string(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_eeprom_read_string(self, line):
        '''eeprom_read_string <addr> <rd_len>
        <addr>: int, [0~], the address to read data.
        <rd_len>: int, [0~], length of data to be read.
        eg: eeprom_read_string [0x278,3] '''
        if '?' == line:
            print(get_function_doc(self))
            return None

        line = line.replace(' ', ',')
        result = self.uel001003a.eeprom_read_string(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_get_calibration_mode(self, line):
        '''get_calibration_mode
        return: str, ["raw", "cal"]
        eg: get_calibration_mode '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.uel001003a.get_calibration_mode()
        print(result)

    @handle_errors
    def do_set_calibration_mode(self, line):
        '''set_calibration_mode <mode>
        mode: str, ["raw", "cal"]
        eg: set_calibration_mode ["raw"]'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.uel001003a.set_calibration_mode(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit
        Exit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help
        Usage'''
        print('Usage:')
        for name, attr in inspect.getmembers(self):
            if 'do_' in name:
                print(attr.__doc__)


def create_uel001003a_dbg(i2c_bus_name, spi_bus_name, gpio_device_name, switch_pin_id):
    uel001003a_dbg = UEL001003ADebuger()

    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)

    if spi_bus_name == '':
        spi_bus_name = None
    else:
        axi4_bus = AXI4LiteBus(spi_bus_name, 8192)
        spi_bus = MIXQSPISG(axi4_bus)

    if gpio_device_name == '':
        gpio_switch = GPIO(int(switch_pin_id), "output")
    else:
        axi4_bus = AXI4LiteBus(gpio_device_name, 256)
        gpio = MIXGPIOSG(axi4_bus)
        gpio_switch = Pin(gpio, int(switch_pin_id))

    uel001003a_dbg.uel001003a = UEL001003A(i2c=i2c_bus, spi=spi_bus, gpio_switch=gpio_switch)

    return uel001003a_dbg


arguments = [
    ['-i2c', '--i2c', 'i2c bus name for uel001003a', '/dev/i2c-0'],
    ['-spi', '--spi', 'spi bus name for uel001003a', '/dev/MIX_QSPI_0'],
    ['-gd', '--gd', 'gpio device name', ''],
    ['-gpio_switch', '--gpio_switch', 'switch pin id', 86],
]


if __name__ == '__main__':
    '''
    python uel001003a_tool.py
    '''

    parser = argparse.ArgumentParser()
    for arg in arguments:
        parser.add_argument(arg[0], arg[1], help=arg[2], default=arg[3])

    args = parser.parse_args()
    uel001003a_dbg = create_uel001003a_dbg(args.i2c, args.spi, args.gd, args.gpio_switch)
    uel001003a_dbg.cmdloop()
