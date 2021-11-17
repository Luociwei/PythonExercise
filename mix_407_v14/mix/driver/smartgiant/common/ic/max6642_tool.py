# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
import inspect
from functools import wraps
from mix.driver.smartgiant.common.ic.max6642 import MAX6642
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef


__author__ = 'weiping.mo@SmartGiant'
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


class MAX6642Debuger(cmd.Cmd):
    prompt = 'max6642>'
    intro = 'Xavier max6642 debug tool, Type help or ? to list commands.\n'

    @handle_errors
    def do_get_temperature(self, line):
        '''get_temperature
        MAX6642 read local or remote temperature
        channel:  	string('local','remote')
        extended: 	boolean(True,False)
        eg: 		get_temperature 'local',True '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        result = self.max6642.get_temperature(*list(eval(line)))
        print("Result:")
        print(result)

    @handle_errors
    def do_write_high_limit(self, line):
        '''write_high_limit
        MAX6642 write local or remote high limit
        channel:  	string('local','remote')
        limit:      int(0-255)
        eg: 		write_high_limit 'local',75 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.max6642.write_high_limit(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_write_config(self, line):
        '''write_config
        MAX6642 write configuration_byte bit
        config_bit: string('mask_alert','stop','external_only','fault_queue')
        bit_val:   	int(0/1), bit value
        eg: 		write_config 'mask_alert',1 '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        line = line.replace(' ', ',')
        self.max6642.write_config(*list(eval(line)))
        print("Done.")

    @handle_errors
    def do_read_high_limit(self, line):
        '''read_high_limit
        MAX6642 read local or remote high limit
        channel:  	string('local','remote')
        eg: 		read_high_limit 'local' '''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.max6642.read_high_limit(eval(line))
        print("Result:")
        print(result)

    @handle_errors
    def do_manufacturer_id(self, line):
        '''manufacturer_id
        MAX6642 read manufacturer ID(4Dh)'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.max6642.manufacturer_id()
        print("Result:")
        print(result)

    @handle_errors
    def do_single_shot(self, line):
        '''single_shot
        MAX6642 single-shot command'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        self.max6642.single_shot()
        print("Done.")

    @handle_errors
    def do_read_state(self, line):
        '''read_state
        MAX6642 read status byte'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.max6642.read_state()
        print("Result:")
        print(result)

    @handle_errors
    def do_read_config(self, line):
        '''read_config
        MAX6642 read configuration_byte'''
        if '?' == line:
            print(get_function_doc(self))
            return None
        result = self.max6642.read_config()
        print("Result:")
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


def create_max6642_dbg(dev_name, dev_addr):
    max6642_dbg = MAX6642Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    max6642_dbg.max6642 = MAX6642(dev_addr, i2c_bus)
    return max6642_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x48')
    args = parser.parse_args()
    max6642_dbg = create_max6642_dbg(args.device, int(args.address, 16))

    max6642_dbg.cmdloop()
