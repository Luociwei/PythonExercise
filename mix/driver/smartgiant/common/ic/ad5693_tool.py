# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from ad5693 import AD5693
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.bus.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef


__author__ = 'chenfeng@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class AD5693Debuger(cmd.Cmd):
    prompt = 'ad5693>'
    intro = 'Xavier ad5693 debug tool'

    @handle_errors
    def do_output_volt_dc(self, line):
        '''output_volt_dc [channel] [volt]'''
        line = line.replace(' ', ',')
        self.ad5693.output_volt_dc(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_output_volt_dc.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_ad5693_dbg(dev_name, dev_addr):
    ad5693_dbg = AD5693Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    ad5693_dbg.ad5693 = AD5693(dev_addr, i2c_bus)
    return ad5693_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x4C')
    args = parser.parse_args()
    ad5693_dbg = create_ad5693_dbg(args.device, int(args.address, 16))

    ad5693_dbg.cmdloop()
