# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from cat24cxx import CAT24C32
from ..utility import utility
from ..bus.axi4_lite_bus import AXI4LiteBus
from ..bus.pl_i2c_bus import PLI2CBus
from ..bus.i2c import I2C
from ..bus.axi4_lite_def import PLI2CDef


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class CAT24C32Debuger(cmd.Cmd):
    prompt = 'cat24c32>'
    intro = 'xavier cat24c32 debug tool'

    @handle_errors
    def do_read(self, line):
        '''read [address] [length] eg: 0x01 2'''
        line = line.replace(' ', ',')
        rd_data = self.cat24c32.read(*list(eval(line)))
        print (rd_data)

    @handle_errors
    def do_write(self, line):
        '''write [address] [data_list] eg: 0x01 [0xff, 0xff]'''
        line = line.replace(' ', ',')
        self.cat24c32.write(*list(eval(line)))
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_read.__doc__)
        print(self.do_write.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_cat24c32_dbg(device_name, device_addr):
    cat24c32_dbg = CAT24C32Debuger()
    if device_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(device_name):
            axi4_bus = AXI4LiteBus(device_name, PLI2CDef.REG_SIZE)
            i2c_bus = PLI2CBus(axi4_bus)
        else:
            i2c_bus = I2C(device_name)
    cat24c32_dbg.cat24c32 = CAT24C32(device_addr, i2c_bus)
    return cat24c32_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x50')
    args = parser.parse_args()
    cat24c32_dbg = create_cat24c32_dbg(args.device, int(args.address, 16))

    cat24c32_dbg.cmdloop()
