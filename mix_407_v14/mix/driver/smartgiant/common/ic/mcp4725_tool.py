# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef
from mix.driver.smartgiant.common.ic.mcp4725 import MCP4725
from mix.driver.core.utility import utility
from mix.driver.smartgiant.common.bus.axi4_lite_bus import AXI4LiteBus

__author__ = 'jingyong.xiao@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class MCP4725Debuger(cmd.Cmd):
    prompt = 'mcp4725>'
    intro = 'Xavier mcp4725 debug tool'

    @handle_errors
    def do_output_volt(self, line):
        '''output_volt [voltage]'''
        line = line.replace(' ', ',')
        data = self.mcp4725.output_volt_dc(eval(line))
        print('Done.')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print(self.do_output_volt.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_mcp4725_dbg(dev_name, device_address):
    mcp4725_dbg = MCP4725Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    mcp4725_dbg.mcp4725 = MCP4725(device_address, i2c_bus)
    return mcp4725_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x60')
    args = parser.parse_args()

    mcp4725_dbg = create_mcp4725_dbg(args.device, int(args.address, 0))

    mcp4725_dbg.cmdloop()
