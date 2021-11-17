# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from tmp10x import TMP108
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef


__author__ = 'huangzicheng@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class TMP108Debuger(cmd.Cmd):
    prompt = 'TMP108>'
    intro = 'Xavier tmp108 debug tool'

    @handle_errors
    def do_write_register(self, line):
        '''write_register addr [data1,data2]'''
        line = line.replace(' ', ',')
        self.tmp108.write_register(*list(eval(line)))
        print('Done')

    @handle_errors
    def do_read_register(self, line):
        '''read_register addr length'''
        line = line.replace(' ', ',')
        ret = self.tmp108.read_register(*list(eval(line)))
        print(ret)

    @handle_errors
    def do_get_temperature(self, line):
        '''get_temperature'''
        ret = self.tmp108.get_temperature()
        print(ret)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_write_register.__doc__)
        print(self.do_read_register.__doc__)
        print(self.do_get_temperature.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_tmp108_dbg(dev_name, dev_addr):
    tmp108_dbg = TMP108Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    tmp108_dbg.tmp108 = TMP108(dev_addr, i2c_bus)
    return tmp108_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address',
                        help='device address', default='0x48')
    args = parser.parse_args()
    tmp108_dbg = create_tmp108_dbg(args.device, int(args.address, 16))

    tmp108_dbg.cmdloop()
