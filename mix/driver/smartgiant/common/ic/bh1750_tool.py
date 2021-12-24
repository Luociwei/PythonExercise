# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ic.bh1750 import BH1750
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
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


class BH1750Debuger(cmd.Cmd):
    prompt = 'bh1750>'
    intro = 'Xavier bh1750 debug tool'

    @handle_errors
    def do_get_intensity(self, line):
        '''get_intensity'''
        result = self.bh1750.get_intensity()
        print('Result:')
        print(result)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_get_intensity.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_bh1750_dbg(dev_name, dev_addr):
    bh1750_dbg = BH1750Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    bh1750_dbg.bh1750 = BH1750(dev_addr, i2c_bus)
    return bh1750_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x23')
    args = parser.parse_args()
    bh1750_dbg = create_bh1750_dbg(args.device, int(args.address, 16))

    bh1750_dbg.cmdloop()
