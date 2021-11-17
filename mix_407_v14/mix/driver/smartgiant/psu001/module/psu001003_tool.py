# -*- coding: utf-8 -*-

import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import *
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.psu001.module.psu001003 import PSU001003

__author__ = 'Zili.Li@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class Psu001003Debugger(cmd.Cmd):
    prompt = 'psu001003>'
    intro = 'MIX psu001003 debug tool'

    @handle_errors
    def do_module_init(self, line):
        '''module_init'''
        self.psu.module_init()
        print("Done.")

    @handle_errors
    def do_reset(self, line):
        '''reset
        Reset hardware circuit when over-current or over-voltage.'''
        self.psu.reset()
        print("Done.")

    @handle_errors
    def do_output_enable(self, channel):
        '''output_enable
        Enable channel output
        eg: output_enable 'VBATT' '''
        self.psu.output_enable(channel)
        print("Done.")

    @handle_errors
    def do_output_disable(self, channel):
        '''output_disable
        Disable channel output
        eg: output_disable 'VBATT' '''

        self.psu.output_disable(channel)
        print("Done.")

    @handle_errors
    def do_gain_set(self, line):
        '''gain_set
        Set gain value
        eg: gain_set 'VBUS',10 '''

        self.psu.gain_set(line.split()[0], int(line.split()[1]))
        print("Done.")

    @handle_errors
    def do_quit(self, line):
        '''quit
        Exit'''
        return True

    def do_help(self, line):
        '''help
        '''
        print('Usage:')
        print(self.do_module_init.__doc__)
        print(self.do_reset.__doc__)
        print(self.do_output_enable.__doc__)
        print(self.do_output_disable.__doc__)
        print(self.do_gain_set.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_psu001003_dbg(i2c_bus_name):
    psu001003_dbg = Psu001003Debugger()
    if i2c_bus_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(i2c_bus_name):
            axi4_bus = AXI4LiteBus(i2c_bus_name, 256)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(i2c_bus_name)
    psu001003_dbg.psu = PSU001003(i2c_bus)
    psu001003_dbg.psu.board_init()
    return psu001003_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default="")
    args = parser.parse_args()
    psu001003_dbg = create_psu001003_dbg(args.device)
    psu001003_dbg.cmdloop()
