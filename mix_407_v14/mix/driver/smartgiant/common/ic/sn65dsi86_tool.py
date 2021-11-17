# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.core.utility import utility
from mix.driver.smartgiant.commong.ic.sn65dsi86 import SN65DSI86
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef

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


class SN65DSI86Debuger(cmd.Cmd):
    prompt = 'sn65dsi86>'
    intro = 'Xavier sn65dsi86 debug tool'

    def do_write_register(self, line):
        '''write_register [reg_addr] [wr_data] eg:0x01 [0x12,0x23]'''
        line = line.replace(' ', ',')
        self.sn65dsi86.write_register(*list(eval(line)))
        print("Done.")

    def do_read_register(self, line):
        '''read_register [addr] [rd_len] eg: read_register 0x01 2'''
        line = line.replace(' ', ',')
        result = self.sn65dsi86.read_register(*list(eval(line)))
        print("Result:")
        print(result)

    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print("Usage:")
        print(self.do_write_register.__doc__)
        print(self.do_read_register.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_sn65_dbg(dev_name, dev_addr):
    sn65dbg = SN65DSI86Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    sn65dbg.sn65dsi86 = SN65DSI86(dev_addr, i2c_bus)
    return sn65dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x2c')
    args = parser.parse_args()

    sn65dbg = create_sn65_dbg(args.device, int(args.address, 16))

    sn65dbg.cmdloop()
