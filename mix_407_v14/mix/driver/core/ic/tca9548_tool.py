# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from tca9548 import TCA9548
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


class TCA9548Debuger(cmd.Cmd):
    prompt = 'tca9548>'
    intro = 'Xavier tca9548 debug tool'

    @handle_errors
    def do_set_channel_state(self, line):
        '''set_channel_state [(channel value,state)]'''
        self.tca9548.set_channel_state(eval(line))
        print('Done')

    @handle_errors
    def do_get_channel_state(self, line):
        '''get_channel_state [channel value]'''
        ret = self.tca9548.get_channel_state(eval(line))
        print(ret)

    @handle_errors
    def do_open_all_channel(self, line):
        '''open_all_channel'''
        self.tca9548.open_all_channel()
        print('Done')

    @handle_errors
    def do_close_all_channel(self, line):
        '''close_all_channel'''
        self.tca9548.close_all_channel()
        print('Done')

    @handle_errors
    def do_quit(self, line):
        '''quit'''
        return True

    @handle_errors
    def do_help(self, line):
        '''help'''
        print('Usage:')
        print(self.do_set_channel_state.__doc__)
        print(self.do_get_channel_state.__doc__)
        print(self.do_open_all_channel.__doc__)
        print(self.do_close_all_channel.__doc__)
        print(self.do_quit.__doc__)
        print(self.do_help.__doc__)


def create_tca9548_dbg(dev_name, dev_addr):
    tca9548_dbg = TCA9548Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = PLI2CBus(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    tca9548_dbg.tca9548 = TCA9548(dev_addr, i2c_bus)
    return tca9548_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x70')
    args = parser.parse_args()
    tca9548_dbg = create_tca9548_dbg(args.device, int(args.address, 16))

    tca9548_dbg.cmdloop()
