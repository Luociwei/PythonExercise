# -*- coding: utf-8 -*-
import argparse
import cmd
import os
import traceback
from functools import wraps
from nct75 import NCT75
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


class NCT75Debuger(cmd.Cmd):
    prompt = 'nct75>'
    intro = 'Xavier nct75 debug tool'

    @handle_errors
    def do_read_temp(self, line):
        '''read_temp'''
        result = self.nct75.temperature
        print(result)

    @handle_errors
    def do_work_mode(self, line):
        '''work_mode'''
        result = self.nct75.get_work_mode
        print(result)

    @handle_errors
    def do_set_work_mode(self, line):
        '''set_work_mode'''
        self.nct75.work_mode = eval(line)
        print('Done.')

    @handle_errors
    def config_overtemperature(self, line):
        '''config_overtemperature t_os t_hyst mode polarity'''
        line = line.replace(' ', ',')
        self.nct75.config_overtemperature(*list(eval(line)))
        print('Done.')


def create_nct75_dbg(dev_name, dev_addr):
    nct75_dbg = NCT75Debuger()
    if dev_name == '':
        i2c_bus = None
    else:
        if utility.is_pl_device(dev_name):
            axi4_bus = AXI4LiteBus(dev_name, PLI2CDef.REG_SIZE)
            i2c_bus = PLI2CBus(axi4_bus)
        else:
            i2c_bus = I2C(dev_name)
    nct75_dbg.nct75 = NCT75(dev_addr, i2c_bus)
    return nct75_dbg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--device', help='device file name', default='')
    parser.add_argument('-a', '--address', help='device address', default='0x48')
    args = parser.parse_args()
    nct75_dbg = create_nct75_dbg(args.device, int(args.address, 16))

    nct75_dbg.cmdloop()
