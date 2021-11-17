# -*- coding:utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from mix.driver.smartgiant.common.ic.adg2128 import ADG2128
from mix.driver.core.utility import utility
from mix.driver.core.bus.axi4_lite_bus import AXI4LiteBus
from mix.driver.smartgiant.common.ipcore.mix_i2c_sg import MIXI2CSG
from mix.driver.core.bus.i2c import I2C
from mix.driver.core.bus.axi4_lite_def import PLI2CDef


__author__ = 'zijian.xu@SmartGiant'
__version__ = '0.1'


def handle_errors(func):
    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(e.message, os.linesep, traceback.format_exc())
    return wrapper_func


class ADG2128Debuger(cmd.Cmd):
    prompt = 'adg2128>'
    intro = 'Xavier adg2128 debug tool'

    @handle_errors
    def do_write_register(self, line):
        '''write_register [addr] [data] eg: 0x01 0xffff'''
        line = line.replace(' ', ',')
        self.adg2128.write_register(*list(eval(line)))
        print("Done")

    @handle_errors
    def do_read_register(self, line):
        '''read_register [addr] [len] eg: 0x01 2'''
        line = line.replace(' ', ',')
        rd_data = self.adg2128.read_register(*list(eval(line)))
        print('Result:')
        print(rd_data)

    @handle_errors
    def do_set_xy_state(self, line):
        '''set_xy_state [switch_val] eg: [[1,2,0], [3,4,1]]'''
        self.adg2128.set_xy_state((eval(line)))
        print("Done")

    @handle_errors
    def do_get_xy_state(self, line):
        '''get_xy_state [switch_val] eg: [[1,2], [3,4]]'''
        line = line.replace(' ', ',')
        rd_data = self.adg2128.get_xy_state(eval(line))
        print('Result:')
        print(rd_data)

    @handle_errors
    def do_connect(self, line):
        '''connect x y eg: 1 2'''
        line = line.replace(' ', ',')
        self.adg2128.connect(*eval(line))
        print("Done")

    @handle_errors
    def do_disconnect(self, line):
        '''disconnect x y eg: 1 2'''
        line = line.replace(' ', ',')
        self.adg2128.disconnect(*eval(line))
        print("Done")

    @handle_errors
    def do_is_connect(self, line):
        '''is_connect x y eg: 1 2'''
        line = line.replace(' ', ',')
        ret = self.adg2128.is_connect(*eval(line))
        print(ret)

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_write_register.__doc__)
        print(self.do_read_register.__doc__)
        print(self.do_set_xy_state.__doc__)
        print(self.do_get_xy_state.__doc__)
        print(self.do_connect.__doc__)
        print(self.do_disconnect.__doc__)
        print(self.do_is_connect.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_adg2128_dbg(dev_name, dev_addr):
    adg2128_dbg = ADG2128Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = MIXI2CSG(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)

    adg2128_dbg.adg2128 = ADG2128(dev_addr, i2c_bus)
    return adg2128_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address',
                        help='device address', default='0x70')
    args = parser.parse_args()
    ad5693_dbg = create_adg2128_dbg(args.device, int(args.address, 16))

    ad5693_dbg.cmdloop()
