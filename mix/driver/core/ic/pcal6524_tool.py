# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.bus.pl_i2c_bus import PLI2CBus
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.smartgiant.common.ic.pcal6524 import PCAL6524
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'jiasheng@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class PCAL6524Debuger(cmd.Cmd):
    prompt = 'pcal6524>'
    intro = 'Xavier pcal6524 debug tool'

    @handle_errors
    def do_read_register(self, line):
        '''read_register device_address rd_len'''
        line = line.replace(' ', ',')
        data = self.pcal6524.read_register(*list(eval(line)))
        print('Result:')
        print(data)
        return

    @handle_errors
    def do_write_register(self, line):
        '''write_register register_address [data]'''
        line = line.replace(' ', ',')
        self.pcal6524.write_register(*list(eval(line)))
        print('Done.')
        return

    @handle_errors
    def do_reset(self, line):
        '''reset'''
        self.pcal6524.reset_chip()
        print('Done.')
        return

    @handle_errors
    def do_get_pins_dir(self, line):
        '''get_pins_dir [pin_id,pin_id,...]'''
        result = self.pcal6524.get_pins_dir(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_pins_dir(self, line):
        '''set_pins_dir [[pin_id,level],...]'''
        self.pcal6524.set_pins_dir(eval(line))
        print('Done.')
        return

    @handle_errors
    def do_get_pins(self, line):
        '''get_pins [pin_id,...]'''
        result = self.pcal6524.get_pins_state(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_pins(self, line):
        '''set_pins [[pin_id,level],...]'''
        self.pcal6524.set_pins_state(eval(line))
        print('Done.')
        return

    @handle_errors
    def do_set_pull_up_or_down(self, line):
        '''set_pull_up_or_down [[pin_id,mode],...]'''
        self.pcal6524.set_pull_up_or_down(eval(line))
        print('Done.')
        return

    @handle_errors
    def do_get_pull_up_or_down(self, line):
        '''get_pull_up_or_down [pin_id,...]'''
        result = self.pcal6524.get_pull_up_or_down_state(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_set_pins_mode(self, line):
        '''set_pins_mode [[pin_id,mode],...]'''
        self.pcal6524.set_pins_mode(eval(line))
        print('Done.')
        return

    @handle_errors
    def do_get_pins_mode(self, line):
        '''get_pins_mode [pin_id,...]'''
        result = self.pcal6524.get_get_pins_mode(eval(line))
        print('Result:')
        print(result)
        return

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        print("Usage:")
        print(self.do_read_register.__doc__)
        print(self.do_write_register.__doc__)
        print(self.do_reset.__doc__)
        print(self.do_get_pins_dir.__doc__)
        print(self.do_set_pins_dir.__doc__)
        print(self.do_get_pins.__doc__)
        print(self.do_set_pins.__doc__)
        print(self.do_set_pull_up_or_down.__doc__)
        print(self.do_get_pull_up_or_down.__doc__)
        print(self.do_set_pins_mode.__doc__)
        print(self.do_get_pins_mode.__doc__)
        print(self.do_quit.__doc__)


def create_pcal6524_dbg(dev_name, device_address):
    pcal6524_dbg = PCAL6524Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = PLI2CBus(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    pcal6524_dbg.pcal6524 = PCAL6524(device_address, i2c_bus)
    return pcal6524_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x20')
    args = parser.parse_args()

    pcal6524_dbg = create_pcal6524_dbg(args.device, int(args.address, 16))

    pcal6524_dbg.cmdloop()
