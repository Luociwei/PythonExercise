# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_gpio_sg import MIXGPIOSG
from mix.driver.core.bus.axi4_lite_def import PLGPIODef
from mix.driver.smartgiant.common.ic.dm634 import DM634
from mix.driver.smartgiant.common.ic.dm634 import DM634Def

__author__ = 'yuanle@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class DM634Debuger(cmd.Cmd):
    prompt = 'dm634>'
    intro = 'Xavier dm634 debug tool'

    @handle_errors
    def do_set_mode(self, line):
        '''set_mode [gck|normal]'''
        self.dm634.set_mode(eval(line))
        print('Done.')

    @handle_errors
    def do_get_mode(self, line):
        '''get_mode'''
        result = self.dm634.get_mode()
        print('Result:')
        print(result)

    @handle_errors
    def do_set_chs(self, line):
        '''set_chs [(chX,valueY),...]'''
        line = line.replace(' ', ',')
        self.dm634.set_channels(eval(line))
        print('Done.')

    @handle_errors
    def do_set_all(self, line):
        '''set_all [brightness]'''
        self.dm634.set_all_channel_brightness(eval(line))
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_set_mode.__doc__)
        print(self.do_get_mode.__doc__)
        print(self.do_set_chs.__doc__)
        print(self.do_set_all.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_dm634_dbg(axi4_dev_name, gpio_dev_name, gpio_id):
    dm634_dbg = DM634Debuger()
    if axi4_dev_name == '':
        axi4_bus = None
    else:
        axi4_bus = AXI4LiteBus(axi4_dev_name, DM634Def.REG_SIZE)

    if gpio_dev_name == '':
        gpio_dev = None
    else:
        axi4_gpio = AXI4LiteBus(gpio_dev_name, PLGPIODef.REG_SIZE)
        gpio_dev = MIXGPIOSG(axi4_gpio)
    dm634_dbg.dm634 = DM634(axi4_bus, gpio_dev, gpio_id)
    return dm634_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d1', '--axi4', help='axi4 device file name', default='')
    parser.add_argument('-d2', '--gpio', help='gpio device file name', default='')
    parser.add_argument('-p', '--pin', help='gpio pin number', default='0')

    args = parser.parse_args()

    dm634_dbg = create_dm634_dbg(args.axi4, args.gpio, int(args.pin))

    dm634_dbg.cmdloop()
